#!/usr/bin/env python
"""
Script para probar manualmente el cambio de cargo
"""

import requests
import json

# URL del empleado con cargo actual (Ana Maria Marin)
empleado_id = "cd36dbaa-8c6c-48d2-a29d-f55a85533ba8"  # De los logs del servidor
base_url = "http://127.0.0.1:8000"

# URL para el cambio de cargo
cambiar_cargo_url = f"{base_url}/empleados/{empleado_id}/cambiar-cargo/"

print(f"🔗 URL a probar: {cambiar_cargo_url}")

# Datos de prueba
data = {
    'nuevo_cargo': '1',  # ID de cargo existente
    'nueva_sede': '1',   # ID de sede existente  
    'fecha_inicio': '2025-11-07',
    'motivo': 'Prueba de cambio de cargo'
}

print(f"📝 Datos a enviar: {data}")

try:
    # Primero hacer GET para obtener la página y el token CSRF
    response_get = requests.get(f"{base_url}/empleados/{empleado_id}/")
    print(f"📄 GET Response: {response_get.status_code}")
    
    if "csrfmiddlewaretoken" in response_get.text:
        print("✅ Token CSRF encontrado en la página")
    else:
        print("❌ Token CSRF no encontrado")
        
    # Intentar POST sin autenticación (debería fallar)
    response_post = requests.post(cambiar_cargo_url, data=data)
    print(f"📤 POST Response: {response_post.status_code}")
    print(f"📋 Response text: {response_post.text[:200]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n💡 Nota: Este test fallará porque requiere autenticación y CSRF token")
print("   Use el navegador para probar la funcionalidad completa.")