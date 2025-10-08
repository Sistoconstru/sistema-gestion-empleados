from django.core.management.base import BaseCommand
from apps.evaluations.models import EvaluacionDesempeño, AsignacionEvaluacion
from apps.employees.models import Empleado
from django.utils import timezone

class Command(BaseCommand):
    help = 'Asigna evaluaciones generales (del SER) a todos los empleados activos para el periodo actual.'

    def handle(self, *args, **options):
        periodo_actual = timezone.now().strftime('%Y')  # Ajusta según tu lógica de periodos
        # Filtra evaluaciones generales (no asociadas a cargo)
        evaluaciones_generales = EvaluacionDesempeño.objects.filter(tipo_evaluacion__es_autoevaluacion=True, activa=True)
        empleados = Empleado.objects.filter(activo=True)
        total_asignadas = 0
        for evaluacion in evaluaciones_generales:
            for empleado in empleados:
                existe = AsignacionEvaluacion.objects.filter(
                    empleado_evaluado=empleado,
                    evaluacion=evaluacion,
                    periodo_evaluacion=periodo_actual
                ).exists()
                if not existe:
                    AsignacionEvaluacion.objects.create(
                        empleado_evaluado=empleado,
                        evaluacion=evaluacion,
                        periodo_evaluacion=periodo_actual,
                        estado='pendiente',
                        es_autoevaluacion=True
                    )
                    total_asignadas += 1
        self.stdout.write(self.style.SUCCESS(f'Asignaciones creadas: {total_asignadas}'))
