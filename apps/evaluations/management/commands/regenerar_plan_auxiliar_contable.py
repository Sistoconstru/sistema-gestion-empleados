"""
Comando para regenerar el plan de mejora de evaluaciones de Auxiliar Contable
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.evaluations.models import AsignacionEvaluacion, RespuestaEvaluacion, PlanMejoraPredefinido
from apps.evaluations.utils.respuestas_predefinidas_auxiliar_contable import (
    calcular_puntaje_ponderado_auxiliar_contable,
    generar_plan_mejora_auxiliar_contable
)


class Command(BaseCommand):
    help = 'Regenera el plan de mejora de evaluaciones de Auxiliar Contable completadas'

    def handle(self, *args, **options):
        self.stdout.write("="*80)
        self.stdout.write("REGENERANDO PLANES DE MEJORA - AUXILIAR CONTABLE")
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
            self.stdout.write(f"Asignacion ID: {asignacion.id}")
            self.stdout.write(f"Empleado: {asignacion.empleado_evaluado.nombre_completo}")
            self.stdout.write(f"Puntaje: {asignacion.puntaje_total}%")

            # Obtener respuestas
            respuestas = RespuestaEvaluacion.objects.filter(
                asignacion=asignacion
            ).select_related('pregunta', 'opcion_seleccionada')

            if not respuestas.exists():
                self.stdout.write(self.style.WARNING(f"  [AVISO] No se encontraron respuestas para esta asignacion"))
                continue

            # Recalcular y generar plan
            resultado_calc = calcular_puntaje_ponderado_auxiliar_contable(respuestas)
            plan_mejora_texto = generar_plan_mejora_auxiliar_contable(respuestas, resultado_calc)

            self.stdout.write(f"\nPlan generado ({len(plan_mejora_texto)} caracteres)")

            # Preguntar si se debe actualizar
            respuesta = input(f"\nRegenarar plan de mejora? (s/n): ")

            if respuesta.lower() == 's':
                try:
                    with transaction.atomic():
                        # Eliminar plan existente si lo hay
                        PlanMejoraPredefinido.objects.filter(
                            asignacion_evaluacion=asignacion
                        ).delete()

                        # Crear nuevo plan
                        PlanMejoraPredefinido.objects.create(
                            asignacion_evaluacion=asignacion,
                            plan_mejora=plan_mejora_texto,
                            generado_por=asignacion.evaluador.usuario if asignacion.evaluador and asignacion.evaluador.usuario else None,
                            estado='pendiente_aprobacion'
                        )

                        self.stdout.write(self.style.SUCCESS(f"  [OK] Plan de mejora regenerado correctamente"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  [ERROR] Error al regenerar: {str(e)}"))
            else:
                self.stdout.write(self.style.WARNING(f"  [OMITIDO] Plan omitido"))

        self.stdout.write(f"\n{'='*80}")
        self.stdout.write(self.style.SUCCESS("[OK] Proceso completado"))
        self.stdout.write("="*80)
