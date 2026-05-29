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

        # Tarea 6: Resultados de partidos cada 5 min, las 24 horas.
        # El comando filtra solo partidos en su ventana de finalización, así que si
        # no hay partidos terminando hace 0 requests a la API. Latencia ~5 min tras
        # el pitazo final con consumo mínimo. Reemplaza el workflow de GitHub Actions
        # que fallaba (railway run ejecutaba Django en un runner sin dependencias).
        scheduler.add_job(
            _actualizar_resultados_mundial,
            'cron',
            minute='*/5',
            id='actualizar_resultados_mundial',
            name='Actualizar resultados Polla Mundial',
            replace_existing=True,
            misfire_grace_time=120,
            coalesce=True,
        )

        # Tarea 7: Fixture y equipos TBD una vez al día (5:30 AM hora Colombia).
        # importar_partidos_mundial hace 1 request por corrida SIEMPRE, y
        # actualizar_equipos_tbd hace 1 request por cada partido con equipo TBD.
        # Correrlos cada 5 min reventaría el plan de la API (límite 3000/mes), así
        # que van en un job diario: el fixture es estable y los equipos de
        # eliminación se definen al terminar cada ronda (no minuto a minuto).
        scheduler.add_job(
            _actualizar_fixture_mundial,
            'cron',
            hour=5,
            minute=30,
            id='actualizar_fixture_mundial',
            name='Actualizar fixture y equipos TBD Polla Mundial',
            replace_existing=True,
            misfire_grace_time=3600,
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
        logger.info('  - Cada 5 min (24h): Resultados Polla Mundial (solo partidos en ventana de finalización)')
        logger.info('  - 05:30 AM: Fixture y equipos TBD Polla Mundial (1 vez al día, ahorro de API)')

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
