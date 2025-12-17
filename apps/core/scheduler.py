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

        scheduler.start()

        logger.info('✅ Scheduler iniciado exitosamente')
        logger.info('Tareas programadas:')
        logger.info('  - 02:00 AM: Asignar evaluaciones de período de prueba')
        logger.info('  - 02:15 AM: Activar empleados completados')
        logger.info('  - 03:00 AM (día 1): Limpiar logs de auditoría antiguos')

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
