"""
Comando para verificar el estado de planes de mejora
"""
from django.core.management.base import BaseCommand
from apps.evaluations.models import AsignacionEvaluacion, PlanMejoraPredefinido


class Command(BaseCommand):
    help = 'Verifica el estado de las últimas evaluaciones y sus planes de mejora'

    def handle(self, *args, **options):
        # Ver últimas evaluaciones completadas
        self.stdout.write(f"\n{'='*80}")
        self.stdout.write("ÚLTIMAS EVALUACIONES COMPLETADAS")
        self.stdout.write(f"{'='*80}\n")

        asignaciones = AsignacionEvaluacion.objects.filter(
            estado='completado'
        ).select_related(
            'empleado_evaluado',
            'evaluacion',
            'evaluacion__tipo_evaluacion'
        ).order_by('-id')[:10]

        for asig in asignaciones:
            self.stdout.write(f"\n{'-'*80}")
            self.stdout.write(f"ID Asignación: {asig.id}")
            self.stdout.write(f"Empleado: {asig.empleado_evaluado.nombre_completo}")
            self.stdout.write(f"Evaluación: {asig.evaluacion.nombre}")
            tipo = asig.evaluacion.tipo_evaluacion.codigo if asig.evaluacion.tipo_evaluacion else 'SIN TIPO'
            self.stdout.write(f"Tipo: {tipo}")
            self.stdout.write(f"Estado: {asig.estado}")
            self.stdout.write(f"Estado aprobación: {asig.estado_aprobacion}")
            self.stdout.write(f"Puntaje: {asig.puntaje_total}")
            self.stdout.write(f"Porcentaje: {asig.porcentaje_completado}%")

            # Buscar plan de mejora
            try:
                plan = PlanMejoraPredefinido.objects.get(asignacion_evaluacion=asig)
                self.stdout.write(self.style.SUCCESS(f"\n✓ TIENE PLAN DE MEJORA:"))
                self.stdout.write(f"  - ID Plan: {plan.id}")
                self.stdout.write(f"  - Estado: {plan.estado}")
                self.stdout.write(f"  - Aceptado por empleado: {plan.aceptado_por_empleado}")
                self.stdout.write(f"  - Fecha aceptación: {plan.fecha_aceptacion_empleado}")
                self.stdout.write(f"  - Rechazado: {plan.rechazado_por_empleado}")
                self.stdout.write(f"  - Primeros 100 chars: {plan.plan_mejora[:100]}...")
            except PlanMejoraPredefinido.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"\n✗ NO TIENE PLAN DE MEJORA"))
            except PlanMejoraPredefinido.MultipleObjectsReturned:
                planes = PlanMejoraPredefinido.objects.filter(asignacion_evaluacion=asig)
                self.stdout.write(self.style.WARNING(f"\n⚠ TIENE {planes.count()} PLANES (DUPLICADOS):"))
                for p in planes:
                    self.stdout.write(f"  - ID: {p.id}, Estado: {p.estado}")

        self.stdout.write(f"\n{'='*80}\n")
