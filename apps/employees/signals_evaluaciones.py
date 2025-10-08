from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.evaluations.models import EvaluacionCargo, AsignacionEvaluacion, EvaluacionDesempeño
from apps.employees.models import HistorialCargo
from django.utils import timezone

@receiver(post_save, sender=HistorialCargo)
def asignar_evaluaciones_por_cargo(sender, instance, created, **kwargs):
    """
    Asigna automáticamente evaluaciones de desempeño al empleado cuando se le asigna un cargo activo.
    """
    if not instance.activo:
        return
    empleado = instance.empleado
    cargo = instance.cargo
    periodo_actual = timezone.now().strftime('%Y')  # Puedes ajustar el periodo según tu lógica

    # Evaluaciones asociadas al cargo
    evaluaciones = EvaluacionCargo.objects.filter(cargo=cargo).select_related('evaluacion')
    for ec in evaluaciones:
        evaluacion = ec.evaluacion
        # Evitar duplicados
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
                es_autoevaluacion=False
            )
