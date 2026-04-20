"""
Comando para recalcular el puntaje de evaluaciones de Auxiliar Contable completadas
que tienen el puntaje incorrecto debido a un bug en la función _calcular_resultado_evaluacion
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from apps.evaluations.models import AsignacionEvaluacion, RespuestaEvaluacion, ResultadoEvaluacion
from apps.evaluations.utils.respuestas_predefinidas_auxiliar_contable import calcular_puntaje_ponderado_auxiliar_contable


class Command(BaseCommand):
    help = 'Recalcula el puntaje de evaluaciones de Auxiliar Contable completadas'

    def handle(self, *args, **options):
        self.stdout.write("="*80)
        self.stdout.write("RECALCULANDO PUNTAJES DE AUXILIAR CONTABLE")
        self.stdout.write("="*80)

        # Buscar todas las evaluaciones de Auxiliar Contable completadas
        asignaciones = AsignacionEvaluacion.objects.filter(
            evaluacion__tipo_evaluacion__codigo='ANUAL_AUX_CONTABLE',
            estado='completada'
        ).select_related('empleado_evaluado', 'evaluacion')

        if not asignaciones.exists():
            self.stdout.write(self.style.WARNING("No se encontraron evaluaciones de Auxiliar Contable completadas"))
            return

        self.stdout.write(f"\nSe encontraron {asignaciones.count()} evaluaciones de Auxiliar Contable completadas\n")

        for asignacion in asignaciones:
            self.stdout.write(f"\n{'='*80}")
            self.stdout.write(f"Asignación ID: {asignacion.id}")
            self.stdout.write(f"Empleado: {asignacion.empleado_evaluado.nombre_completo}")
            self.stdout.write(f"Puntaje actual en BD: {asignacion.puntaje_total}")

            # Obtener respuestas
            respuestas = RespuestaEvaluacion.objects.filter(
                asignacion=asignacion
            ).select_related('pregunta', 'opcion_seleccionada')

            if not respuestas.exists():
                self.stdout.write(self.style.WARNING(f"  [AVISO] No se encontraron respuestas para esta asignación"))
                continue

            # Recalcular usando la función correcta
            resultado_calc = calcular_puntaje_ponderado_auxiliar_contable(respuestas)

            puntaje_final = Decimal(str(resultado_calc['puntaje_escala']))  # 1-5
            porcentaje = Decimal(str(resultado_calc['puntaje_porcentaje']))  # 0-100
            nivel_desempeno = resultado_calc['nivel_desempeno']

            # Mapear nivel_desempeno a clasificación estándar
            mapeo_clasificacion = {
                'Muy alto': 'excelente',
                'Alto': 'sobresaliente',
                'Moderado': 'satisfactorio',
                'Bajo': 'mejorable',
                'Muy bajo': 'insatisfactorio'
            }
            clasificacion = mapeo_clasificacion.get(nivel_desempeno, 'satisfactorio')

            # Generar aspectos según nivel
            if porcentaje >= 91:
                aspectos_positivos = "• Desempeño excepcional en todas las competencias evaluadas\n• Supera consistentemente las expectativas en todas las categorías\n• Referente de excelencia para el equipo"
                areas_mejora = "• Continuar siendo modelo de excelencia\n• Liderar programas de mejora en el área\n• Mentor de compañeros con menor desempeño"
            elif porcentaje >= 76:
                aspectos_positivos = "• Desempeño destacado en la mayoría de competencias\n• Supera las expectativas del cargo\n• Contribuye significativamente a objetivos del área"
                areas_mejora = "• Fortalecer competencias con calificación moderada\n• Incrementar participación en proyectos de mejora\n• Desarrollar habilidades de liderazgo"
            elif porcentaje >= 61:
                aspectos_positivos = "• Cumple satisfactoriamente con las responsabilidades del cargo\n• Desempeño aceptable en la mayoría de competencias\n• Mantiene estándares mínimos de calidad"
                areas_mejora = "• Mejorar competencias con calificación baja\n• Incrementar eficiencia y productividad\n• Fortalecer habilidades técnicas específicas"
            elif porcentaje >= 41:
                aspectos_positivos = "• Muestra disposición para aprender y mejorar\n• Cumple con algunas responsabilidades básicas\n• Asiste puntualmente a sus labores"
                areas_mejora = "• Requiere capacitación urgente en competencias críticas\n• Necesita supervisión y acompañamiento constante\n• Desarrollar habilidades técnicas básicas del puesto"
            else:
                aspectos_positivos = "• Asiste a sus labores\n• Muestra interés en el desarrollo profesional"
                areas_mejora = "• Requiere mejora urgente en todas las competencias evaluadas\n• Necesita capacitación intensiva y supervisión directa\n• Plan de acción correctivo inmediato"

            # Detalle por categorías
            detalle_categorias = resultado_calc.get('puntajes_categorias', {})
            comentarios_detalle = "DESEMPEÑO POR CATEGORÍAS:\n"
            for cat, promedio in detalle_categorias.items():
                porcentaje_cat = ((promedio - 1) / 4) * 100
                comentarios_detalle += f"• {cat}: {promedio}/5 ({porcentaje_cat:.1f}%)\n"

            comentarios_generales = f'Evaluación anual completada con {porcentaje:.1f}% de cumplimiento.\n\n{comentarios_detalle}'

            # Determinar recomendación
            if porcentaje >= 76:
                recomendaciones = 'Desempeño destacado. Se recomienda considerar para promociones o responsabilidades adicionales.'
            elif porcentaje >= 61:
                recomendaciones = 'Desempeño satisfactorio. El empleado continúa en el cargo con seguimiento en áreas de mejora.'
            else:
                recomendaciones = 'Desempeño por debajo de expectativas. Requiere plan de mejora con seguimientos bimensuales.'

            self.stdout.write(f"\nPuntaje recalculado:")
            self.stdout.write(f"  Porcentaje: {porcentaje}%")
            self.stdout.write(f"  Escala 5: {puntaje_final}")
            self.stdout.write(f"  Nivel: {nivel_desempeno} ({clasificacion})")

            # Preguntar si se debe actualizar
            respuesta = input(f"\n¿Actualizar esta evaluación? (s/n): ")

            if respuesta.lower() == 's':
                try:
                    with transaction.atomic():
                        # Actualizar ResultadoEvaluacion
                        resultado, created = ResultadoEvaluacion.objects.get_or_create(
                            asignacion=asignacion,
                            defaults={
                                'puntaje_final': puntaje_final,
                                'porcentaje_obtenido': porcentaje,
                                'nivel_desempeño': clasificacion,
                                'aspectos_positivos': aspectos_positivos,
                                'areas_mejora': areas_mejora,
                                'comentarios_generales': comentarios_generales,
                                'recomendaciones': recomendaciones,
                                'generado_por': asignacion.evaluador.usuario if asignacion.evaluador and asignacion.evaluador.usuario else None,
                            }
                        )

                        if not created:
                            resultado.puntaje_final = puntaje_final
                            resultado.porcentaje_obtenido = porcentaje
                            resultado.nivel_desempeño = clasificacion
                            resultado.aspectos_positivos = aspectos_positivos
                            resultado.areas_mejora = areas_mejora
                            resultado.comentarios_generales = comentarios_generales
                            resultado.recomendaciones = recomendaciones
                            resultado.save()

                        # Actualizar AsignacionEvaluacion
                        asignacion.puntaje_total = porcentaje
                        asignacion.porcentaje_completado = porcentaje
                        asignacion.save()

                        self.stdout.write(self.style.SUCCESS(f"  [OK] Evaluación actualizada correctamente"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  [ERROR] Error al actualizar: {str(e)}"))
            else:
                self.stdout.write(self.style.WARNING(f"  [OMITIDO] Evaluación omitida"))

        self.stdout.write(f"\n{'='*80}")
        self.stdout.write(self.style.SUCCESS("[OK] Proceso completado"))
        self.stdout.write("="*80)
