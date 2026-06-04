"""
Comando para probar el impacto de normalizar categorías en los puntajes de evaluaciones.
Compara puntajes calculados con y sin normalización.
"""

from django.core.management.base import BaseCommand
from apps.evaluations.models import AsignacionEvaluacion, RespuestaEvaluacion
from collections import defaultdict


class Command(BaseCommand):
    help = 'Prueba el impacto de normalizar categorías en los puntajes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Número de evaluaciones a analizar (default: 10)'
        )

    def handle(self, *args, **options):
        limit = options['limit']

        self.stdout.write(self.style.SUCCESS('\n' + '='*100))
        self.stdout.write(self.style.SUCCESS('PRUEBA DE IMPACTO: NORMALIZACION DE CATEGORIAS'))
        self.stdout.write(self.style.SUCCESS('='*100 + '\n'))

        # Función para normalizar categorías
        def normalizar_categoria(categoria_original):
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
            return categoria_original

        # Pesos de categorías
        pesos_categorias = {
            'Competencias Organizacionales': 10.0,
            'Objetivos - El Hacer': 40.0,
            'Competencias Interpersonales - El Ser': 25.0,
            'Competencias Técnicas - El Saber': 25.0
        }

        # Obtener muestra de evaluaciones
        evaluaciones = AsignacionEvaluacion.objects.filter(
            estado='completada',
            puntaje_total__isnull=False,
            evaluacion__tipo_evaluacion__codigo__startswith='ANUAL_'
        )[:limit]

        total_evaluaciones = evaluaciones.count()
        self.stdout.write(f'Analizando {total_evaluaciones} evaluaciones...\n')

        diferencias = []
        evaluaciones_afectadas = 0
        max_diferencia = 0
        sum_diferencias = 0

        for asignacion in evaluaciones:
            respuestas = RespuestaEvaluacion.objects.filter(
                asignacion=asignacion,
                opcion_seleccionada__isnull=False
            ).select_related('pregunta', 'opcion_seleccionada')

            if not respuestas.exists():
                continue

            # ============ CALCULO SIN NORMALIZAR (Lógica actual) ============
            puntajes_sin_norm = defaultdict(float)
            preguntas_sin_norm = defaultdict(int)

            for r in respuestas:
                if r.pregunta.peso_porcentual == 0:  # SST
                    continue
                cat = r.pregunta.categoria  # SIN NORMALIZAR
                valor = float(r.opcion_seleccionada.valor_numerico)
                puntajes_sin_norm[cat] += valor
                preguntas_sin_norm[cat] += 1

            puntaje_sin_norm = 0.0
            for cat, peso in pesos_categorias.items():
                if preguntas_sin_norm[cat] > 0:
                    promedio = puntajes_sin_norm[cat] / preguntas_sin_norm[cat]
                    porcentaje = ((promedio - 1) / 4) * 100
                    puntaje_sin_norm += (porcentaje * peso) / 100

            # ============ CALCULO CON NORMALIZAR (Lógica corregida) ============
            puntajes_con_norm = defaultdict(float)
            preguntas_con_norm = defaultdict(int)

            for r in respuestas:
                if r.pregunta.peso_porcentual == 0:  # SST
                    continue
                cat = normalizar_categoria(r.pregunta.categoria)  # CON NORMALIZAR
                if cat and cat in pesos_categorias:
                    valor = float(r.opcion_seleccionada.valor_numerico)
                    puntajes_con_norm[cat] += valor
                    preguntas_con_norm[cat] += 1

            puntaje_con_norm = 0.0
            for cat, peso in pesos_categorias.items():
                if preguntas_con_norm[cat] > 0:
                    promedio = puntajes_con_norm[cat] / preguntas_con_norm[cat]
                    porcentaje = ((promedio - 1) / 4) * 100
                    puntaje_con_norm += (porcentaje * peso) / 100

            # Calcular diferencia
            diferencia = abs(puntaje_con_norm - puntaje_sin_norm)
            puntaje_actual_bd = float(asignacion.puntaje_total)

            # Verificar si hay diferencia significativa
            if diferencia > 0.01:  # Más de 0.01 puntos de diferencia
                evaluaciones_afectadas += 1
                max_diferencia = max(max_diferencia, diferencia)
                sum_diferencias += diferencia

                # Analizar categorías con problemas
                categorias_problema = []
                for r in respuestas:
                    cat_original = r.pregunta.categoria
                    cat_normalizada = normalizar_categoria(cat_original)
                    if cat_original != cat_normalizada:
                        categorias_problema.append(f'{cat_original} -> {cat_normalizada}')

                diferencias.append({
                    'empleado': asignacion.empleado_evaluado.nombre_completo,
                    'tipo_eval': asignacion.evaluacion.nombre,
                    'puntaje_bd': puntaje_actual_bd,
                    'puntaje_sin_norm': puntaje_sin_norm,
                    'puntaje_con_norm': puntaje_con_norm,
                    'diferencia': diferencia,
                    'categorias_problema': list(set(categorias_problema))
                })

        # ============ MOSTRAR RESULTADOS ============
        self.stdout.write(self.style.WARNING('\nRESULTADO DEL ANALISIS:'))
        self.stdout.write('='*100)

        if evaluaciones_afectadas == 0:
            self.stdout.write(self.style.SUCCESS(
                f'\n[OK] TODAS las {total_evaluaciones} evaluaciones tienen puntajes CORRECTOS.'
            ))
            self.stdout.write(self.style.SUCCESS(
                'No se encontraron diferencias. Las categorias ya estan normalizadas.\n'
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f'\n[!] {evaluaciones_afectadas} de {total_evaluaciones} evaluaciones tienen puntajes INCORRECTOS '
                f'({(evaluaciones_afectadas/total_evaluaciones*100):.1f}%)\n'
            ))

            promedio_diferencia = sum_diferencias / evaluaciones_afectadas if evaluaciones_afectadas > 0 else 0

            self.stdout.write(f'Diferencia maxima encontrada: {max_diferencia:.2f} puntos')
            self.stdout.write(f'Diferencia promedio: {promedio_diferencia:.2f} puntos\n')

            # Mostrar casos más afectados
            diferencias_ordenadas = sorted(diferencias, key=lambda x: x['diferencia'], reverse=True)

            self.stdout.write(self.style.WARNING('\nTOP 5 EVALUACIONES MAS AFECTADAS:'))
            self.stdout.write('-'*100)

            for i, caso in enumerate(diferencias_ordenadas[:5], 1):
                self.stdout.write(f'\n{i}. {caso["empleado"]}')
                self.stdout.write(f'   Tipo: {caso["tipo_eval"]}')
                self.stdout.write(f'   Puntaje en BD: {caso["puntaje_bd"]:.2f}')
                self.stdout.write(f'   Calculado sin normalizar: {caso["puntaje_sin_norm"]:.2f}')
                self.stdout.write(f'   Calculado con normalizar: {caso["puntaje_con_norm"]:.2f}')
                self.stdout.write(self.style.ERROR(f'   DIFERENCIA: {caso["diferencia"]:.2f} puntos'))

                if caso['categorias_problema']:
                    self.stdout.write('   Categorias con problemas:')
                    for cat_problema in caso['categorias_problema'][:3]:
                        self.stdout.write(f'     - {cat_problema}')

            # Mostrar todos los casos si son pocos
            if len(diferencias) <= 20:
                self.stdout.write(self.style.WARNING('\n\nTODAS LAS EVALUACIONES AFECTADAS:'))
                self.stdout.write('-'*100)

                for caso in diferencias_ordenadas:
                    diff_signo = '+' if caso['puntaje_con_norm'] > caso['puntaje_sin_norm'] else ''
                    self.stdout.write(
                        f'{caso["empleado"][:40]:40} | '
                        f'BD: {caso["puntaje_bd"]:5.2f} | '
                        f'Actual: {caso["puntaje_sin_norm"]:5.2f} | '
                        f'Correcto: {caso["puntaje_con_norm"]:5.2f} | '
                        f'Diff: {diff_signo}{caso["diferencia"]:.2f}'
                    )

        self.stdout.write(self.style.SUCCESS('\n' + '='*100))
        self.stdout.write(self.style.SUCCESS('ANALISIS COMPLETADO'))
        self.stdout.write(self.style.SUCCESS('='*100 + '\n'))

        # Recomendación
        if evaluaciones_afectadas > 0:
            self.stdout.write(self.style.WARNING('RECOMENDACION:'))
            self.stdout.write('1. Actualizar los 16 archivos de utils para normalizar categorias')
            self.stdout.write('2. Ejecutar comando de recalcular evaluaciones para corregir puntajes')
            self.stdout.write('3. Verificar que planes de mejora reflejen las competencias correctas\n')
