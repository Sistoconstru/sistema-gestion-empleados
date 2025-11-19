#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from apps.evaluations.models import EvaluacionDesempeño, PreguntaEvaluacion, OpcionEvaluacion

def verificar_evaluacion():
    try:
        eval = EvaluacionDesempeño.objects.get(codigo='EVAL_PERIODO_PRUEBA_2024')
        print(f'✅ Evaluación: {eval.nombre}')
        print(f'📝 Descripción: {eval.descripcion}')
        print(f'📊 Preguntas: {eval.preguntaevaluacion_set.count()}')
        print('\n🔍 PREGUNTAS DETALLADAS:')
        
        for p in eval.preguntaevaluacion_set.all().order_by('orden'):
            print(f'\n{p.orden}. {p.pregunta}')
            print(f'   Categoría: {p.categoria}')
            print(f'   Descripción: {p.descripcion}')
            print(f'   Peso: {p.peso_porcentual}%')
            
            opciones = p.opcionevaluacion_set.all().order_by('orden')
            print(f'   Opciones: {opciones.count()}')
            for opcion in opciones:
                print(f'     - {opcion.opcion} (Valor: {opcion.valor_numerico})')
        
        print(f'\n✅ Evaluación configurada correctamente')
        
        # Verificar puntaje total posible
        total_preguntas = eval.preguntaevaluacion_set.count()
        puntaje_minimo = total_preguntas * 1  # 1 punto por pregunta
        puntaje_maximo = total_preguntas * 3  # 3 puntos por pregunta
        
        print(f'\n📊 CRITERIOS DE EVALUACIÓN:')
        print(f'   Preguntas: {total_preguntas}')
        print(f'   Puntaje mínimo posible: {puntaje_minimo} puntos')
        print(f'   Puntaje máximo posible: {puntaje_maximo} puntos')
        print(f'   Para NO continuar: 1-13 puntos')
        print(f'   Para continuar: 14-{puntaje_maximo} puntos')
        
    except EvaluacionDesempeño.DoesNotExist:
        print('❌ No se encontró la evaluación EVAL_PERIODO_PRUEBA_2024')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    verificar_evaluacion()