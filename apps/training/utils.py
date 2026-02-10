# apps/training/utils.py

def asignar_capacitaciones_por_cargo(empleado, usuario):
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
            inscrito_por=usuario  # Ahora se pasa el usuario válido
        )
        
        inscripciones_creadas += 1

    return inscripciones_creadas


def get_certificado_externo_upload_path(instance, filename):
    """
    Genera ruta de subida para certificados externos
    Estructura: capacitaciones/certificados/{numero_documento}/externo/{codigo_capacitacion}_{filename}
    """
    import os
    from django.utils.text import get_valid_filename

    empleado_doc = instance.empleado.numero_documento
    capacitacion_codigo = instance.capacitacion.codigo

    # Limpiar el nombre del archivo
    filename = get_valid_filename(filename)
    name, ext = os.path.splitext(filename)

    # Crear nombre único con código de capacitación
    new_filename = f"{capacitacion_codigo}_{name}{ext}"

    return f'capacitaciones/certificados/{empleado_doc}/externo/{new_filename}'


def get_certificado_generado_upload_path(instance, filename):
    """
    Genera ruta de subida para certificados generados automáticamente
    Estructura: capacitaciones/certificados/{numero_documento}/generado/{numero_certificado}.pdf
    """
    import os
    from django.utils.text import get_valid_filename

    empleado_doc = instance.empleado.numero_documento

    # Usar número de certificado si existe, sino usar código de capacitación
    if instance.numero_certificado:
        base_name = instance.numero_certificado
    else:
        base_name = f"{instance.capacitacion.codigo}_{instance.id}"

    # Limpiar el nombre del archivo
    filename = get_valid_filename(filename)
    ext = os.path.splitext(filename)[1] or '.pdf'

    new_filename = f"{base_name}{ext}"

    return f'capacitaciones/certificados/{empleado_doc}/generado/{new_filename}'


def get_plantilla_logo_upload_path(instance, filename):
    """
    Genera ruta de subida para logos de plantillas de certificados
    Estructura: capacitaciones/plantillas/{codigo_capacitacion}/logo_{filename}
    """
    import os
    from django.utils.text import get_valid_filename

    capacitacion_codigo = instance.capacitacion.codigo
    filename = get_valid_filename(filename)

    return f'capacitaciones/plantillas/{capacitacion_codigo}/logo_{filename}'


def get_plantilla_firma_upload_path(instance, filename):
    """
    Genera ruta de subida para firmas de plantillas de certificados
    Estructura: capacitaciones/plantillas/{codigo_capacitacion}/firma_{filename}
    """
    import os
    from django.utils.text import get_valid_filename

    capacitacion_codigo = instance.capacitacion.codigo
    filename = get_valid_filename(filename)

    return f'capacitaciones/plantillas/{capacitacion_codigo}/firma_{filename}'


def get_plantilla_firma_rrhh_upload_path(instance, filename):
    """
    Genera ruta de subida para firma de RRHH en plantillas de certificados
    Estructura: capacitaciones/plantillas/{codigo_capacitacion}/firma_rrhh_{filename}
    """
    import os
    from django.utils.text import get_valid_filename

    capacitacion_codigo = instance.capacitacion.codigo
    filename = get_valid_filename(filename)

    return f'capacitaciones/plantillas/{capacitacion_codigo}/firma_rrhh_{filename}'


def get_plantilla_fondo_upload_path(instance, filename):
    """
    Genera ruta de subida para imagen de fondo de plantillas de certificados
    Estructura: capacitaciones/plantillas/{codigo_capacitacion}/fondo_{filename}
    """
    import os
    from django.utils.text import get_valid_filename

    capacitacion_codigo = instance.capacitacion.codigo
    filename = get_valid_filename(filename)

    return f'capacitaciones/plantillas/{capacitacion_codigo}/fondo_{filename}'