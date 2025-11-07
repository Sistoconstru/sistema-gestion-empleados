#!/usr/bin/env python3
"""
Script para hacer commit de todos los cambios incluyendo archivos estáticos
"""

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
            if result.stderr.strip():
                print(f"📝 Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Excepción en {description}: {str(e)}")
        return False
    return True

def main():
    """Función principal para hacer commit"""
    print("🚀 Iniciando commit de cambios corporativos...")
    
    # Lista de comandos a ejecutar
    commands = [
        ("python manage.py collectstatic --noinput", "Recopilando archivos estáticos"),
        ("git add .", "Agregando todos los archivos al stage"),
        ("git commit -m 'Fix: Agregar archivos estáticos corporativos para producción\n\n- Remover staticfiles/ del .gitignore\n- Incluir corporativo.css compilado\n- Mejorar grid de tarjetas admin dashboard\n- Agregar scripts de sincronización para producción'", "Creando commit con cambios"),
        ("git push origin mi-rama", "Subiendo cambios al repositorio"),
    ]
    
    # Ejecutar comandos
    for command, description in commands:
        if not run_command(command, description):
            print(f"\n⚠️  Error en: {description}")
            if "commit" in description.lower():
                print("💡 Tip: Puede que no haya cambios para hacer commit")
            continue
    
    print(f"\n🎉 ¡Cambios enviados al repositorio!")
    print(f"\n📋 Próximos pasos en PRODUCCIÓN:")
    print(f"   1. Ejecutar: python update_production.py")
    print(f"   2. O ejecutar: bash sync_production.sh")
    print(f"   3. Verificar dashboard en navegador incógnito")
    print(f"   4. Confirmar colores corporativos aplicados")

if __name__ == "__main__":
    main()