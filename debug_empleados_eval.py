#!/usr/bin/env python
"""
Debug script para verificar empleados con evaluaciones
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.append('.')
sys.path.append('./config')
sys.path.append('./apps')

django.setup()

from apps.employees.models import Empleado
from apps.evaluations.models import AsignacionEvaluacion

def debug_empleados():
    print("=== DEBUG EMPLEADOS CON EVALUACIONES ===")
    
    # Total de empleados
    total_empleados = Empleado.objects.count()
    print(f"Total empleados en BD: {total_empleados}")
    
    # Total de evaluaciones
    total_evaluaciones = AsignacionEvaluacion.objects.count()
    print(f"Total evaluaciones en BD: {total_evaluaciones}")
    
    # Empleados con evaluaciones (método actual problemático)
    empleados_con_eval_v1 = Empleado.objects.filter(
        evaluaciones_recibidas__isnull=False
    ).distinct()
    print(f"Empleados con eval (isnull=False): {empleados_con_eval_v1.count()}")
    
    # Método alternativo
    empleados_con_eval_v2 = Empleado.objects.filter(
        id__in=AsignacionEvaluacion.objects.values_list('empleado_evaluado_id', flat=True)
    ).distinct()
    print(f"Empleados con eval (método alternativo): {empleados_con_eval_v2.count()}")
    
    # Mostrar primeros 5 empleados con evaluaciones
    print("\nPrimeros empleados con evaluaciones:")
    for emp in empleados_con_eval_v2[:5]:
        evaluaciones_count = emp.evaluaciones_recibidas.count()
        print(f"- {emp.apellidos}, {emp.nombres} ({evaluaciones_count} evaluaciones)")
    
    # Verificar estados de evaluaciones
    print("\nEstados de evaluaciones:")
    estados = AsignacionEvaluacion.objects.values('estado').annotate(
        count=django.db.models.Count('id')
    ).order_by('estado')
    
    for estado in estados:
        print(f"- {estado['estado']}: {estado['count']}")

if __name__ == '__main__':
    debug_empleados()