"""
Comando para ver todas las asignaciones de evaluación y sus estados
"""
from django.core.management.base import BaseCommand
from apps.evaluations.models import AsignacionEvaluacion, PlanMejoraPredefinido


class Command(BaseCommand):
    help = 'Ver todas las asignaciones de evaluación con sus estados'

    def handle(self, *args, **options):
        # Ver TODAS las evaluaciones (sin filtro de estado)
        self.stdout.write(f"\n{'='*80}")
        self.stdout.write("TODAS LAS EVALUACIONES (ÚLTIMAS 20)")
        self.stdout.write(f"{'='*80}\n")

        asignaciones = AsignacionEvaluacion.objects.all().select_related(
            'empleado_evaluado',
            'evaluacion',
            'evaluacion__tipo_evaluacion',
            'evaluador'
        ).order_by('-id')[:20]

        self.stdout.write(f"Total asignaciones encontradas: {AsignacionEvaluacion.objects.count()}\n")

        for asig in asignaciones:
            self.stdout.write(f"\n{'-'*80}")
            self.stdout.write(f"ID: {asig.id}")
            self.stdout.write(f"Empleado: {asig.empleado_evaluado.nombre_completo}")
            self.stdout.write(f"Evaluador: {asig.evaluador.nombre_completo if asig.evaluador else 'Sin evaluador'}")
            self.stdout.write(f"Evaluación: {asig.evaluacion.nombre}")
            tipo = asig.evaluacion.tipo_evaluacion.codigo if asig.evaluacion.tipo_evaluacion else 'SIN TIPO'
            self.stdout.write(f"Tipo: {tipo}")
            self.stdout.write(f"ESTADO: {asig.estado}")
            self.stdout.write(f"Estado aprobación: {asig.estado_aprobacion}")
            self.stdout.write(f"Puntaje: {asig.puntaje_total}")
            self.stdout.write(f"Porcentaje: {asig.porcentaje_completado}%")
            self.stdout.write(f"Fecha creación: {asig.created_at}")

            # Buscar plan de mejora
            try:
                plan = PlanMejoraPredefinido.objects.get(asignacion_evaluacion=asig)
                self.stdout.write(self.style.SUCCESS(f"✓ TIENE PLAN (ID: {plan.id}, Estado: {plan.estado})"))
            except PlanMejoraPredefinido.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"✗ SIN PLAN DE MEJORA"))

        # Resumen por estado
        self.stdout.write(f"\n{'='*80}")
        self.stdout.write("RESUMEN POR ESTADO:")
        self.stdout.write(f"{'='*80}\n")

        from django.db.models import Count
        estados = AsignacionEvaluacion.objects.values('estado').annotate(
            total=Count('id')
        ).order_by('-total')

        for estado in estados:
            self.stdout.write(f"  {estado['estado']}: {estado['total']}")

        self.stdout.write(f"\n{'='*80}\n")
