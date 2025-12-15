"""
Management command para iniciar el scheduler de tareas automáticas.

Uso:
    python manage.py start_scheduler

Este comando inicia el planificador de tareas en segundo plano que
ejecuta automáticamente:
- 02:00 AM: Asignación de evaluaciones de período de prueba
- 02:15 AM: Activación de empleados completados
"""

from django.core.management.base import BaseCommand
from apps.core.scheduler import start_scheduler, get_scheduler_status
import logging
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Inicia el scheduler de tareas automáticas del sistema de evaluaciones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--status',
            action='store_true',
            help='Muestra el estado actual del scheduler sin iniciarlo',
        )
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Mantiene el scheduler ejecutándose como daemon',
        )

    def handle(self, *args, **options):
        if options['status']:
            self._mostrar_status()
        else:
            self._iniciar_scheduler(daemon=options.get('daemon', False))

    def _iniciar_scheduler(self, daemon=False):
        """Inicia el scheduler."""
        self.stdout.write(self.style.WARNING('>> Iniciando scheduler de tareas automaticas...'))

        scheduler = start_scheduler()

        if scheduler and scheduler.running:
            self.stdout.write(
                self.style.SUCCESS('\n[OK] Scheduler iniciado exitosamente')
            )
            self.stdout.write('\n' + '='*60)
            self.stdout.write('TAREAS PROGRAMADAS:')
            self.stdout.write('='*60)
            self.stdout.write('[02:00 AM] Asignar evaluaciones de periodo de prueba')
            self.stdout.write('    - Empleados en estado "p-prue" con 30-60 dias')
            self.stdout.write('    - Verifica que no tengan evaluacion asignada')
            self.stdout.write('    - Asigna a jefe directo con vencimiento de 15 dias')
            self.stdout.write('')
            self.stdout.write('[02:15 AM] Activar empleados completados')
            self.stdout.write('    - Empleados en estado "p-prue" con 60+ dias')
            self.stdout.write('    - Verifica evaluacion completada satisfactoriamente')
            self.stdout.write('    - Cambia estado a ACTIVO')
            self.stdout.write('='*60)
            self.stdout.write('\nEl scheduler se ejecutara en segundo plano')
            self.stdout.write('Consulta los logs en: logs/django.log')

            if daemon:
                self.stdout.write('Modo daemon: El scheduler permanecera ejecutandose...')
                self.stdout.write('='*60)
                logger.info('Scheduler iniciado en modo daemon')

                # Mantener el proceso vivo en modo daemon
                try:
                    while True:
                        time.sleep(60)  # Dormir por 1 minuto
                except KeyboardInterrupt:
                    self.stdout.write('\n\nDeteniendo scheduler...')
                    logger.info('Scheduler detenido por usuario')
            else:
                self.stdout.write('Nota: El scheduler se detiene si Django se reinicia')
                self.stdout.write('='*60)
        else:
            self.stdout.write(
                self.style.ERROR('\n[ERROR] Error al iniciar el scheduler')
            )

    def _mostrar_status(self):
        """Muestra el estado actual del scheduler."""
        status = get_scheduler_status()

        self.stdout.write('\n' + '='*60)
        self.stdout.write('ESTADO DEL SCHEDULER')
        self.stdout.write('='*60)

        if status['running']:
            self.stdout.write(self.style.SUCCESS('[OK] Estado: EJECUTANDOSE'))
        else:
            self.stdout.write(self.style.ERROR('[PARADO] Estado: DETENIDO'))

        if status['next_run_times']:
            self.stdout.write('\nProximas ejecuciones:')
            for job in status['next_run_times']:
                self.stdout.write(f"  - {job['nombre']}")
                self.stdout.write(f"    Proxima ejecucion: {job['siguiente_ejecucion']}")
        else:
            self.stdout.write(self.style.WARNING('\nNo hay tareas programadas'))

        self.stdout.write('='*60 + '\n')
