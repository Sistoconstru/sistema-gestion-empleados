#!/usr/bin/env python
"""
Test directo de la vista cambiar_cargo_empleado
"""

import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.employees.models import Empleado, HistorialCargo
from apps.organizational.models import Cargo, Sede
from apps.employees.views import cambiar_cargo_empleado

def test_vista_cambio_cargo():
    """Test directo de la vista de cambio de cargo"""
    
    print("🧪 Probando vista cambiar_cargo_empleado...")
    
    # Obtener un empleado con cargo
    empleado = Empleado.objects.filter(
        historialcargo__activa=True
    ).first()
    
    if not empleado:
        print("❌ No hay empleados con cargo activo para probar")
        return
        
    print(f"👤 Empleado seleccionado: {empleado.nombre_completo}")
    
    # Obtener cargo actual
    cargo_actual = empleado.historialcargo_set.filter(activa=True).first()
    print(f"💼 Cargo actual: {cargo_actual.cargo.nombre}")
    
    # Obtener un cargo diferente
    nuevo_cargo = Cargo.objects.filter(
        activo=True
    ).exclude(id=cargo_actual.cargo.id).first()
    
    if not nuevo_cargo:
        print("❌ No hay otros cargos disponibles")
        return
        
    print(f"🔄 Nuevo cargo: {nuevo_cargo.nombre}")
    
    # Obtener una sede
    nueva_sede = Sede.objects.filter(activa=True).first()
    print(f"🏢 Nueva sede: {nueva_sede.nombre}")
    
    # Crear usuario admin para el test
    User = get_user_model()
    admin_user = User.objects.filter(is_staff=True).first()
    
    if not admin_user:
        print("❌ No hay usuarios administradores")
        return
        
    print(f"👨‍💼 Usuario admin: {admin_user.username}")
    
    # Crear request factory
    factory = RequestFactory()
    
    # Crear request POST
    request = factory.post(f'/empleados/{empleado.id}/cambiar-cargo/', {
        'nuevo_cargo': str(nuevo_cargo.id),
        'nueva_sede': str(nueva_sede.id),
        'fecha_inicio': '2025-11-07',
        'motivo': 'Test automatizado de cambio de cargo'
    })
    
    # Asignar usuario al request
    request.user = admin_user
    
    try:
        # Llamar a la vista
        response = cambiar_cargo_empleado(request, empleado.id)
        
        print(f"📊 Response status: {response.status_code}")
        
        # Si es JsonResponse, obtener el contenido
        if hasattr(response, 'content'):
            import json
            content = json.loads(response.content.decode())
            print(f"📝 Response content: {content}")
            
            if content.get('success'):
                print("✅ Cambio de cargo exitoso!")
                
                # Verificar en la base de datos
                empleado.refresh_from_db()
                nuevo_cargo_actual = empleado.historialcargo_set.filter(activa=True).first()
                print(f"✨ Nuevo cargo en BD: {nuevo_cargo_actual.cargo.nombre}")
                
            else:
                print(f"❌ Error en cambio: {content.get('message')}")
        
    except Exception as e:
        print(f"❌ Error ejecutando vista: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vista_cambio_cargo()