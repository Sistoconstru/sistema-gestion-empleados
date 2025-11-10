#!/usr/bin/env python
"""
Script para activar automáticamente empleados que han completado su periodo de prueba.
Este script está diseñado para ser ejecutado como tarea programada (cron en Linux/Mac o Task Scheduler en Windows).

Uso:
    python scripts/activar_empleados_automatico.py

Configuración de tareas programadas:
    - Linux/Mac (crontab): 0 6 * * * /path/to/python /path/to/scripts/activar_empleados_automatico.py
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
        logging.FileHandler(os.path.join(PROJECT_ROOT, 'logs', 'activacion_automatica.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal para activar empleados automáticamente"""
    try:
        logger.info("Iniciando proceso de activación automática de empleados")
        logger.info(f"Configuración Django: {os.environ.get('DJANGO_SETTINGS_MODULE', 'No definido')}")
        
        # Ejecutar el comando de management
        call_command('activar_empleados_prueba', verbosity=2)
        
        logger.info("Proceso de activación automática completado exitosamente")
        
    except Exception as e:
        logger.error(f"Error durante la activación automática: {e}")
        raise

if __name__ == '__main__':
    main()