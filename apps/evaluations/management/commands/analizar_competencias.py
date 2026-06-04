"""
Comando para analizar la consistencia de competencias en las evaluaciones.
Verifica que todas las evaluaciones tengan las mismas competencias y detecta inconsistencias.
"""

from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from apps.evaluations.models import (
    AsignacionEvaluacion,
    PreguntaEvaluacion,
    RespuestaEvaluacion
)
from collections import defaultdict


class Command(BaseCommand):
    help = 'Analiza la consistencia de competencias en las evaluaciones'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('ANÁLISIS DE COMPETENCIAS EN EVALUACIONES'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))

        # Competencias esperadas
        competencias_esperadas = [
            'Competencias Organizacionales',
            'Objetivos - El Hacer',
            'Competencias Interpersonales - El Ser',
            'Competencias Técnicas - El Saber'
        ]

        # Función para normalizar categorías
        def normalizar_categoria(categoria_original):
            """Normaliza variantes de nombres de categorías."""
            if not categoria_original:
                return None

            if 'Organizacionales' in categoria_original:
                return 'Competencias Organizacionales'
            elif 'Objetivos' in categoria_original:
                return 'Objetivos - El Hacer'
            elif 'Interpersonales' in categoria_original:
                return 'Competencias Interpersonales - El Ser'
            elif 'Técnicas' in categoria_original or 'Tecnicas' in categoria_original:
                return 'Competencias Técnicas - El Saber'

            return categoria_original  # Devolver original si no coincide

        # 1. Análisis de Preguntas por Categoría
        self.stdout.write(self.style.WARNING('\n1. PREGUNTAS POR CATEGORÍA:'))
        self.stdout.write('-' * 80)

        categorias = PreguntaEvaluacion.objects.values('categoria').annotate(
            total=Count('id')
        ).order_by('categoria')

        categorias_encontradas = {}
        for cat in categorias:
            categoria = cat['categoria']
            total = cat['total']
            categorias_encontradas[categoria] = total

            # Marcar si coincide con las esperadas
            if categoria in competencias_esperadas:
                self.stdout.write(self.style.SUCCESS(f'  [OK] {categoria}: {total} preguntas'))
            else:
                self.stdout.write(self.style.ERROR(f'  [X] {categoria}: {total} preguntas (NO ESPERADA)'))

        # 2. Verificar competencias faltantes
        self.stdout.write(self.style.WARNING('\n2. VERIFICACIÓN DE COMPETENCIAS ESPERADAS:'))
        self.stdout.write('-' * 80)

        for comp in competencias_esperadas:
            if comp in categorias_encontradas:
                self.stdout.write(self.style.SUCCESS(f'  [OK] {comp}: ENCONTRADA'))
            else:
                self.stdout.write(self.style.ERROR(f'  [X] {comp}: NO ENCONTRADA EN PREGUNTAS'))

        # 3. Análisis de Evaluaciones Completadas
        self.stdout.write(self.style.WARNING('\n3. EVALUACIONES COMPLETADAS:'))
        self.stdout.write('-' * 80)

        evaluaciones_completadas = AsignacionEvaluacion.objects.filter(
            estado='completado'
        ).select_related('empleado', 'evaluacion')

        total_evaluaciones = evaluaciones_completadas.count()
        self.stdout.write(f'  Total: {total_evaluaciones} evaluaciones completadas\n')

        # 4. Análisis de Respuestas por Competencia
        self.stdout.write(self.style.WARNING('4. RESPUESTAS POR COMPETENCIA:'))
        self.stdout.write('-' * 80)

        analisis_por_competencia = {}

        for categoria in competencias_esperadas:
            # Obtener todas las evaluaciones que tienen al menos una respuesta en esta categoría
            # IMPORTANTE: Buscar tanto el nombre exacto como las variantes
            evaluaciones_ids = set()
            respuestas_sin_seleccion = 0

            # Obtener todas las respuestas de evaluaciones completadas
            respuestas = RespuestaEvaluacion.objects.filter(
                asignacion__estado='completada',
                asignacion__puntaje_total__isnull=False,
                asignacion__evaluacion__tipo_evaluacion__codigo__startswith='ANUAL_'
            ).select_related('asignacion', 'pregunta', 'opcion_seleccionada')

            for resp in respuestas:
                # Normalizar la categoría de la pregunta
                categoria_normalizada = normalizar_categoria(resp.pregunta.categoria)

                # Solo contar si coincide con la categoría que estamos analizando
                if categoria_normalizada == categoria:
                    if resp.opcion_seleccionada:
                        evaluaciones_ids.add(resp.asignacion.id)
                    else:
                        respuestas_sin_seleccion += 1

            total_con_respuestas = len(evaluaciones_ids)

            analisis_por_competencia[categoria] = {
                'evaluaciones_con_respuestas': total_con_respuestas,
                'respuestas_sin_seleccion': respuestas_sin_seleccion
            }

            # Mostrar resultado
            if total_con_respuestas == total_evaluaciones:
                self.stdout.write(self.style.SUCCESS(
                    f'  [OK] {categoria}: {total_con_respuestas}/{total_evaluaciones} evaluaciones'
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f'  [X] {categoria}: {total_con_respuestas}/{total_evaluaciones} evaluaciones '
                    f'({total_evaluaciones - total_con_respuestas} FALTANTES)'
                ))

            if respuestas_sin_seleccion > 0:
                self.stdout.write(self.style.WARNING(
                    f'    [!] {respuestas_sin_seleccion} respuestas sin opcion seleccionada'
                ))

        # 5. Análisis Detallado de Evaluaciones Faltantes
        self.stdout.write(self.style.WARNING('\n5. EVALUACIONES SIN RESPUESTAS POR COMPETENCIA:'))
        self.stdout.write('-' * 80)

        for categoria in competencias_esperadas:
            # Obtener IDs de evaluaciones con respuestas en esta categoría (usando normalización)
            evaluaciones_con_respuestas = set()

            respuestas = RespuestaEvaluacion.objects.filter(
                asignacion__estado='completada',
                asignacion__puntaje_total__isnull=False,
                asignacion__evaluacion__tipo_evaluacion__codigo__startswith='ANUAL_',
                opcion_seleccionada__isnull=False
            ).select_related('pregunta', 'asignacion')

            for resp in respuestas:
                if normalizar_categoria(resp.pregunta.categoria) == categoria:
                    evaluaciones_con_respuestas.add(resp.asignacion.id)

            # Todas las evaluaciones completadas
            todas_evaluaciones = set(evaluaciones_completadas.values_list('id', flat=True))

            # Evaluaciones sin respuestas en esta categoría
            evaluaciones_sin_respuestas = todas_evaluaciones - evaluaciones_con_respuestas

            if evaluaciones_sin_respuestas:
                self.stdout.write(self.style.ERROR(f'\n  {categoria}:'))
                self.stdout.write(f'    {len(evaluaciones_sin_respuestas)} evaluaciones sin respuestas en esta categoría')

                # Mostrar primeras 5 como muestra
                muestra = list(evaluaciones_sin_respuestas)[:5]
                for eval_id in muestra:
                    try:
                        asignacion = AsignacionEvaluacion.objects.get(id=eval_id)
                        self.stdout.write(
                            f'      - ID: {eval_id}, Empleado: {asignacion.empleado.nombre_completo}, '
                            f'Tipo: {asignacion.evaluacion.tipo_evaluacion}'
                        )
                    except AsignacionEvaluacion.DoesNotExist:
                        pass

                if len(evaluaciones_sin_respuestas) > 5:
                    self.stdout.write(f'      ... y {len(evaluaciones_sin_respuestas) - 5} más')

        # 6. Análisis por Tipo de Evaluación
        self.stdout.write(self.style.WARNING('\n6. ANÁLISIS POR TIPO DE EVALUACIÓN:'))
        self.stdout.write('-' * 80)

        tipos_evaluacion = evaluaciones_completadas.values(
            'evaluacion__tipo_evaluacion'
        ).annotate(total=Count('id')).order_by('evaluacion__tipo_evaluacion')

        for tipo in tipos_evaluacion:
            tipo_nombre = tipo['evaluacion__tipo_evaluacion']
            total = tipo['total']
            self.stdout.write(f'\n  {tipo_nombre}: {total} evaluaciones')

            # Verificar competencias por tipo (usando normalización)
            for categoria in competencias_esperadas:
                evaluaciones_tipo = AsignacionEvaluacion.objects.filter(
                    estado='completada',
                    puntaje_total__isnull=False,
                    evaluacion__tipo_evaluacion__codigo__startswith='ANUAL_'
                )

                evaluaciones_con_cat = set()
                for eval in evaluaciones_tipo:
                    # Buscar respuestas cuya categoría normalizada coincida
                    respuestas_eval = RespuestaEvaluacion.objects.filter(
                        asignacion=eval,
                        opcion_seleccionada__isnull=False
                    ).select_related('pregunta')

                    for resp in respuestas_eval:
                        if normalizar_categoria(resp.pregunta.categoria) == categoria:
                            evaluaciones_con_cat.add(eval.id)
                            break  # Ya encontramos una, no necesitamos seguir buscando

                porcentaje = (len(evaluaciones_con_cat) / total * 100) if total > 0 else 0

                if porcentaje == 100:
                    self.stdout.write(self.style.SUCCESS(
                        f'    [OK] {categoria}: {len(evaluaciones_con_cat)}/{total} ({porcentaje:.1f}%)'
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f'    [X] {categoria}: {len(evaluaciones_con_cat)}/{total} ({porcentaje:.1f}%)'
                    ))

        # 7. Resumen y Recomendaciones
        self.stdout.write(self.style.WARNING('\n7. RESUMEN Y RECOMENDACIONES:'))
        self.stdout.write('=' * 80)

        todas_consistentes = all(
            datos['evaluaciones_con_respuestas'] == total_evaluaciones
            for datos in analisis_por_competencia.values()
        )

        if todas_consistentes:
            self.stdout.write(self.style.SUCCESS(
                '\n[OK] TODAS las evaluaciones tienen respuestas en las 4 competencias.'
            ))
            self.stdout.write(self.style.SUCCESS(
                '  El sistema esta funcionando correctamente.\n'
            ))
        else:
            self.stdout.write(self.style.ERROR(
                '\n[X] INCONSISTENCIA DETECTADA: No todas las evaluaciones tienen las 4 competencias.'
            ))
            self.stdout.write(self.style.WARNING('\nPosibles causas:'))
            self.stdout.write('  1. Evaluaciones creadas con plantillas diferentes')
            self.stdout.write('  2. Respuestas sin opción seleccionada (preguntas sin responder)')
            self.stdout.write('  3. Preguntas que no están asociadas a las competencias esperadas')
            self.stdout.write('\nRecomendaciones:')
            self.stdout.write('  - Revisar las plantillas de evaluación por tipo')
            self.stdout.write('  - Verificar si hay preguntas obligatorias sin responder')
            self.stdout.write('  - Normalizar las categorías de preguntas\n')

        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('ANÁLISIS COMPLETADO'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))
