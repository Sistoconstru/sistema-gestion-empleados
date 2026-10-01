"""Permisos del módulo beneficios de retención.

Usa el sistema de Roles propio de SIGHU (apps.authentication.models.UsuarioRol).
Permite entrada a usuarios con rol RRHH o ADMIN, o superusers (fallback).
"""
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


ROLES_PERMITIDOS = {'RRHH', 'ADMIN'}


def _usuario_puede_gestionar(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        from apps.authentication.models import UsuarioRol
        return UsuarioRol.objects.filter(
            usuario=user, rol__codigo__in=ROLES_PERMITIDOS, activo=True,
        ).exists()
    except Exception:
        # Fallback — si el modelo cambia o falla, respetamos is_staff.
        return bool(getattr(user, 'is_staff', False))


def rrhh_required(view_func):
    """Permite solo a usuarios con rol RRHH, ADMIN o superusers."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not _usuario_puede_gestionar(request.user):
            messages.error(
                request,
                'Esta sección es de uso exclusivo de RRHH.'
            )
            return redirect('employees:empleado_perfil')
        return view_func(request, *args, **kwargs)
    return _wrapped
