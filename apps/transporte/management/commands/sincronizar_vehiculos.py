"""Refresca la flota desde Odoo y le avisa las asignaciones pendientes.

Odoo es el dueño del maestro: aquí solo se copia lo necesario para
identificar el vehículo y saber quién lo conduce. Lo que SIGHU aporta
—documentos y vencimientos— no se toca nunca, ni siquiera cuando el
vehículo se da de baja: ese historial es la constancia de que el vehículo
estuvo en regla mientras rodaba.

El cruce es por `odoo_id`, no por placa. Odoo no reutiliza ese id, así que
un vehículo archivado y uno nuevo nunca se confunden.
"""
from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from apps.employees.models import Empleado
from apps.transporte.models import ServicioIniciado, Vehiculo
from apps.transporte.odoo_client import (
    OdooConflictoError, OdooTransporteError, avisar_asignacion,
    avisar_servicio_finalizado, avisar_servicio_iniciado, listar_vehiculos,
)

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Trae los vehículos desde Odoo y reintenta las asignaciones pendientes.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Muestra qué cambiaría sin guardar nada',
        )
        parser.add_argument(
            '--sin-archivados', action='store_true',
            help='No pedir los dados de baja (por defecto sí se piden, para marcarlos)',
        )

    def handle(self, **options):
        dry_run = options['dry_run']
        incluir_archivados = not options['sin_archivados']

        try:
            vehiculos = listar_vehiculos(incluir_archivados=incluir_archivados)
        except OdooTransporteError as e:
            self.stdout.write(self.style.ERROR(f'No se pudo consultar Odoo: {e}'))
            logger.error('Sincronización de vehículos fallida: %s', e)
            return

        self.stdout.write(f'Vehículos que reporta Odoo: {len(vehiculos)}\n')

        creados = actualizados = dados_de_baja = 0
        ahora = timezone.now()

        for v in vehiculos:
            odoo_id = v.get('id') or v.get('vehiculo_id')
            if not odoo_id:
                self.stdout.write(self.style.WARNING(f'  sin id, se omite: {v}'))
                continue

            datos = {
                'placa': v.get('placa') or '',
                'marca': v.get('marca') or '',
                'modelo': v.get('modelo') or '',
                'activo': bool(v.get('activo', True)),
                'fecha_baja': v.get('fecha_baja') or None,
                'fecha_sincronizacion': ahora,
            }
            if v.get('anio') or v.get('año'):
                datos['anio'] = v.get('anio') or v.get('año')

            # El conductor lo decide SIGHU y se le avisa a Odoo, así que no
            # se pisa con lo que Odoo reporte: si difieren, manda el aviso
            # pendiente, no la lectura.
            existente = Vehiculo.objects.filter(odoo_id=odoo_id).first()

            if dry_run:
                accion = 'actualizaría' if existente else 'crearía'
                baja = ' (DE BAJA)' if not datos['activo'] else ''
                self.stdout.write(f'  {accion}: {datos["placa"]}{baja}')
                continue

            vehiculo, creado = Vehiculo.objects.update_or_create(
                odoo_id=odoo_id, defaults=datos)
            if creado:
                creados += 1
                self.stdout.write(f'  nuevo: {vehiculo.placa}')
            else:
                actualizados += 1
            if not datos['activo']:
                dados_de_baja += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'\nDRY RUN sobre {len(vehiculos)} vehículo(s). No se guardó nada.'))
            return

        self.stdout.write(
            f'\nCreados: {creados} | actualizados: {actualizados} '
            f'| dados de baja: {dados_de_baja}')

        self._reintentar_asignaciones()
        self._reintentar_salidas()

    # --- Avisos que quedaron pendientes ---------------------------------

    def _reintentar_asignaciones(self):
        pendientes = Vehiculo.objects.filter(
            asignacion_sincronizada=False, conductor__isnull=False)
        if not pendientes.exists():
            self.stdout.write('Sin asignaciones pendientes de avisar.')
            return

        self.stdout.write(f'\nAsignaciones por avisar a Odoo: {pendientes.count()}')
        avisadas = fallidas = 0
        for vehiculo in pendientes.select_related('conductor'):
            desde = vehiculo.asignacion_desde or timezone.localdate()
            try:
                avisar_asignacion(
                    placa=vehiculo.placa,
                    cedula=vehiculo.conductor.numero_documento,
                    desde=desde,
                )
            except OdooTransporteError as e:
                fallidas += 1
                self.stdout.write(self.style.ERROR(
                    f'  {vehiculo.placa}: {e}'))
                logger.warning('Asignación no avisada (%s): %s', vehiculo.placa, e)
                continue
            Vehiculo.objects.filter(pk=vehiculo.pk).update(
                asignacion_sincronizada=True)
            avisadas += 1
            self.stdout.write(
                f'  avisada: {vehiculo.placa} → {vehiculo.conductor.nombre_completo}')

        self.stdout.write(
            self.style.SUCCESS(f'\nAsignaciones avisadas: {avisadas}')
            if not fallidas else
            self.style.WARNING(
                f'\nAvisadas: {avisadas} | quedan pendientes: {fallidas}'))

    def _reintentar_salidas(self):
        """Salidas y entregas que Odoo todavía no ha recibido.

        Hoy ninguno de los dos endpoints existe del lado de Odoo, así que
        estas quedan pendientes y eso está bien: el dato ya está guardado
        en SIGHU y el día que Odoo los implemente se ponen al día solas.
        """
        # Los que Odoo rechazó con un 409 quedan fuera a propósito: del
        # otro lado cambió algo y repetir el aviso da siempre lo mismo.
        self._reintentar_avisos(
            etiqueta='Salidas',
            pendientes=ServicioIniciado.objects.filter(
                sincronizado=False, conflicto_odoo=False,
                anulado_en__isnull=True,
            ).select_related('vehiculo', 'conductor'),
            avisar=avisar_servicio_iniciado,
            campos_ok={'sincronizado': True},
            campo_error='ultimo_error',
            campo_fecha='fecha_sincronizacion',
            campo_conflicto='conflicto_odoo',
        )
        self._reintentar_avisos(
            etiqueta='Entregas',
            pendientes=ServicioIniciado.objects.filter(
                entrega_sincronizada=False,
                conflicto_odoo_entrega=False,
                entregado_en__isnull=False,
                anulado_en__isnull=True,
            ).select_related('vehiculo', 'conductor'),
            avisar=avisar_servicio_finalizado,
            campos_ok={'entrega_sincronizada': True},
            campo_error='ultimo_error_entrega',
            campo_fecha='fecha_sincronizacion_entrega',
            campo_conflicto='conflicto_odoo_entrega',
        )

        rechazados = ServicioIniciado.objects.filter(
            anulado_en__isnull=True
        ).filter(
            models.Q(conflicto_odoo=True) | models.Q(conflicto_odoo_entrega=True)
        ).count()
        if rechazados:
            self.stdout.write(self.style.WARNING(
                f'\nRechazados por Odoo y no se reintentan: {rechazados}. '
                f'Se revisan en el admin, en Servicios iniciados.'))

    def _reintentar_avisos(self, etiqueta, pendientes, avisar,
                           campos_ok, campo_error, campo_fecha,
                           campo_conflicto):
        if not pendientes.exists():
            self.stdout.write(f'Sin {etiqueta.lower()} pendientes de avisar.')
            return

        self.stdout.write(f'\n{etiqueta} por avisar a Odoo: {pendientes.count()}')
        avisadas = fallidas = rechazadas = 0
        ultimo_error = ''
        for servicio in pendientes:
            try:
                avisar(servicio)
            except OdooConflictoError as e:
                rechazadas += 1
                ServicioIniciado.objects.filter(pk=servicio.pk).update(
                    **{campo_conflicto: True, campo_error: e.motivo[:300]})
                self.stdout.write(self.style.ERROR(
                    f'  rechazada por Odoo ({e.status_code}): '
                    f'{servicio.ref or servicio.odoo_id} '
                    f'({servicio.vehiculo.placa}) — {e.motivo[:120]}'))
                # Un 400 es dato malo de SIGHU: no es operación, es un bug.
                registrar = logger.error if e.es_culpa_nuestra else logger.warning
                registrar('Odoo rechazó %s de %s (%s): %s', etiqueta.lower(),
                          servicio.ref or servicio.odoo_id, e.status_code,
                          e.motivo)
                continue
            except OdooTransporteError as e:
                fallidas += 1
                ultimo_error = str(e)
                ServicioIniciado.objects.filter(pk=servicio.pk).update(
                    **{campo_error: str(e)[:300]})
                continue
            ServicioIniciado.objects.filter(pk=servicio.pk).update(
                **campos_ok,
                **{campo_fecha: timezone.now(), campo_error: '',
                   campo_conflicto: False})
            avisadas += 1
            self.stdout.write(
                f'  avisada: {servicio.ref or servicio.odoo_id} '
                f'({servicio.vehiculo.placa})')

        if fallidas:
            # Un solo renglón y no uno por registro: cuando el endpoint aún
            # no existe todas fallan por lo mismo y repetirlo solo hace ruido.
            self.stdout.write(self.style.WARNING(
                f'\n{etiqueta} avisadas: {avisadas} | quedan pendientes: '
                f'{fallidas} — {ultimo_error[:160]}'))
            logger.info('%s pendientes de avisar a Odoo: %s (%s)',
                        etiqueta, fallidas, ultimo_error[:200])
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\n{etiqueta} avisadas: {avisadas}'))
