#!/usr/bin/env python
"""
Test de creación directa de HistorialCargo
"""

import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.employees.models import Empleado, HistorialCargo
from apps.organizational.models import Cargo, Sede
from django.contrib.auth import get_user_model

def test_crear_historial_cargo():
    """Test de creación directa"""
    
    print("🧪 Probando creación directa de HistorialCargo...")
    
    # Obtener datos
    empleado = Empleado.objects.first()
    cargo = Cargo.objects.filter(activo=True).first()
    User = get_user_model()
    user = User.objects.filter(is_staff=True).first()
    
    print(f"👤 Empleado: {empleado.nombre_completo}")
    print(f"💼 Cargo: {cargo.nombre}")
    print(f"👨‍💼 Usuario: {user.username}")
    
    try:
        # Crear historial
        historial = HistorialCargo.objects.create(
            empleado=empleado,
            cargo=cargo,
            fecha_inicio=date.today(),
            activa=True,
            motivo_cambio="Test de creación directa",
            creado_por=user,
            modificado_por=user
        )
        
        print(f"✅ HistorialCargo creado: {historial}")
        print(f"🔄 ID: {historial.id}")
        print(f"📊 Activa: {historial.activa}")
        
        # Intentar acceder a activo (esto debería fallar)
        try:
            activo = historial.activo
            print(f"❌ Error: activo accesible: {activo}")
        except AttributeError as e:
            print(f"✅ Correcto: activo no accesible: {e}")
            
    except Exception as e:
        print(f"❌ Error creando historial: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_crear_historial_cargo()