"""
Configuración y gestión del planificador de tareas automáticas usando APScheduler.

Este módulo configura las tareas que se ejecutan automáticamente:
- Asignación de evaluaciones de período de prueba a los 30 días
- Activación de empleados después de completar período de prueba (60+ días)
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from django.utils import timezone

logger = logging.getLogger(__name__)

scheduler = None


def start_scheduler():
    """
    Inicia el planificador de tareas automáticas.

    Las tareas que se ejecutan son:
    - 02:00 AM: Asignar evaluaciones de período de prueba (30-60 días)
    - 02:15 AM: Activar empleados que completaron período de prueba (60+ días)
    """
    global scheduler

    if scheduler is not None and scheduler.running:
        logger.info('Scheduler ya está corriendo')
        return

    try:
        scheduler = BackgroundScheduler()

        # Tarea 1: Asignar evaluaciones de período de prueba a las 2:00 AM
        scheduler.add_job(
            _asignar_evaluaciones_periodo_prueba,
            'cron',
            hour=2,
            minute=0,
            id='asignar_evaluaciones',
            name='Asignar evaluaciones de período de prueba',
            replace_existing=True,
            misfire_grace_time=600,  # 10 minutos de tolerancia
            coalesce=True,  # Si se pierden múltiples ejecuciones, ejecutar solo una
        )

        # Tarea 2: Activar empleados a las 2:15 AM (15 minutos después)
        scheduler.add_job(
            _activar_empleados_prueba,
            'cron',
            hour=2,
            minute=15,
            id='activar_empleados',
            name='Activar empleados de período de prueba',
            replace_existing=True,
            misfire_grace_time=600,
            coalesce=True,
        )

        # Tarea 3: Limpiar logs antiguos el 1ro de cada mes a las 3:00 AM
        scheduler.add_job(
            _limpiar_logs_antiguos,
            'cron',
            day=1,
            hour=3,
            minute=0,
            id='limpiar_logs',
            name='Limpiar logs de auditoría mayores a 2 años',
            replace_existing=True,
            misfire_grace_time=3600,  # 1 hora de tolerancia
            coalesce=True,
        )

        # Tarea 4: Enviar recordatorios de evaluaciones pendientes a las 4:00 AM
        scheduler.add_job(
            _enviar_recordatorios_evaluaciones,
            'cron',
            hour=4,
            minute=0,
            id='recordatorios_evaluaciones',
            name='Enviar recordatorios de evaluaciones pendientes',
            replace_existing=True,
            misfire_grace_time=600,  # 10 minutos de tolerancia
            coalesce=True,
        )

        # Tarea 5: Enviar recordatorios de seguimientos bimensuales a las 4:15 AM
        scheduler.add_job(
            _enviar_recordatorios_seguimientos,
            'cron',
            hour=4,
            minute=15,
            id='recordatorios_seguimientos',
            name='Enviar recordatorios de seguimientos bimensuales',
            replace_existing=True,
            misfire_grace_time=600,  # 10 minutos de tolerancia
            coalesce=True,
        )

        # DESHABILITADO: Polla Mundial (Mundial 2026 terminó). Reactivar en la
        # próxima copa comentando/eliminando este bloque y descomentando los
        # scheduler.add_job de abajo.
        #
        # scheduler.add_job(
        #     _actualizar_resultados_mundial,
        #     'cron', minute='*/5',
        #     id='actualizar_resultados_mundial',
        #     name='Actualizar resultados Polla Mundial',
        #     replace_existing=True, misfire_grace_time=120, coalesce=True,
        # )
        # scheduler.add_job(
        #     _actualizar_fixture_mundial,
        #     'cron', hour=5, minute=30,
        #     id='actualizar_fixture_mundial',
        #     name='Actualizar fixture y equipos TBD Polla Mundial',
        #     replace_existing=True, misfire_grace_time=3600, coalesce=True,
        # )

        # Recordatorio de sesiones de capacitación: cada 10 min chequea
        # sesiones que arrancan en <=24h o <=30min y avisa vía push a los
        # inscritos que no hayan sido notificados aún.
        scheduler.add_job(
            _recordatorios_sesiones_capacitacion,
            'interval',
            minutes=10,
            id='recordatorios_sesiones',
            name='Recordatorios de sesiones de capacitación',
            replace_existing=True,
            misfire_grace_time=300,
            coalesce=True,
        )

        # Recordatorio a jefes de registrar la asistencia del equipo.
        # Corre L-V a las 8:00 (arranque de jornada). Solo dispara push si el
        # jefe no tiene NINGÚN registro de su equipo hoy y hoy es día hábil
        # (excluye festivos oficiales).
        scheduler.add_job(
            _recordar_asistencia_jefes,
            'cron',
            day_of_week='mon-fri', hour=8, minute=0,
            id='recordar_asistencia_jefes',
            name='Recordatorio asistencia a jefes',
            replace_existing=True,
            misfire_grace_time=1800,
            coalesce=True,
        )

        scheduler.start()

        logger.info('✅ Scheduler iniciado exitosamente')
        logger.info('Tareas programadas:')
        logger.info('  - 02:00 AM: Asignar evaluaciones de período de prueba')
        logger.info('  - 02:15 AM: Activar empleados completados')
        logger.info('  - 03:00 AM (día 1): Limpiar logs de auditoría antiguos')
        logger.info('  - 04:00 AM: Enviar recordatorios de evaluaciones pendientes')
        logger.info('  - 04:15 AM: Enviar recordatorios de seguimientos bimensuales')
        logger.info('  - 08:00 (L-V, no festivos): Recordatorio de asistencia a jefes')
        # (Polla Mundial deshabilitada — Mundial 2026 terminado)

        return scheduler

    except Exception as e:
        logger.error(f'❌ Error al iniciar scheduler: {e}', exc_info=True)
        return None


def stop_scheduler():
    """Detiene el planificador de tareas."""
    global scheduler

    if scheduler and scheduler.running:
        try:
            scheduler.shutdown(wait=False)
            logger.info('Scheduler detenido')
        except Exception as e:
            logger.error(f'Error al detener scheduler: {e}')


def _asignar_evaluaciones_periodo_prueba():
    """
    Ejecuta el comando de asignación de evaluaciones de período de prueba.

    Este comando:
    - Busca empleados en estado 'p-prue' con 30-60 días de servicio
    - Verifica que no tengan evaluación ya asignada
    - Asigna la evaluación de período de prueba al jefe directo
    - Establece vencimiento de 15 días
    """
    try:
        logger.info('🔄 Iniciando asignación de evaluaciones de período de prueba...')

        call_command(
            'asignar_evaluaciones_periodo_prueba',
            '--dias-minimos', '30',
            '--dias-maximos', '60'
        )

        logger.info('✅ Asignación de evaluaciones completada')

    except Exception as e:
        logger.error(
            f'❌ Error en asignación de evaluaciones: {e}',
            exc_info=True
        )


def _activar_empleados_prueba():
    """
    Ejecuta el comando de activación de empleados de período de prueba.

    Este comando:
    - Busca empleados en estado 'p-prue' con más de 60 días de servicio
    - Verifica que tengan evaluación de período de prueba completada
    - Valida que el puntaje sea satisfactorio (≥ 14/21 puntos)
    - Cambia el estado a ACTIVO
    """
    try:
        logger.info('🔄 Iniciando activación de empleados de período de prueba...')

        call_command(
            'activar_empleados_prueba',
            '--dias-periodo', '60'
        )

        logger.info('✅ Activación de empleados completada')

    except Exception as e:
        logger.error(
            f'❌ Error en activación de empleados: {e}',
            exc_info=True
        )


def _limpiar_logs_antiguos():
    """
    Ejecuta el comando de limpieza de logs de auditoría antiguos.

    Este comando:
    - Busca logs con más de 730 días (2 años) de antigüedad
    - Elimina los registros antiguos para mantener la BD optimizada
    - Registra estadísticas de la operación
    """
    try:
        logger.info('🔄 Iniciando limpieza de logs de auditoría antiguos...')

        call_command(
            'limpiar_logs_antiguos',
            '--dias', '730'
        )

        logger.info('✅ Limpieza de logs completada')

    except Exception as e:
        logger.error(
            f'❌ Error en limpieza de logs: {e}',
            exc_info=True
        )


def _enviar_recordatorios_evaluaciones():
    """
    Ejecuta el comando de envío de recordatorios de evaluaciones pendientes.

    Este comando:
    - Busca evaluaciones en estado 'pendiente' hace 3+ días sin actividad
    - Verifica la última notificación enviada para evitar spam
    - Envía recordatorios al empleado evaluado y al evaluador (jefe directo)
    - Las notificaciones aparecen en el sistema para revisión
    """
    try:
        logger.info('🔄 Iniciando envío de recordatorios de evaluaciones...')

        call_command(
            'enviar_recordatorios_evaluaciones',
            '--dias', '3'
        )

        logger.info('✅ Recordatorios de evaluaciones enviados')

    except Exception as e:
        logger.error(
            f'❌ Error al enviar recordatorios de evaluaciones: {e}',
            exc_info=True
        )


def _enviar_recordatorios_seguimientos():
    """
    Ejecuta el comando de envío de recordatorios de seguimientos bimensuales.

    Este comando:
    - Busca seguimientos bimensuales pendientes próximos a vencer (5 días antes)
    - Verifica la última notificación enviada para evitar spam
    - Envía recordatorios al supervisor y al empleado evaluado
    - Marca como 'atrasado' los seguimientos que pasaron su fecha límite
    """
    try:
        logger.info('🔄 Iniciando envío de recordatorios de seguimientos bimensuales...')

        call_command(
            'enviar_recordatorios_seguimientos',
            '--dias-anticipacion', '5',
            '--marcar-atrasados'
        )

        logger.info('✅ Recordatorios de seguimientos enviados y seguimientos atrasados actualizados')

    except Exception as e:
        logger.error(
            f'❌ Error al enviar recordatorios de seguimientos: {e}',
            exc_info=True
        )


def _actualizar_resultados_mundial():
    """
    Actualiza resultados de partidos finalizados y recalcula puntos (cada 5 min).

    El comando filtra solo partidos en su ventana de finalización, así que cuando
    no hay partidos terminando no consume API. Es el job de baja latencia: refleja
    el resultado y los puntos de las predicciones a los pocos minutos del pitazo final.

    Corre dentro del servicio Railway, por lo que Django y la red privada están
    disponibles — a diferencia del workflow de GitHub Actions que fallaba en un
    runner externo sin dependencias.
    """
    try:
        logger.info('🔄 Iniciando actualización de resultados Polla Mundial...')
        call_command('actualizar_resultados_mundial', '--verbose')
        logger.info('✅ Resultados Polla Mundial actualizados')
    except Exception as e:
        logger.error(
            f'❌ Error en actualización de resultados Polla Mundial: {e}',
            exc_info=True
        )


def _actualizar_fixture_mundial():
    """
    Actualiza fixture y equipos TBD una vez al día (ahorro de API).

    Estos comandos consumen API en cada corrida (importar siempre hace 1 request;
    equipos TBD hace 1 por cada partido pendiente de definir), por eso van en un
    job diario en vez de cada 5 min:
    1. actualizar_equipos_tbd: resuelve equipos de eliminatorias ya clasificados
    2. importar_partidos_mundial: re-sincroniza el fixture (cambios de calendario)

    Como los equipos de cada ronda se definen al terminar la ronda anterior (con
    días de margen antes de jugarse), una actualización diaria es suficiente.
    """
    try:
        logger.info('🔄 Iniciando actualización de fixture/equipos TBD Polla Mundial...')

        try:
            call_command('actualizar_equipos_tbd')
        except Exception as e:
            logger.warning(f'⚠️ Error actualizando equipos TBD (continuando): {e}')

        try:
            call_command('importar_partidos_mundial', '--season=2026', '--force')
        except Exception as e:
            logger.warning(f'⚠️ Sin nuevos partidos o error importando (continuando): {e}')

        logger.info('✅ Fixture/equipos TBD Polla Mundial actualizado')

    except Exception as e:
        logger.error(
            f'❌ Error en actualización de fixture Polla Mundial: {e}',
            exc_info=True
        )


def get_scheduler_status():
    """
    Obtiene el estado actual del scheduler.

    Returns:
        dict: Información sobre el estado del scheduler y tareas programadas
    """
    global scheduler

    status = {
        'running': scheduler is not None and scheduler.running,
        'next_run_times': []
    }

    if scheduler and scheduler.running:
        for job in scheduler.get_jobs():
            status['next_run_times'].append({
                'nombre': job.name,
                'siguiente_ejecucion': str(job.next_run_time),
            })

    return status


def _recordatorios_sesiones_capacitacion():
    """Envía push a los inscritos cuando su sesión arranca en <=24h y en <=30min.

    Idempotente: marca en `Notificacion.datos_adicionales` qué ventana ya se
    notificó para no duplicar. Corre cada 10 min.
    """
    from datetime import datetime, timedelta, time
    from django.utils import timezone as django_tz
    from apps.training.models import SesionCapacitacion, InscripcionCapacitacion
    from apps.notifications.models import Notificacion
    from apps.notifications.push_utils import send_push

    ahora = datetime.now()
    ventana_24h_desde = ahora + timedelta(hours=23, minutes=45)
    ventana_24h_hasta = ahora + timedelta(hours=24, minutes=15)
    ventana_30m_desde = ahora + timedelta(minutes=20)
    ventana_30m_hasta = ahora + timedelta(minutes=40)

    sesiones = SesionCapacitacion.objects.filter(
        estado__in=('programada', 'en_curso'),
    ).select_related('capacitacion')

    enviadas = 0
    for sesion in sesiones:
        inicio = datetime.combine(sesion.fecha_inicio, sesion.hora_inicio or time.min)
        for tag_kind, desde, hasta, mensaje in (
            ('24h', ventana_24h_desde, ventana_24h_hasta,
             f'Tu sesión "{sesion.capacitacion.nombre}" ({sesion.codigo}) es mañana '
             f'a las {(sesion.hora_inicio.strftime("%H:%M") if sesion.hora_inicio else "primera hora")} en {sesion.lugar}.'),
            ('30m', ventana_30m_desde, ventana_30m_hasta,
             f'Tu sesión "{sesion.capacitacion.nombre}" empieza en menos de 30 min '
             f'en {sesion.lugar}.'),
        ):
            if not (desde <= inicio <= hasta):
                continue
            for insc in InscripcionCapacitacion.objects.filter(
                sesion=sesion,
            ).select_related('empleado__usuario'):
                if insc.empleado is None or insc.empleado.usuario is None:
                    continue
                tag = f'sesion-{sesion.pk}-{tag_kind}'
                # Idempotencia: si ya hay una notif con este tag para este user, saltar
                ya_enviada = Notificacion.objects.filter(
                    usuario=insc.empleado.usuario,
                    datos_adicionales__contains={'push_tag': tag},
                ).exists()
                if ya_enviada:
                    continue
                enviadas_i, _ = send_push(
                    insc.empleado.usuario,
                    'Sesión de capacitación',
                    mensaje,
                    url=f'/capacitaciones/sesiones/{sesion.pk}/',
                    tag=tag,
                    tag_group='sesion-capacitacion',
                    actions=[
                        {'action': 'ver', 'title': 'Ver sesión'},
                    ],
                    action_urls={'ver': f'/capacitaciones/sesiones/{sesion.pk}/'},
                )
                Notificacion.objects.create(
                    usuario=insc.empleado.usuario,
                    titulo='Sesión de capacitación',
                    mensaje=mensaje,
                    datos_adicionales={'push_tag': tag, 'sesion_id': str(sesion.pk)},
                )
                if enviadas_i:
                    enviadas += 1
    if enviadas:
        logger.info(f'Recordatorios sesiones capacitación: {enviadas} push enviadas.')


def _recordar_asistencia_jefes():
    """Envía push a los jefes que hoy no han registrado NINGÚN dato de asistencia
    de su equipo. Solo corre en días hábiles (L-V no festivos). Idempotente
    por día vía tag en Notificacion.datos_adicionales.
    """
    from datetime import date as _date
    from apps.employees.models import AsistenciaDiaria, Empleado, HistorialCargo
    from apps.employees.utils.dias_habiles import es_festivo_oficial
    from apps.notifications.models import Notificacion, TipoNotificacion
    from apps.notifications.push_utils import send_push

    hoy = _date.today()
    if hoy.weekday() >= 5 or es_festivo_oficial(hoy):
        logger.info('Hoy no es día laboral — no se envía recordatorio a jefes.')
        return

    tipo_notif, _ = TipoNotificacion.objects.get_or_create(
        codigo='recordatorio_asistencia',
        defaults={
            'nombre': 'Recordatorio de asistencia del equipo',
            'descripcion': 'Aviso al jefe cuando no ha registrado la asistencia de su equipo en el día.',
            'plantilla_titulo': 'Falta registrar la asistencia de tu equipo',
            'plantilla_mensaje': 'Aún no has registrado la asistencia hoy.',
            'enviar_email': False,
            'enviar_push': True,
            'activo': True,
        },
    )

    # Jefes activos: empleados que son jefe_directo de al menos un
    # HistorialCargo activo. Reuso el mismo criterio que el reporte RRHH.
    jefes_ids = HistorialCargo.objects.filter(
        activo=True, jefe_directo__isnull=False,
    ).values_list('jefe_directo', flat=True).distinct()
    jefes = Empleado.objects.filter(
        pk__in=list(jefes_ids),
        usuario__isnull=False, usuario__is_active=True,
    ).select_related('usuario')

    enviadas = 0
    saltados_ya_notificados = 0
    saltados_ya_registro = 0
    for jefe in jefes:
        # ¿Su equipo tiene AL MENOS 1 registro hoy?
        tiene_registro = AsistenciaDiaria.objects.filter(
            fecha=hoy,
            empleado__historialcargo__activo=True,
            empleado__historialcargo__jefe_directo=jefe,
        ).exists()
        if tiene_registro:
            saltados_ya_registro += 1
            continue

        # ¿Tiene subordinados activos (elegibles para registro)?
        # Si no tiene equipo elegible hoy, no molestar.
        tiene_equipo = Empleado.objects.filter(
            historialcargo__activo=True,
            historialcargo__jefe_directo=jefe,
            estado__codigo__in=['999', 'p-prue'],
        ).exists()
        if not tiene_equipo:
            continue

        # Idempotencia: no repetir si ya se envió hoy
        tag = f'asistencia-recordatorio-{jefe.pk}-{hoy.isoformat()}'
        ya = Notificacion.objects.filter(
            usuario=jefe.usuario,
            datos_adicionales__contains={'push_tag': tag},
        ).exists()
        if ya:
            saltados_ya_notificados += 1
            continue

        titulo = 'Recuerda registrar la asistencia de tu equipo'
        cuerpo = (
            f'Hoy {hoy:%d/%m/%Y} debes registrar la asistencia de tu equipo. '
            f'Puedes hacerlo desde el módulo de asistencia.'
        )
        enviadas_i, _ = send_push(
            jefe.usuario, titulo, cuerpo,
            url='/empleados/asistencia/',
            tag=tag,
            tag_group='asistencia-recordatorio',
            actions=[{'action': 'ir', 'title': 'Ir a registrar'}],
            action_urls={'ir': '/empleados/asistencia/'},
        )
        Notificacion.objects.create(
            usuario=jefe.usuario,
            tipo_notificacion=tipo_notif,
            titulo=titulo,
            mensaje=cuerpo,
            datos_adicionales={'push_tag': tag, 'jefe_id': str(jefe.pk), 'fecha': hoy.isoformat()},
        )
        if enviadas_i:
            enviadas += 1

    logger.info(
        f'Recordatorio asistencia a jefes: {enviadas} push enviadas · '
        f'{saltados_ya_registro} con registro · {saltados_ya_notificados} ya notificados hoy.'
    )
