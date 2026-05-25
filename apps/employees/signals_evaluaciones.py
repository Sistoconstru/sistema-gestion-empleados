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

        # VALIDACIÓN CRÍTICA: Verificar compatibilidad entre estado del empleado y tipo de evaluación
        # No asignar evaluaciones de periodo de prueba a empleados activos, ni viceversa
        estado_empleado = empleado.estado.codigo if empleado.estado else None
        tipo_evaluacion = evaluacion.tipo_evaluacion.codigo if evaluacion.tipo_evaluacion else None

        if estado_empleado and tipo_evaluacion:
            es_periodo_prueba = tipo_evaluacion == 'PERIODO_PRUEBA'
            empleado_en_prueba = estado_empleado == 'p-prue'

            # Validar reglas de negocio
            if es_periodo_prueba and not empleado_en_prueba:
                # Intentando asignar evaluación de periodo de prueba a empleado activo - OMITIR
                print(f"[SIGNAL] OMITIDO: No se puede asignar evaluación de periodo de prueba a {empleado.nombre_completo} (no está en periodo de prueba)")
                continue
            elif not es_periodo_prueba and empleado_en_prueba:
                # Intentando asignar evaluación de desempeño a empleado en periodo de prueba - OMITIR
                print(f"[SIGNAL] OMITIDO: No se puede asignar evaluación de desempeño a {empleado.nombre_completo} (está en periodo de prueba)")
                continue

            # VALIDACIÓN DE ANTIGÜEDAD: Para evaluaciones de desempeño (NO periodo de prueba),
            # el empleado debe tener al menos 5 meses de antigüedad
            # Esto evita asignar evaluaciones de desempeño a empleados recién pasados a activos
            if not es_periodo_prueba and empleado.fecha_ingreso:
                MESES_MINIMOS_DESEMPEÑO = 5
                fecha_actual = timezone.now().date()
                antigüedad_dias = (fecha_actual - empleado.fecha_ingreso).days
                antigüedad_meses = antigüedad_dias / 30.44  # Promedio de días por mes

                if antigüedad_meses < MESES_MINIMOS_DESEMPEÑO:
                    print(f"[SIGNAL] OMITIDO: {empleado.nombre_completo} no tiene antigüedad suficiente "
                          f"para evaluación de desempeño ({antigüedad_meses:.1f} meses, mínimo: {MESES_MINIMOS_DESEMPEÑO} meses). "
                          f"Fecha ingreso: {empleado.fecha_ingreso}")
                    continue

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
