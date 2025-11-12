#!/usr/bin/env python
"""
Script de diagnóstico para revisar estados de empleados en producción
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from apps.employees.models import Empleado, EstadoEmpleado
from django.db.models import Count

def diagnostico_estados():
    print("=== DIAGNÓSTICO DE ESTADOS DE EMPLEADOS ===\n")
    
    # Obtener todos los estados existentes
    print("1. ESTADOS DISPONIBLES EN EL SISTEMA:")
    estados = EstadoEmpleado.objects.all().order_by('codigo')
    for estado in estados:
        print(f"   - Código: '{estado.codigo}' | Nombre: '{estado.nombre}'")
    
    print(f"\n   Total de estados: {estados.count()}\n")
    
    # Obtener distribución de empleados por estado
    print("2. DISTRIBUCIÓN DE EMPLEADOS POR ESTADO:")
    distribucion = Empleado.objects.values(
        'estado__codigo', 
        'estado__nombre'
    ).annotate(
        total=Count('id')
    ).order_by('-total')
    
    total_empleados = Empleado.objects.count()
    print(f"   Total de empleados: {total_empleados}\n")
    
    for item in distribucion:
        codigo = item['estado__codigo']
        nombre = item['estado__nombre']
        total = item['total']
        porcentaje = round((total / total_empleados) * 100, 1) if total_empleados > 0 else 0
        print(f"   - {codigo} ({nombre}): {total} empleados ({porcentaje}%)")
    
    print("\n3. EMPLEADOS SIN ESTADO ASIGNADO:")
    sin_estado = Empleado.objects.filter(estado__isnull=True).count()
    print(f"   - Empleados sin estado: {sin_estado}")
    
    # Buscar códigos específicos que estamos buscando
    print("\n4. VERIFICACIÓN DE CÓDIGOS BUSCADOS:")
    codigos_buscados = ['ACTIVO', 'Activo', '999', 'activo', 'PRUEBA', 'periodo_prueba', 'p-prue', 'prueba']
    
    for codigo in codigos_buscados:
        try:
            estado = EstadoEmpleado.objects.get(codigo=codigo)
            empleados = Empleado.objects.filter(estado=estado).count()
            print(f"   ✓ '{codigo}' encontrado: {empleados} empleados")
        except EstadoEmpleado.DoesNotExist:
            print(f"   ✗ '{codigo}' NO EXISTE")

if __name__ == "__main__":
    diagnostico_estados()