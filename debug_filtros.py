#!/usr/bin/env python
"""
Debug script para probar filtros de empleados
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

def test_filtros():
    print("=== TEST DE FILTROS ===")
    
    # Obtener empleados disponibles usando la misma lógica de la vista
    empleados_con_evaluaciones = Empleado.objects.filter(
        id__in=AsignacionEvaluacion.objects.values_list('empleado_evaluado_id', flat=True)
    ).distinct().order_by('apellidos', 'nombres')
    
    print(f"Empleados disponibles para filtro: {empleados_con_evaluaciones.count()}")
    
    # Mostrar algunos empleados
    for emp in empleados_con_evaluaciones[:5]:
        print(f"- ID: {emp.id}, Nombre: {emp.apellidos}, {emp.nombres}")
    
    # Probar filtro por empleado específico
    if empleados_con_evaluaciones.exists():
        primer_empleado = empleados_con_evaluaciones.first()
        print(f"\nProbando filtro con empleado ID: {primer_empleado.id}")
        
        # Simular la misma lógica del queryset de la vista
        queryset_base = AsignacionEvaluacion.objects.select_related(
            'empleado_evaluado',
            'evaluador',
            'evaluacion',
            'evaluacion__tipo_evaluacion'
        ).order_by('-fecha_asignacion')
        
        print(f"Total evaluaciones sin filtro: {queryset_base.count()}")
        
        # Aplicar filtro por empleado
        queryset_filtrado = queryset_base.filter(empleado_evaluado__id=primer_empleado.id)
        print(f"Evaluaciones filtradas por empleado {primer_empleado.apellidos}: {queryset_filtrado.count()}")
        
        # Mostrar evaluaciones del empleado
        for eval in queryset_filtrado:
            print(f"  - Evaluación: {eval.evaluacion.nombre}, Estado: {eval.estado}")
    
    # Probar filtros combinados
    print("\n=== PRUEBA DE FILTROS COMBINADOS ===")
    
    # Filtro por estado
    pendientes = AsignacionEvaluacion.objects.filter(estado='pendiente')
    print(f"Evaluaciones pendientes: {pendientes.count()}")
    
    completadas = AsignacionEvaluacion.objects.filter(estado='completada')
    print(f"Evaluaciones completadas: {completadas.count()}")

if __name__ == '__main__':
    test_filtros()