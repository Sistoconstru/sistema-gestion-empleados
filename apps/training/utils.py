# apps/training/utils.py

def asignar_capacitaciones_por_cargo(empleado):
    """Asignar automáticamente capacitaciones obligatorias según cargo"""
    from .models import CapacitacionCargo, InscripcionCapacitacion
    from datetime import date, timedelta
    
    # Obtener cargo actual
    historial_actual = empleado.historialcargo_set.filter(activo=True).first()
    if not historial_actual:
        return
    
    cargo = historial_actual.cargo
    
    # Obtener capacitaciones del cargo
    capacitaciones_cargo = CapacitacionCargo.objects.filter(
        cargo=cargo,
        capacitacion__activa=True
    ).select_related('capacitacion')
    
    inscripciones_creadas = 0
    
    for cap_cargo in capacitaciones_cargo:
        capacitacion = cap_cargo.capacitacion
        
        # Verificar si ya está inscrito
        if InscripcionCapacitacion.objects.filter(
            empleado=empleado,
            capacitacion=capacitacion
        ).exists():
            continue
        
        # Calcular fecha límite
        fecha_limite = date.today() + timedelta(days=cap_cargo.dias_plazo_completar)
        
        # Crear inscripción
        InscripcionCapacitacion.objects.create(
            empleado=empleado,
            capacitacion=capacitacion,
            fecha_limite=fecha_limite,
            obligatoria=cap_cargo.obligatoria,
            aprobada_supervisor=True,
            inscrito_por_id=1  # Sistema/Admin
        )
        
        inscripciones_creadas += 1
    
    return inscripciones_creadas