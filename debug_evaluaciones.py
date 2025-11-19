#!/usr/bin/env python
"""
Script para debugging de evaluaciones pendientes
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.evaluations.models import AsignacionEvaluacion
from apps.employees.models import Empleado

def debug_evaluaciones():
    """Debug de evaluaciones pendientes"""
    
    print("=== DEBUG EVALUACIONES ===\n")
    
    # Obtener todas las evaluaciones
    evaluaciones = AsignacionEvaluacion.objects.all().select_related(
        'empleado_evaluado', 'evaluacion', 'evaluador'
    )
    
    print(f"Total evaluaciones en sistema: {evaluaciones.count()}")
    
    # Agrupar por estado
    estados = {}
    for eval in evaluaciones:
        estado = eval.estado
        if estado not in estados:
            estados[estado] = []
        estados[estado].append(eval)
    
    print(f"\nEvaluaciones por estado:")
    for estado, evals in estados.items():
        print(f"  {estado}: {len(evals)}")
    
    # Mostrar detalles de evaluaciones pendientes
    print(f"\n=== EVALUACIONES PENDIENTES ===")
    pendientes = evaluaciones.filter(estado__in=['pendiente', 'en_progreso'])
    
    for eval in pendientes:
        print(f"ID: {eval.id}")
        print(f"Empleado: {eval.empleado_evaluado.nombre_completo}")
        print(f"Estado: {eval.estado}")
        print(f"Fecha asignación: {eval.fecha_asignacion}")
        print(f"Fecha vencimiento: {eval.fecha_vencimiento}")
        print(f"Fecha completada: {eval.fecha_completada}")
        print(f"Evaluación: {eval.evaluacion.nombre}")
        print("-" * 50)
    
    # Verificar un empleado específico
    print(f"\n=== VERIFICACIÓN POR EMPLEADO ===")
    empleado_test = Empleado.objects.first()
    if empleado_test:
        print(f"Empleado de prueba: {empleado_test.nombre_completo}")
        
        evals_empleado = evaluaciones.filter(empleado_evaluado=empleado_test)
        print(f"Evaluaciones del empleado: {evals_empleado.count()}")
        
        pendientes_empleado = evals_empleado.filter(estado__in=['pendiente', 'en_progreso'])
        print(f"Pendientes: {pendientes_empleado.count()}")
        
        for eval in pendientes_empleado:
            print(f"  - {eval.evaluacion.nombre} ({eval.estado})")

if __name__ == "__main__":
    debug_evaluaciones()