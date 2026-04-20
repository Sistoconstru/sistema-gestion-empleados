"""
Comando para regenerar el plan de mejora de una evaluación específica
"""
from django.core.management.base import BaseCommand
from apps.evaluations.models import AsignacionEvaluacion, RespuestaEvaluacion, PlanMejoraPredefinido
import sys


class Command(BaseCommand):
    help = 'Regenera el plan de mejora para una evaluación completada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--asignacion-id',
            type=str,
            help='ID de la asignación de evaluación'
        )

    def handle(self, *args, **options):
        asignacion_id = options.get('asignacion_id')

        if not asignacion_id:
            self.stdout.write(self.style.ERROR('Debe proporcionar --asignacion-id'))
            return

        try:
            asignacion = AsignacionEvaluacion.objects.get(id=asignacion_id)
        except AsignacionEvaluacion.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'No se encontró asignación con ID: {asignacion_id}'))
            return

        if asignacion.estado != 'completada':
            self.stdout.write(self.style.ERROR('La evaluación no está completada'))
            return

        self.stdout.write(f'Regenerando plan de mejora para:')
        self.stdout.write(f'  Empleado: {asignacion.empleado_evaluado.nombre_completo}')
        self.stdout.write(f'  Evaluación: {asignacion.evaluacion.nombre}')
        self.stdout.write(f'  Tipo: {asignacion.evaluacion.tipo_evaluacion.codigo}')
        self.stdout.write('')

        # Obtener respuestas
        respuestas = RespuestaEvaluacion.objects.filter(
            asignacion=asignacion
        ).select_related('pregunta', 'opcion_seleccionada')

        if not respuestas.exists():
            self.stdout.write(self.style.ERROR('No hay respuestas para esta evaluación'))
            return

        tipo_eval_codigo = asignacion.evaluacion.tipo_evaluacion.codigo
        plan_mejora_texto = None

        try:
            if tipo_eval_codigo == 'ANUAL_AUX_RRHH':
                from apps.evaluations.utils.respuestas_predefinidas_auxiliar_rrhh import (
                    generar_plan_mejora_auxiliar_rrhh,
                    calcular_puntaje_ponderado_auxiliar_rrhh
                )
                resultado_evaluacion = calcular_puntaje_ponderado_auxiliar_rrhh(respuestas)
                plan_mejora_texto = generar_plan_mejora_auxiliar_rrhh(respuestas, resultado_evaluacion)

                # Actualizar puntajes en la asignación
                asignacion.puntaje_total = resultado_evaluacion['puntaje_porcentaje']
                asignacion.puntaje_escala = resultado_evaluacion['puntaje_escala']
                asignacion.nivel_desempeno = resultado_evaluacion['nivel_desempeno']
                asignacion.save()

                self.stdout.write(self.style.SUCCESS(f'[OK] Puntaje: {resultado_evaluacion["puntaje_porcentaje"]:.2f}%'))
                self.stdout.write(self.style.SUCCESS(f'[OK] Escala: {resultado_evaluacion["puntaje_escala"]:.2f}/5'))
                self.stdout.write(self.style.SUCCESS(f'[OK] Nivel: {resultado_evaluacion["nivel_desempeno"]}'))

            elif tipo_eval_codigo == 'ANUAL_AUX_TESORERIA':
                from apps.evaluations.utils.respuestas_predefinidas_auxiliar_tesoreria import (
                    generar_plan_mejora_auxiliar_tesoreria,
                    calcular_puntaje_ponderado_auxiliar_tesoreria
                )
                resultado_evaluacion = calcular_puntaje_ponderado_auxiliar_tesoreria(respuestas)
                plan_mejora_texto = generar_plan_mejora_auxiliar_tesoreria(respuestas, resultado_evaluacion)

                # Actualizar puntajes en la asignación
                asignacion.puntaje_total = resultado_evaluacion['puntaje_porcentaje']
                asignacion.puntaje_escala = resultado_evaluacion['puntaje_escala']
                asignacion.nivel_desempeno = resultado_evaluacion['nivel_desempeno']
                asignacion.save()

                self.stdout.write(self.style.SUCCESS(f'[OK] Puntaje: {resultado_evaluacion["puntaje_porcentaje"]:.2f}%'))
                self.stdout.write(self.style.SUCCESS(f'[OK] Escala: {resultado_evaluacion["puntaje_escala"]:.2f}/5'))
                self.stdout.write(self.style.SUCCESS(f'[OK] Nivel: {resultado_evaluacion["nivel_desempeno"]}'))

            else:
                self.stdout.write(self.style.ERROR(f'Tipo de evaluación no soportado: {tipo_eval_codigo}'))
                return

            if not plan_mejora_texto:
                self.stdout.write(self.style.ERROR('No se pudo generar el plan de mejora'))
                return

            # Eliminar plan existente si hay
            PlanMejoraPredefinido.objects.filter(asignacion_evaluacion=asignacion).delete()

            # Determinar quién genera el plan (debe ser un Usuario)
            if asignacion.evaluador and hasattr(asignacion.evaluador, 'usuario'):
                generado_por = asignacion.evaluador.usuario
            else:
                generado_por = asignacion.empleado_evaluado.usuario

            # Crear nuevo plan
            plan = PlanMejoraPredefinido.objects.create(
                asignacion_evaluacion=asignacion,
                plan_mejora=plan_mejora_texto,
                generado_por=generado_por
            )

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('[OK] Plan de mejora regenerado exitosamente'))
            self.stdout.write(f'  ID del plan: {plan.id}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al generar plan: {str(e)}'))
            import traceback
            traceback.print_exc()
