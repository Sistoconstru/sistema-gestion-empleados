#!/usr/bin/env python3
"""
Script para actualizar archivos estáticos y plantillas en producción
Ejecutar este script en el servidor de producción para sincronizar cambios
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completado exitosamente")
            if result.stdout.strip():
                print(f"📝 Salida: {result.stdout.strip()}")
        else:
            print(f"❌ Error en {description}")
            print(f"📝 Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Excepción en {description}: {str(e)}")
        return False
    return True

def check_css_file():
    """Verifica que el archivo CSS corporativo exista"""
    css_paths = [
        "static/css/corporativo.css",
        "staticfiles/css/corporativo.css"
    ]
    
    print(f"\n🔍 Verificando archivos CSS...")
    for path in css_paths:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {path} encontrado ({size} bytes)")
        else:
            print(f"❌ {path} no encontrado")

def main():
    """Función principal para actualizar producción"""
    print("🚀 Iniciando actualización de producción...")
    
    # Verificar archivos CSS antes
    check_css_file()
    
    # Lista de comandos a ejecutar
    commands = [
        ("git pull origin mi-rama", "Descargando últimos cambios del repositorio"),
        ("python manage.py collectstatic --noinput --clear", "Recopilando archivos estáticos"),
        ("python manage.py migrate", "Aplicando migraciones de base de datos"),
    ]
    
    # Ejecutar comandos
    for command, description in commands:
        if not run_command(command, description):
            print(f"\n⚠️  Error crítico en: {description}")
            print("🛑 Deteniendo actualización")
            sys.exit(1)
    
    # Verificar archivos CSS después
    check_css_file()
    
    print(f"\n🎉 ¡Actualización de producción completada exitosamente!")
    print(f"\n📋 Pasos adicionales recomendados:")
    print(f"   1. Reiniciar el servidor web (Apache/Nginx)")
    print(f"   2. Limpiar caché del navegador (Ctrl+F5 o modo incógnito)")
    print(f"   3. Verificar dashboard: https://tu-dominio.com/recognition/admin/")
    print(f"   4. Comprobar que las tarjetas se muestren con colores corporativos")
    print(f"\n🎨 Colores esperados:")
    print(f"   - Verde corporativo: #1b4d3e")
    print(f"   - Amarillo corporativo: #ffd600")
    print(f"   - Tarjetas con bordes redondeados y efectos hover")

if __name__ == "__main__":
    main()