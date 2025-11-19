#!/usr/bin/env python
"""
Test específico del filtro de empleado
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

def generar_url_test():
    print("=== GENERADOR DE URL DE PRUEBA ===")
    
    # Obtener empleado con evaluaciones
    empleados_con_eval = Empleado.objects.filter(
        id__in=AsignacionEvaluacion.objects.values_list('empleado_evaluado_id', flat=True)
    ).distinct()[:5]
    
    print("URLs de prueba para filtros:")
    print("\n1. FILTRO POR EMPLEADO:")
    
    for i, emp in enumerate(empleados_con_eval, 1):
        eval_count = AsignacionEvaluacion.objects.filter(empleado_evaluado=emp).count()
        print(f"{i}. {emp.apellidos}, {emp.nombres} ({eval_count} evaluaciones)")
        print(f"   URL: http://127.0.0.1:8000/evaluaciones/listado-completo/?empleado={emp.id}")
        print()
    
    print("2. FILTROS COMBINADOS:")
    if empleados_con_eval.exists():
        primer_emp = empleados_con_eval.first()
        print(f"Empleado {primer_emp.apellidos} + Estado pendiente:")
        print(f"   URL: http://127.0.0.1:8000/evaluaciones/listado-completo/?empleado={primer_emp.id}&estado=pendiente")
        print()
    
    print("3. ESTADÍSTICAS:")
    total_evaluaciones = AsignacionEvaluacion.objects.count()
    pendientes = AsignacionEvaluacion.objects.filter(estado='pendiente').count()
    completadas = AsignacionEvaluacion.objects.filter(estado='completada').count()
    
    print(f"Total evaluaciones: {total_evaluaciones}")
    print(f"Pendientes: {pendientes}")
    print(f"Completadas: {completadas}")

if __name__ == '__main__':
    generar_url_test()