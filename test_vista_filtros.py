#!/usr/bin/env python
"""
Test directo de la vista ListadoCompletoEvaluacionesView
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

from django.test import RequestFactory
from apps.evaluations.views import ListadoCompletoEvaluacionesView
from apps.employees.models import Empleado
from apps.evaluations.models import AsignacionEvaluacion
from django.contrib.auth.models import AnonymousUser

def test_vista_filtros():
    print("=== TEST DIRECTO DE VISTA ===")
    
    # Crear factory de requests
    factory = RequestFactory()
    
    # Obtener un empleado para test
    empleado_test = Empleado.objects.filter(
        id__in=AsignacionEvaluacion.objects.values_list('empleado_evaluado_id', flat=True)
    ).first()
    
    if not empleado_test:
        print("No hay empleados con evaluaciones")
        return
    
    print(f"Empleado de prueba: {empleado_test.apellidos}, {empleado_test.nombres} (ID: {empleado_test.id})")
    
    # Test 1: Sin filtros
    request = factory.get('/evaluaciones/listado-completo/')
    view = ListadoCompletoEvaluacionesView()
    view.request = request
    
    queryset = view.get_queryset()
    print(f"Sin filtros: {queryset.count()} evaluaciones")
    
    # Test 2: Con filtro de empleado
    request_with_filter = factory.get(f'/evaluaciones/listado-completo/?empleado={empleado_test.id}')
    view_filtered = ListadoCompletoEvaluacionesView()
    view_filtered.request = request_with_filter
    
    queryset_filtered = view_filtered.get_queryset()
    print(f"Con filtro empleado {empleado_test.apellidos}: {queryset_filtered.count()} evaluaciones")
    
    # Test 3: Verificar qué parámetros llegan
    params = request_with_filter.GET
    print(f"Parámetros recibidos: {dict(params)}")
    
    # Test 4: Manual filter
    manual_filter = AsignacionEvaluacion.objects.filter(empleado_evaluado__id=empleado_test.id)
    print(f"Filtro manual directo: {manual_filter.count()} evaluaciones")
    
    # Test 5: Verificar empleados disponibles
    empleados_disponibles = Empleado.objects.filter(
        id__in=AsignacionEvaluacion.objects.values_list('empleado_evaluado_id', flat=True)
    ).distinct().order_by('apellidos', 'nombres')
    
    print(f"Empleados disponibles: {empleados_disponibles.count()}")
    print("Primeros 5:")
    for emp in empleados_disponibles[:5]:
        evals_count = AsignacionEvaluacion.objects.filter(empleado_evaluado=emp).count()
        print(f"  - {emp.apellidos}, {emp.nombres}: {evals_count} evaluaciones")

if __name__ == '__main__':
    test_vista_filtros()