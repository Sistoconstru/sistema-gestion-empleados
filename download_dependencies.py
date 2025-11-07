#!/usr/bin/env python3
"""
Script para descargar dependencias CSS/JS localmente
Soluciona problemas de CDN bloqueados por navegadores
"""

import os
import urllib.request
import subprocess
import sys

def download_file(url, local_path, description):
    """Descarga un archivo desde una URL"""
    try:
        print(f"📥 Descargando {description}...")
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        urllib.request.urlretrieve(url, local_path)
        
        # Verificar que el archivo se descargó correctamente
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            size = os.path.getsize(local_path)
            print(f"✅ {description} descargado ({size} bytes)")
            return True
        else:
            print(f"❌ Error: {description} no se descargó correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error descargando {description}: {str(e)}")
        return False

def main():
    """Función principal para descargar dependencias"""
    print("🚀 Descargando dependencias locales para evitar bloqueo de CDN...")
    
    # URLs y rutas locales
    dependencies = [
        {
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
            "path": "static/css/vendor/bootstrap.min.css",
            "description": "Bootstrap CSS"
        },
        {
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js",
            "path": "static/js/vendor/bootstrap.bundle.min.js", 
            "description": "Bootstrap JS"
        },
        {
            "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
            "path": "static/css/vendor/fontawesome.min.css",
            "description": "Font Awesome CSS"
        },
        {
            "url": "https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.js",
            "path": "static/js/vendor/sweetalert2.min.js",
            "description": "SweetAlert2 JS"
        },
        # Font Awesome Webfonts (en la ruta correcta)
        {
            "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.woff2",
            "path": "static/css/webfonts/fa-solid-900.woff2",
            "description": "Font Awesome Solid WOFF2"
        },
        {
            "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.woff2",
            "path": "static/css/webfonts/fa-regular-400.woff2",
            "description": "Font Awesome Regular WOFF2"
        },
        {
            "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-brands-400.woff2",
            "path": "static/css/webfonts/fa-brands-400.woff2",
            "description": "Font Awesome Brands WOFF2"
        }
    ]
    
    success_count = 0
    
    # Descargar cada dependencia
    for dep in dependencies:
        if download_file(dep["url"], dep["path"], dep["description"]):
            success_count += 1
    
    print(f"\n📊 Resumen: {success_count}/{len(dependencies)} dependencias descargadas")
    
    if success_count == len(dependencies):
        print(f"\n🎉 ¡Todas las dependencias descargadas exitosamente!")
        
        # Recopilar archivos estáticos
        print(f"\n📦 Recopilando archivos estáticos...")
        try:
            subprocess.run(["python", "manage.py", "collectstatic", "--noinput"], check=True)
            print(f"✅ Archivos estáticos recopilados")
        except subprocess.CalledProcessError:
            print(f"⚠️  Error recopilando archivos estáticos (puede ser normal si Django no está configurado)")
        except FileNotFoundError:
            print(f"⚠️  manage.py no encontrado (ejecutar desde la raíz del proyecto)")
        
        print(f"\n📋 Próximos pasos:")
        print(f"   1. Ejecutar 'python manage.py collectstatic --noinput' en producción")
        print(f"   2. Reiniciar el servidor web")
        print(f"   3. Verificar que los estilos se cargan correctamente")
        print(f"   4. Los CDN funcionarán como fallback si las versiones locales fallan")
        
    else:
        print(f"\n⚠️  Algunas dependencias no se pudieron descargar")
        print(f"   - Los CDN seguirán funcionando como respaldo")
        print(f"   - Revisar conexión a internet")

if __name__ == "__main__":
    main()