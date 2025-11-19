#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.evaluations.models import AsignacionEvaluacion, ResultadoEvaluacion, RespuestaEvaluacion
from apps.evaluations.views import _calcular_resultado_evaluacion

def debug_evaluacion():
    try:
        # Buscar la evaluación específica
        asignacion_id = '3bbe2994-7087-4d2e-b04d-a352bfb76e0c'
        asignacion = AsignacionEvaluacion.objects.get(pk=asignacion_id)
        
        print(f'🔍 DEBUGGING EVALUACIÓN: {asignacion_id}')
        print(f'📊 Estado actual:')
        print(f'   - puntaje_total: {asignacion.puntaje_total}')
        print(f'   - porcentaje_completado: {asignacion.porcentaje_completado}')
        print(f'   - estado: {asignacion.estado}')
        
        # Obtener respuestas
        respuestas = RespuestaEvaluacion.objects.filter(asignacion=asignacion)
        print(f'\n📝 RESPUESTAS ({respuestas.count()}):')
        total_puntos = 0
        for respuesta in respuestas:
            if respuesta.opcion_seleccionada:
                valor = respuesta.opcion_seleccionada.valor_numerico
                total_puntos += valor
                print(f'   - Pregunta {respuesta.pregunta.orden}: {valor} puntos')
        
        print(f'\n📈 CÁLCULO MANUAL:')
        print(f'   - Total calculado manualmente: {total_puntos} puntos')
        print(f'   - Porcentaje: {(total_puntos/21)*100:.1f}%')
        
        # Verificar resultado
        try:
            resultado = ResultadoEvaluacion.objects.get(asignacion=asignacion)
            print(f'\n🎯 RESULTADO ALMACENADO:')
            print(f'   - puntaje_final: {resultado.puntaje_final}')
            print(f'   - porcentaje_obtenido: {resultado.porcentaje_obtenido}')
            print(f'   - nivel_desempeño: {resultado.nivel_desempeño}')
        except ResultadoEvaluacion.DoesNotExist:
            print(f'\n❌ No hay ResultadoEvaluacion')
        
        # Recalcular
        print(f'\n🔄 RECALCULANDO...')
        _calcular_resultado_evaluacion(asignacion)
        
        # Recargar desde BD
        asignacion.refresh_from_db()
        print(f'\n✅ DESPUÉS DE RECALCULAR:')
        print(f'   - puntaje_total: {asignacion.puntaje_total}')
        print(f'   - porcentaje_completado: {asignacion.porcentaje_completado}')
        
        # Verificar resultado actualizado
        try:
            resultado = ResultadoEvaluacion.objects.get(asignacion=asignacion)
            print(f'\n🎯 RESULTADO ACTUALIZADO:')
            print(f'   - puntaje_final: {resultado.puntaje_final}')
            print(f'   - porcentaje_obtenido: {resultado.porcentaje_obtenido}')
        except ResultadoEvaluacion.DoesNotExist:
            print(f'\n❌ Aún no hay ResultadoEvaluacion')
        
    except AsignacionEvaluacion.DoesNotExist:
        print(f'❌ Evaluación no encontrada: {asignacion_id}')
    except Exception as e:
        print(f'💥 Error: {e}')

if __name__ == "__main__":
    debug_evaluacion()