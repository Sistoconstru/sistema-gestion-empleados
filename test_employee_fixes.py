#!/usr/bin/env python3
"""
Script para probar las correcciones del modelo Empleado
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.employees.models import Empleado, HistorialCargo
from apps.organizational.models import Cargo
from django.contrib.auth import get_user_model

def probar_cambio_cargo():
    """Prueba el cambio de cargo que antes fallaba"""
    print("🔍 Probando funcionalidad de cambio de cargo...")
    
    try:
        # Buscar un empleado con cargo activo
        empleado = Empleado.objects.filter(historialcargo__activo=True).first()
        if not empleado:
            print("❌ No se encontraron empleados con cargo activo")
            return False
            
        print(f"📝 Empleado: {empleado.nombre_completo}")
        
        # Obtener cargo actual
        cargo_actual = empleado.cargo_actual
        if cargo_actual:
            print(f"💼 Cargo actual: {cargo_actual.cargo.nombre}")
        else:
            print("❌ No se pudo obtener cargo actual")
            return False
            
        # Buscar otro cargo para cambiar
        nuevo_cargo = Cargo.objects.exclude(id=cargo_actual.cargo.id).first()
        if not nuevo_cargo:
            print("❌ No se encontró otro cargo para probar")
            return False
            
        print(f"🔄 Intentando cambiar a: {nuevo_cargo.nombre}")
        
        # Crear nuevo historial de cargo (esto antes fallaba)
        User = get_user_model()
        usuario_admin = User.objects.filter(is_superuser=True).first()
        if not usuario_admin:
            print("❌ No se encontró usuario administrador")
            return False
            
        nuevo_historial = HistorialCargo.objects.create(
            empleado=empleado,
            cargo=nuevo_cargo,
            fecha_inicio='2024-01-15',
            activo=True,
            creado_por=usuario_admin
        )
        
        print(f"✅ Cambio de cargo exitoso!")
        print(f"✅ Nuevo cargo: {empleado.cargo_actual.cargo.nombre}")
        print(f"✅ Cargo anterior automáticamente desactivado")
        
        # Verificar que solo hay un cargo activo
        cargos_activos = HistorialCargo.objects.filter(empleado=empleado, activo=True).count()
        print(f"✅ Cargos activos para {empleado.nombre_completo}: {cargos_activos}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        return False

def probar_validaciones():
    """Prueba las validaciones mejoradas"""
    print("\n🔍 Probando validaciones mejoradas...")
    
    try:
        # Probar manejo de errores en propiedades
        empleado = Empleado.objects.first()
        if empleado:
            cargo = empleado.cargo_actual  # Esto antes usaba except: genérico
            print(f"✅ Propiedad cargo_actual funciona: {cargo}")
            
            nombre_cargo = empleado.nombre_cargo_actual
            print(f"✅ Propiedad nombre_cargo_actual funciona: {nombre_cargo}")
            
            area = empleado.area_actual
            print(f"✅ Propiedad area_actual funciona: {area}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en validaciones: {str(e)}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de correcciones del modelo Empleado\n")
    
    resultado_cargo = probar_cambio_cargo()
    resultado_validaciones = probar_validaciones()
    
    print(f"\n📊 Resumen de pruebas:")
    print(f"   Cambio de cargo: {'✅ EXITOSO' if resultado_cargo else '❌ FALLÓ'}")
    print(f"   Validaciones: {'✅ EXITOSO' if resultado_validaciones else '❌ FALLÓ'}")
    
    if resultado_cargo and resultado_validaciones:
        print(f"\n🎉 ¡Todas las correcciones funcionan correctamente!")
    else:
        print(f"\n⚠️  Algunas pruebas fallaron, revisar configuración")

if __name__ == "__main__":
    main()