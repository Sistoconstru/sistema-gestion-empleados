#!/usr/bin/env python
"""
Script para asignar automáticamente evaluaciones de período de prueba a empleados con 30-60 días.
Este script está diseñado para ser ejecutado como tarea programada (cron en Linux/Mac o Task Scheduler en Windows).

Uso:
    python scripts/asignar_evaluaciones_automatico.py

Configuración de tareas programadas:
    - Linux/Mac (crontab): 0 6 * * * /path/to/python /path/to/scripts/asignar_evaluaciones_automatico.py
    - Windows Task Scheduler: Configurar para ejecutar diariamente a las 6:00 AM
"""

import os
import sys
import logging
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

try:
    import django
    django.setup()
except ImportError:
    print("Error: No se pudo importar Django. Asegúrate de que esté instalado y configurado correctamente.")
    sys.exit(1)

from django.core.management import call_command
from django.conf import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(PROJECT_ROOT, 'logs', 'asignacion_automatica.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal para asignar evaluaciones automáticamente"""
    try:
        logger.info("Iniciando proceso de asignación automática de evaluaciones de período de prueba")
        logger.info(f"Configuración Django: {os.environ.get('DJANGO_SETTINGS_MODULE', 'No definido')}")

        # Ejecutar el comando de management
        call_command('asignar_evaluaciones_periodo_prueba', verbosity=2)

        logger.info("Proceso de asignación automática completado exitosamente")

    except Exception as e:
        logger.error(f"Error durante la asignación automática: {e}")
        raise

if __name__ == '__main__':
    main()
