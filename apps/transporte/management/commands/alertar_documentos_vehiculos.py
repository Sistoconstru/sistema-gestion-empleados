"""Avisa de los documentos de vehículos vencidos o por vencer.

Va al conductor del vehículo y a quienes lo administran: su jefe directo y
el jefe de este. Un SOAT vencido no es un trámite olvidado, es una multa y
un carro parado, así que el aviso tiene que llegarle a quien conduce y a
quien puede autorizar el gasto.

Para no repetir el mismo aviso cada mañana, solo se notifica en hitos: 30,
15, 7, 3 y 1 día antes, el día del vencimiento, y después una vez por
semana mientras siga vencido.
"""
from datetime import date

from django.core.management.base import BaseCommand

from apps.transporte.models import DocumentoVehiculo, Vehiculo
from apps.transporte.permisos import conductores_a_cargo

import logging

logger = logging.getLogger(__name__)

# Días exactos en los que se avisa antes del vencimiento.
HITOS_AVISO = (30, 15, 7, 3, 1, 0)


class Command(BaseCommand):
    help = ('Notifica los documentos de vehículos vencidos o próximos a '
            'vencer, al conductor y a sus jefes.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Muestra a quién se avisaría sin enviar nada',
        )
        parser.add_argument(
            '--todos', action='store_true',
            help='Avisa de todo lo vencido o por vencer, ignorando los hitos',
        )

    def _toca_avisar(self, dias, todos):
        if todos:
            return True
        if dias in HITOS_AVISO:
            return True
        # Ya vencido: un recordatorio semanal, no uno diario.
        return dias < 0 and abs(dias) % 7 == 0

    def handle(self, **options):
        dry_run = options['dry_run']
        todos = options['todos']
        hoy = date.today()

        avisos = []  # (documento, destinatarios)
        for vehiculo in Vehiculo.objects.filter(activo=True).select_related('conductor'):
            for doc in vehiculo.documentos_vigentes():
                if not doc.aplica or doc.fecha_vencimiento is None:
                    continue
                dias = doc.dias_para_vencer
                if dias > DocumentoVehiculo.DIAS_AVISO:
                    continue
                if not self._toca_avisar(dias, todos):
                    continue

                destinatarios = self._destinatarios(vehiculo)
                if destinatarios:
                    avisos.append((doc, dias, destinatarios))

        self.stdout.write(f'Documentos que requieren aviso hoy ({hoy}): {len(avisos)}\n')
        if not avisos:
            self.stdout.write(self.style.SUCCESS('Nada que avisar.'))
            return

        enviadas = 0
        for doc, dias, destinatarios in avisos:
            if dias < 0:
                titulo = f'{doc.get_tipo_display()} vencido — {doc.vehiculo.placa}'
                cuerpo = (f'El {doc.get_tipo_display().lower()} del vehículo '
                          f'{doc.vehiculo.placa} venció hace {abs(dias)} días '
                          f'({doc.fecha_vencimiento:%d/%m/%Y}).')
            elif dias == 0:
                titulo = f'{doc.get_tipo_display()} vence hoy — {doc.vehiculo.placa}'
                cuerpo = (f'El {doc.get_tipo_display().lower()} del vehículo '
                          f'{doc.vehiculo.placa} vence hoy.')
            else:
                titulo = f'{doc.get_tipo_display()} vence en {dias} días — {doc.vehiculo.placa}'
                cuerpo = (f'El {doc.get_tipo_display().lower()} del vehículo '
                          f'{doc.vehiculo.placa} vence el '
                          f'{doc.fecha_vencimiento:%d/%m/%Y}.')

            nombres = ', '.join(e.nombre_completo for e in destinatarios)
            self.stdout.write(f'  [{doc.vehiculo.placa}] {titulo}')
            self.stdout.write(f'      → {nombres}')

            if dry_run:
                continue

            for empleado in destinatarios:
                if self._notificar(empleado, titulo, cuerpo, doc):
                    enviadas += 1

        if dry_run:
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.WARNING(
                f'DRY RUN: se enviarían avisos de {len(avisos)} documentos. '
                f'No se envió nada.'))
            return

        logger.info('Enviadas %s notificaciones de documentos de vehículos.', enviadas)
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'Notificaciones enviadas: {enviadas}'))

    def _destinatarios(self, vehiculo):
        """Conductor del vehículo y quienes lo administran."""
        from apps.employees.models import Empleado

        destinatarios = []
        if vehiculo.conductor and vehiculo.conductor.usuario_id:
            destinatarios.append(vehiculo.conductor)

        # Jefe directo y jefe del jefe del conductor asignado.
        if vehiculo.conductor:
            jefe = vehiculo.conductor.jefe_inmediato
            if jefe and jefe.usuario_id:
                destinatarios.append(jefe)
                director = jefe.jefe_inmediato
                if director and director.usuario_id:
                    destinatarios.append(director)

        # Sin duplicados, conservando el orden.
        vistos, unicos = set(), []
        for e in destinatarios:
            if e.pk not in vistos:
                vistos.add(e.pk)
                unicos.append(e)
        return unicos

    def _notificar(self, empleado, titulo, cuerpo, doc):
        """Crea la notificación y dispara el push si está disponible."""
        try:
            from apps.notifications.models import Notificacion, TipoNotificacion
            tipo, _ = TipoNotificacion.objects.get_or_create(
                codigo='documento_vehiculo',
                defaults={
                    'nombre': 'Documento de vehículo por vencer',
                    'plantilla_titulo': '{titulo}',
                    'plantilla_mensaje': '{mensaje}',
                    'enviar_push': True,
                },
            )
            Notificacion.objects.create(
                usuario=empleado.usuario,
                tipo_notificacion=tipo,
                titulo=titulo[:200],
                mensaje=cuerpo,
                datos_adicionales={
                    'vehiculo_placa': doc.vehiculo.placa,
                    'documento_tipo': doc.tipo,
                    'fecha_vencimiento': str(doc.fecha_vencimiento),
                },
            )
            try:
                from apps.notifications.push_utils import send_push
                send_push(empleado.usuario, titulo, cuerpo, url='/admin/transporte/vehiculo/')
            except Exception as e:
                # El push es un extra: si falla, la notificación en la campana
                # ya quedó registrada y el aviso no se pierde.
                logger.warning('Push no enviado a %s: %s', empleado.pk, e)
            return True
        except Exception as e:
            logger.error('No se pudo notificar a %s: %s', empleado.pk, e)
            self.stdout.write(self.style.ERROR(
                f'      error al notificar a {empleado.nombre_completo}: {e}'))
            return False
