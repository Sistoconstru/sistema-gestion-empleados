"""Avisa de las licencias de conducción vencidas o por vencer.

Existe aparte del aviso general de documentos por una razón concreta: ese
solo mira los documentos **aprobados**, y en la flota hay licencias que el
empleado subió y que Talento Humano nunca revisó. Para esas, el aviso
general no existe, y el conductor sigue manejando sin que nadie lo sepa.

Va al conductor y a quienes lo administran —su jefe directo y el jefe de
este—, porque el conductor es quien tiene que renovarla y el jefe es quien
decide si lo deja salir mientras tanto.

Antes del vencimiento se avisa en hitos: 30, 15, 7, 3 y 1 día antes, y el
día mismo. Después, mientras siga sin resolverse, cada uno recibe a su
ritmo, porque tienen tareas distintas:

- El conductor, día por medio hasta que la actualice.
- El jefe y el director, una vez por semana. No son ellos los que van al
  tránsito; necesitan saberlo, no que se lo repitan cada mañana.
"""
from datetime import date

from django.core.management.base import BaseCommand

from apps.transporte import licencias
from apps.transporte.permisos import conductores_vigentes

import logging

logger = logging.getLogger(__name__)

HITOS_AVISO = (30, 15, 7, 3, 1, 0)


class Command(BaseCommand):
    help = ('Notifica a los conductores y a sus jefes las licencias de '
            'conducción vencidas o próximas a vencer.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Muestra a quién se avisaría sin enviar nada')
        parser.add_argument(
            '--todos', action='store_true',
            help='Avisa de todo, ignorando los hitos')

    def _tags(self, empleado, estado, hoy):
        """Las etiquetas de "ya se avisó", una por cadencia.

        La cadencia se decide con la etiqueta y no con un `if` sobre el día:
        el comando corre todos los días y la etiqueta solo cambia cuando
        toca avisar de nuevo. Así un día con el servidor caído no pierde el
        aviso, solo lo corre al siguiente.

        - Al conductor, día por medio: es quien tiene que ir a renovar.
        - Al jefe y al director, una vez por semana calendario, así que les
          llega el lunes o el primer día que el comando alcance a correr.

        Antes del vencimiento son hitos exactos y la etiqueta es la misma
        para todos: ahí no hay insistencia que valga, es una fecha concreta.
        """
        base = f'lic-{empleado.pk}-{estado["clave"]}'
        dias = estado['dias']
        if dias is not None and dias >= 0:
            return f'{base}-{dias}', f'{base}-{dias}'

        anio, semana, _ = hoy.isocalendar()
        return (f'{base}-d{hoy.toordinal() // 2}',
                f'{base}-s{anio}-{semana:02d}')

    def _ya_se_aviso(self, destino, tag):
        from apps.notifications.models import Notificacion

        return Notificacion.objects.filter(
            usuario=destino.usuario,
            datos_adicionales__contains={'aviso_tag': tag},
        ).exists()

    def _toca_avisar(self, estado, todos):
        """¿Este estado amerita aviso hoy? El cuándo lo decide la etiqueta."""
        if todos:
            return True
        clave, dias = estado['clave'], estado['dias']
        if clave == 'vigente':
            return False
        if clave in ('sin_licencia', 'sin_fecha') or dias is None:
            return True
        if dias < 0:
            return True
        return dias in HITOS_AVISO

    def handle(self, **options):
        dry_run = options['dry_run']
        todos = options['todos']
        hoy = date.today()

        conductores = list(conductores_vigentes().order_by('apellidos', 'nombres'))
        estados = licencias.estados_de(conductores, hoy)

        self.stdout.write(f'Conductores vigentes: {len(conductores)}')
        pendientes = []
        for empleado in conductores:
            estado = estados[empleado.pk]
            if estado['clave'] == 'vigente' and estado['aprobada']:
                continue
            marca = '' if estado['al_dia'] else '  ⚠'
            aprobada = '' if estado['aprobada'] else ' (sin aprobar)'
            self.stdout.write(
                f'  {empleado.nombre_completo:<34} {estado["texto"]}{aprobada}{marca}')
            if self._toca_avisar(estado, todos):
                pendientes.append((empleado, estado))

        if not pendientes:
            self.stdout.write(self.style.SUCCESS('\nNada que avisar hoy.'))
            return

        self.stdout.write(f'\nLicencias que ameritan aviso: {len(pendientes)}')
        enviadas = 0
        for empleado, estado in pendientes:
            titulo, cuerpo = self._mensaje(empleado, estado)
            tag_conductor, tag_jefes = self._tags(empleado, estado, hoy)
            self.stdout.write(f'  {titulo}')

            for destino in self._destinatarios(empleado):
                es_el_conductor = destino.pk == empleado.pk
                tag = tag_conductor if es_el_conductor else tag_jefes
                cadencia = 'día por medio' if es_el_conductor else 'semanal'
                if not todos and self._ya_se_aviso(destino, tag):
                    self.stdout.write(
                        f'      · {destino.nombre_completo} — ya avisado '
                        f'({cadencia})')
                    continue
                self.stdout.write(
                    f'      → {destino.nombre_completo} ({cadencia})')
                if dry_run:
                    continue
                if self._notificar(destino, empleado, titulo, cuerpo, estado, tag):
                    enviadas += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'\nDRY RUN: se avisaría de {len(pendientes)} licencia(s). '
                f'No se envió nada.'))
            return

        logger.info('Enviadas %s notificaciones de licencias de conducción.', enviadas)
        self.stdout.write(self.style.SUCCESS(
            f'\nNotificaciones enviadas: {enviadas}'))

    def _mensaje(self, empleado, estado):
        nombre = empleado.nombre_completo
        if estado['clave'] == 'sin_licencia':
            return (f'Sin licencia de conducción — {nombre}',
                    f'{nombre} conduce vehículos de la flota y no tiene la '
                    f'licencia de conducción cargada en SIGHU.')
        if estado['clave'] == 'sin_fecha':
            return (f'Licencia sin fecha de vencimiento — {nombre}',
                    f'La licencia de {nombre} está cargada pero sin fecha de '
                    f'vencimiento, así que no se puede verificar que esté '
                    f'vigente. Talento Humano tiene que completarla.')
        vence = estado['documento'].fecha_vencimiento
        dias = estado['dias']
        if dias < 0:
            return (f'Licencia vencida — {nombre}',
                    f'La licencia de conducción de {nombre} venció hace '
                    f'{abs(dias)} días ({vence:%d/%m/%Y}). No debería conducir '
                    f'hasta renovarla.')
        if dias == 0:
            return (f'Licencia vence hoy — {nombre}',
                    f'La licencia de conducción de {nombre} vence hoy.')
        return (f'Licencia vence en {dias} días — {nombre}',
                f'La licencia de conducción de {nombre} vence el '
                f'{vence:%d/%m/%Y}.')

    def _destinatarios(self, empleado):
        """El conductor, su jefe y el jefe de este."""
        destinatarios = []
        if empleado.usuario_id:
            destinatarios.append(empleado)
        jefe = empleado.jefe_inmediato
        if jefe and jefe.usuario_id:
            destinatarios.append(jefe)
            director = jefe.jefe_inmediato
            if director and director.usuario_id:
                destinatarios.append(director)

        vistos, unicos = set(), []
        for e in destinatarios:
            if e.pk not in vistos:
                vistos.add(e.pk)
                unicos.append(e)
        return unicos

    def _notificar(self, destino, conductor, titulo, cuerpo, estado, tag):
        try:
            from apps.notifications.models import Notificacion, TipoNotificacion
            tipo, _ = TipoNotificacion.objects.get_or_create(
                codigo='licencia_conduccion',
                defaults={
                    'nombre': 'Licencia de conducción por vencer',
                    'plantilla_titulo': '{titulo}',
                    'plantilla_mensaje': '{mensaje}',
                    'enviar_push': True,
                },
            )
            Notificacion.objects.create(
                usuario=destino.usuario,
                tipo_notificacion=tipo,
                titulo=titulo[:200],
                mensaje=cuerpo,
                datos_adicionales={
                    'aviso_tag': tag,
                    'conductor_id': str(conductor.pk),
                    'estado_licencia': estado['clave'],
                    'fecha_vencimiento': (
                        str(estado['documento'].fecha_vencimiento)
                        if estado['documento'] and estado['documento'].fecha_vencimiento
                        else None),
                },
            )
            try:
                from apps.notifications.push_utils import send_push
                send_push(destino.usuario, titulo, cuerpo,
                          url=f'/documentos/empleado/{conductor.pk}/',
                          tag=tag, tag_group='licencias')
            except Exception as e:
                logger.warning('Push de licencia no enviado a %s: %s', destino.pk, e)
            return True
        except Exception as e:
            logger.error('No se pudo notificar la licencia a %s: %s', destino.pk, e)
            self.stdout.write(self.style.ERROR(
                f'      error al notificar a {destino.nombre_completo}: {e}'))
            return False
