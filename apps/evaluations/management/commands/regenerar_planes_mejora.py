"""
Comando para regenerar planes de mejora con los valores actualizados
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.evaluations.models import PlanMejoraPredefinido, RespuestaEvaluacion
from decimal import Decimal


class Command(BaseCommand):
    help = 'Regenera el contenido de planes de mejora con valores actualizados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--plan-id',
            type=int,
            help='Regenerar solo un plan específico',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar cambios sin guardarlos',
        )

    def handle(self, *args, **options):
        plan_id = options.get('plan_id')
        dry_run = options.get('dry_run', False)

        # Obtener planes de mejora de evaluaciones anuales
        planes = PlanMejoraPredefinido.objects.filter(
            asignacion_evaluacion__evaluacion__tipo_evaluacion__codigo__in=['ANUAL_AUX_PROCESOS', 'ANUAL_MANTENIMIENTO']
        ).select_related(
            'asignacion_evaluacion__evaluacion__tipo_evaluacion',
            'asignacion_evaluacion__empleado_evaluado'
        )

        if plan_id:
            planes = planes.filter(id=plan_id)

        total = planes.count()
        self.stdout.write(f"\n{'=' * 80}")
        self.stdout.write(f"Planes de mejora encontrados: {total}")
        self.stdout.write(f"{'=' * 80}\n")

        if total == 0:
            self.stdout.write(self.style.WARNING('No se encontraron planes para regenerar'))
            return

        regenerados = 0

        with transaction.atomic():
            for plan in planes:
                asignacion = plan.asignacion_evaluacion
                tipo_evaluacion_codigo = asignacion.evaluacion.tipo_evaluacion.codigo

                self.stdout.write(f"\n{'-' * 80}")
                self.stdout.write(f"Plan ID: {plan.id}")
                self.stdout.write(f"Empleado: {asignacion.empleado_evaluado.nombre_completo}")
                self.stdout.write(f"Tipo: {tipo_evaluacion_codigo}")

                # Obtener respuestas
                respuestas = RespuestaEvaluacion.objects.filter(
                    asignacion=asignacion
                ).select_related('pregunta', 'opcion_seleccionada')

                if not respuestas.exists():
                    self.stdout.write(self.style.WARNING("  → Sin respuestas, saltando"))
                    continue

                # Recalcular puntaje y regenerar plan
                if tipo_evaluacion_codigo == 'ANUAL_AUX_PROCESOS':
                    from apps.evaluations.utils.respuestas_predefinidas_auxiliar_procesos import (
                        calcular_puntaje_ponderado_auxiliar_procesos,
                        generar_plan_mejora_auxiliar_procesos
                    )
                    resultado_calc = calcular_puntaje_ponderado_auxiliar_procesos(respuestas)
                    nuevo_plan = generar_plan_mejora_auxiliar_procesos(respuestas, resultado_calc)

                elif tipo_evaluacion_codigo == 'ANUAL_MANTENIMIENTO':
                    from apps.evaluations.utils.respuestas_predefinidas_mantenimiento import (
                        calcular_puntaje_ponderado_mantenimiento,
                        generar_plan_mejora_mantenimiento
                    )
                    resultado_calc = calcular_puntaje_ponderado_mantenimiento(respuestas)
                    nuevo_plan = generar_plan_mejora_mantenimiento(respuestas, resultado_calc)
                else:
                    self.stdout.write(self.style.WARNING(f"  → Tipo no soportado: {tipo_evaluacion_codigo}"))
                    continue

                # Mostrar cambios
                self.stdout.write(f"\nPuntaje anterior: {asignacion.puntaje_total:.2f}%")
                self.stdout.write(f"Puntaje recalculado: {resultado_calc['puntaje_porcentaje']:.2f}%")
                self.stdout.write(f"Nivel: {resultado_calc['nivel_desempeno']}")

                self.stdout.write(f"\nPlan anterior (primeras 200 chars):")
                self.stdout.write(f"  {plan.plan_mejora[:200]}...")
                self.stdout.write(f"\nPlan nuevo (primeras 200 chars):")
                self.stdout.write(f"  {nuevo_plan[:200]}...")

                if not dry_run:
                    # Actualizar plan
                    plan.plan_mejora = nuevo_plan
                    plan.save()

                    # Actualizar puntaje de asignación
                    asignacion.puntaje_total = Decimal(str(resultado_calc['puntaje_porcentaje']))
                    asignacion.save()

                    self.stdout.write(self.style.SUCCESS("\n  ✓ Plan regenerado y puntaje actualizado"))
                else:
                    self.stdout.write(self.style.WARNING("\n  → DRY RUN: No se guardó"))

                regenerados += 1

            if dry_run:
                self.stdout.write(f"\n{'=' * 80}")
                self.stdout.write(self.style.WARNING("DRY RUN: Los cambios NO se guardaron"))
                self.stdout.write(f"{'=' * 80}\n")
                transaction.set_rollback(True)

        # Resumen
        self.stdout.write(f"\n{'=' * 80}")
        self.stdout.write(self.style.SUCCESS(f"Planes regenerados: {regenerados}"))
        self.stdout.write(f"{'=' * 80}\n")
