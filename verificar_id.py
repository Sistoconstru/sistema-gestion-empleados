#!/usr/bin/env python
"""
Script para verificar ID de evaluación de James Arias
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.evaluations.models import AsignacionEvaluacion
from apps.employees.models import Empleado

def verificar_id_james():
    """Verificar ID correcto de James Arias"""
    
    print("=== VERIFICAR ID EVALUACIÓN JAMES ===\n")
    
    # Buscar James Arias
    james = Empleado.objects.filter(nombres__icontains="James", apellidos__icontains="Arias").first()
    if not james:
        print("No se encontró James Arias")
        return
    
    print(f"Empleado: {james.nombre_completo}")
    
    # Obtener su evaluación
    evaluacion = AsignacionEvaluacion.objects.filter(empleado_evaluado=james).first()
    if not evaluacion:
        print("No se encontró evaluación")
        return
    
    print(f"ID de evaluación: {evaluacion.id}")
    print(f"Estado: {evaluacion.estado}")
    print(f"Observaciones: '{evaluacion.observaciones}'")
    
    # Verificar usuario asociado
    print(f"Usuario de James: {james.usuario if hasattr(james, 'usuario') and james.usuario else 'NO TIENE USUARIO'}")
    
    # Verificar si tiene resultado
    if hasattr(evaluacion, 'resultadoevaluacion'):
        print("✅ Tiene resultado asociado")
        resultado = evaluacion.resultadoevaluacion
        print(f"Puntaje: {resultado.puntaje_final}")
    else:
        print("❌ No tiene resultado asociado")
    
    # Generar URL correcta
    url_correcta = f"/evaluations/ver-resultados/{evaluacion.id}/"
    print(f"\nURL correcta: {url_correcta}")
    
    # URL del error reportado
    url_error = "http://127.0.0.1:8000/evaluations/ver-resultados/3767fc14-8805-4023-bedd-fa90ccad0ee3/"
    print(f"URL del error: {url_error}")
    
    id_error = "3767fc14-8805-4023-bedd-fa90ccad0ee3"
    print(f"\n¿El ID del error coincide? {str(evaluacion.id) == id_error}")

if __name__ == "__main__":
    verificar_id_james()