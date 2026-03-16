from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.evaluations.models import EvaluacionCargo, AsignacionEvaluacion, EvaluacionDesempeño
from apps.employees.models import HistorialCargo
from django.utils import timezone
from datetime import timedelta

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

    # Calcular fecha de vencimiento (30 días por defecto)
    fecha_vencimiento = timezone.now() + timedelta(days=30)

    # Obtener usuario del sistema para asignado_por
    from apps.authentication.models import Usuario
    usuario_sistema = Usuario.objects.filter(is_superuser=True).first()

    if not usuario_sistema:
        # Si no hay usuario sistema, no crear asignaciones
        return

    # Evaluaciones asociadas al cargo QUE ESTÉN ACTIVAS
    # Solo asignar evaluaciones que hayan sido activadas desde el panel de admin
    evaluaciones = EvaluacionCargo.objects.filter(
        cargo=cargo,
        estado='activa'  # FILTRO CRUCIAL: Solo evaluaciones activadas
    ).select_related('evaluacion')

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
                evaluador=instance.jefe_directo,  # Asignar jefe directo como evaluador
                periodo_evaluacion=periodo_actual,
                fecha_vencimiento=fecha_vencimiento,
                estado='pendiente',
                es_autoevaluacion=False,
                asignado_por=usuario_sistema
            )
