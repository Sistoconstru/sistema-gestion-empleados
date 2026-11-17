"""Quién entra al módulo de transporte y qué ve.

El acceso no se apoya en el sistema de roles porque está sin poblar: los
roles Director, Coordinador y Administrador no tienen ningún usuario
asignado. El organigrama, en cambio, sí está completo y se mantiene solo,
así que el permiso se deriva de él:

- Conductor: su cargo activo está marcado como cargo de conductor.
- Administrador: es jefe directo de un conductor, o jefe de ese jefe. Eso
  da al coordinador y al director de cada conductor sin configurar nada, y
  se corrige solo cuando alguien cambia de equipo.
"""
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from apps.employees.models import Empleado, HistorialCargo, ESTADOS_NO_VIGENTES


def empleado_de(usuario):
    """El Empleado del usuario, o None si no tiene ficha."""
    if not usuario or not usuario.is_authenticated:
        return None
    return Empleado.objects.filter(usuario=usuario).first()


def conductores_vigentes():
    """Empleados vigentes cuyo cargo activo es de conductor."""
    return Empleado.objects.filter(
        historialcargo__activo=True,
        historialcargo__cargo__es_cargo_conductor=True,
    ).exclude(estado__codigo__in=ESTADOS_NO_VIGENTES).distinct()


def es_conductor(empleado):
    if not empleado:
        return False
    return HistorialCargo.objects.filter(
        empleado=empleado, activo=True, cargo__es_cargo_conductor=True
    ).exists()


def conductores_a_cargo(empleado):
    """Conductores de los que este empleado es jefe, directo o del jefe.

    Un conductor reporta a su coordinador y este a su director; ambos
    administran. Se resuelve mirando la cadena hacia arriba desde cada
    conductor, que es más barato que recorrerla hacia abajo y no depende de
    cuántos niveles existan por debajo.
    """
    if not empleado:
        return Empleado.objects.none()

    ids = []
    for h in HistorialCargo.objects.filter(
        empleado__in=conductores_vigentes(), activo=True
    ).select_related('jefe_directo'):
        jefe = h.jefe_directo
        if not jefe:
            continue
        if jefe.pk == empleado.pk:
            ids.append(h.empleado_id)
            continue
        # El jefe del jefe: el director del área.
        jefe_del_jefe = jefe.jefe_inmediato
        if jefe_del_jefe and jefe_del_jefe.pk == empleado.pk:
            ids.append(h.empleado_id)

    return Empleado.objects.filter(pk__in=ids)


def es_admin_transporte(usuario):
    """Administra la flota: staff, o jefe/director de algún conductor."""
    if not usuario or not usuario.is_authenticated:
        return False
    if usuario.is_staff:
        return True
    empleado = empleado_de(usuario)
    return conductores_a_cargo(empleado).exists()


def puede_entrar(usuario):
    """Cualquiera de los dos perfiles del módulo."""
    if es_admin_transporte(usuario):
        return True
    return es_conductor(empleado_de(usuario))


def vehiculos_visibles(usuario):
    """Los vehículos que este usuario puede ver.

    El conductor ve el suyo. El jefe y el director ven los de sus
    conductores. El staff ve todo.
    """
    from .models import Vehiculo

    if not usuario or not usuario.is_authenticated:
        return Vehiculo.objects.none()
    if usuario.is_staff:
        return Vehiculo.objects.all()

    empleado = empleado_de(usuario)
    if not empleado:
        return Vehiculo.objects.none()

    a_cargo = conductores_a_cargo(empleado)
    if a_cargo.exists():
        return Vehiculo.objects.filter(conductor__in=a_cargo)
    if es_conductor(empleado):
        return Vehiculo.objects.filter(conductor=empleado)
    return Vehiculo.objects.none()


def transporte_required(view_func):
    """Deja pasar a conductores y a quienes administran la flota."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not puede_entrar(request.user):
            messages.error(
                request,
                'El módulo de transporte es solo para conductores y sus jefes.'
            )
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


def admin_transporte_required(view_func):
    """Solo quienes administran la flota."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not es_admin_transporte(request.user):
            messages.error(
                request,
                'Solo el jefe o el director de los conductores puede hacer esto.'
            )
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped
