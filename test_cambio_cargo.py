#!/usr/bin/env python
"""
Script de prueba para verificar la funcionalidad de cambio de cargo
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.employees.models import Empleado, HistorialCargo
from apps.organizational.models import Cargo, Sede
from django.contrib.auth import get_user_model

def test_cambio_cargo():
    """Probar la funcionalidad de cambio de cargo"""
    
    print("🔍 Probando funcionalidad de cambio de cargo...")
    
    # Verificar que hay empleados
    empleados = Empleado.objects.all()[:5]
    print(f"📊 Total empleados: {empleados.count()}")
    
    for empleado in empleados:
        print(f"\n👤 Empleado: {empleado.nombre_completo}")
        
        # Verificar cargo actual
        cargo_actual = empleado.historialcargo_set.filter(activa=True).first()
        if cargo_actual:
            print(f"   💼 Cargo actual: {cargo_actual.cargo.nombre}")
            print(f"   🏢 Área: {cargo_actual.cargo.area.nombre}")
            print(f"   📅 Desde: {cargo_actual.fecha_inicio}")
            print(f"   💰 Salario: ${cargo_actual.salario or 'No especificado'}")
        else:
            print("   ⚠️  Sin cargo asignado")
        
        # Mostrar historial
        historial = empleado.historialcargo_set.all().order_by('-fecha_inicio')
        print(f"   📋 Historial total: {historial.count()} cargos")
        
    # Verificar cargos disponibles
    cargos_disponibles = Cargo.objects.filter(activo=True)
    print(f"\n🏢 Cargos disponibles: {cargos_disponibles.count()}")
    
    # Verificar sedes disponibles  
    sedes_disponibles = Sede.objects.filter(activa=True)
    print(f"🏘️  Sedes disponibles: {sedes_disponibles.count()}")
    
    print("\n✅ Verificación completada")

if __name__ == "__main__":
    test_cambio_cargo()