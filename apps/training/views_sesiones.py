"""Vistas para capacitaciones presenciales con sesiones programadas.

Cubre la Fase 2 del módulo:
- Catálogo de sesiones abiertas donde el empleado puede auto-inscribirse.
- Detalle de sesión con acción inscribirse.
- Listado "mis sesiones presenciales" para el empleado.
- Cancelación de la propia inscripción antes de iniciar la sesión.
"""

from datetime import date
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from apps.employees.models import Empleado
from .models import InscripcionCapacitacion, SesionCapacitacion

logger = logging.getLogger(__name__)


def _get_empleado(request):
    """Obtiene el empleado asociado al usuario o None (con mensaje)."""
    try:
        return Empleado.objects.get(usuario=request.user)
    except Empleado.DoesNotExist:
        return None


class SesionesAbiertasView(LoginRequiredMixin, ListView):
    """Catálogo público de sesiones presenciales abiertas a auto-inscripción."""

    model = SesionCapacitacion
    template_name = 'training/sesiones/lista_abiertas.html'
    context_object_name = 'sesiones'
    paginate_by = 12

    def get_queryset(self):
        hoy = date.today()
        qs = SesionCapacitacion.objects.filter(
            inscripcion_abierta=True,
            estado='programada',
        ).select_related('capacitacion', 'encargado').annotate(
            total_inscritos=Count('inscripciones'),
        )
        qs = qs.filter(
            Q(ventana_inscripcion_desde__isnull=True) | Q(ventana_inscripcion_desde__lte=hoy),
            Q(ventana_inscripcion_hasta__isnull=True) | Q(ventana_inscripcion_hasta__gte=hoy),
        )
        return qs.order_by('fecha_inicio', 'codigo')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empleado = _get_empleado(self.request)
        mis_sesiones_ids = set()
        if empleado:
            mis_sesiones_ids = set(
                InscripcionCapacitacion.objects.filter(
                    empleado=empleado,
                    sesion__isnull=False,
                ).values_list('sesion_id', flat=True)
            )
        for sesion in ctx['sesiones']:
            sesion.ya_inscrito = sesion.id in mis_sesiones_ids
            if sesion.cupo_maximo is None:
                sesion.disponibles = None
            else:
                sesion.disponibles = max(0, sesion.cupo_maximo - sesion.total_inscritos)
        ctx['hoy'] = date.today()
        return ctx


class SesionDetailView(LoginRequiredMixin, DetailView):
    model = SesionCapacitacion
    template_name = 'training/sesiones/detail.html'
    context_object_name = 'sesion'

    def get_queryset(self):
        return SesionCapacitacion.objects.select_related(
            'capacitacion', 'capacitacion__tipo', 'encargado',
        ).annotate(total_inscritos=Count('inscripciones'))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empleado = _get_empleado(self.request)
        sesion = ctx['sesion']
        inscripcion = None
        if empleado:
            inscripcion = InscripcionCapacitacion.objects.filter(
                empleado=empleado, sesion=sesion,
            ).first()
        ctx.update({
            'empleado': empleado,
            'mi_inscripcion': inscripcion,
            'puede_inscribirse': (
                empleado is not None
                and inscripcion is None
                and sesion.inscripcion_permitida_hoy()
            ),
            'disponibles': (
                None if sesion.cupo_maximo is None
                else max(0, sesion.cupo_maximo - sesion.total_inscritos)
            ),
            'es_encargado': empleado is not None and sesion.encargado_id == empleado.id,
            'hoy': date.today(),
        })
        return ctx


@login_required
@require_POST
def inscribirse_sesion(request, pk):
    """Auto-inscripción del empleado a una sesión abierta."""
    sesion = get_object_or_404(SesionCapacitacion, pk=pk)
    empleado = _get_empleado(request)
    if empleado is None:
        messages.error(request, 'Tu usuario no está vinculado a un empleado.')
        return redirect('training:sesiones_abiertas')

    if not sesion.inscripcion_permitida_hoy():
        messages.warning(request, 'Esta sesión no admite inscripciones en este momento.')
        return redirect('training:sesion_detail', pk=sesion.pk)

    try:
        with transaction.atomic():
            # Re-chequeo de cupo dentro de la transacción para reducir carreras.
            sesion_lock = SesionCapacitacion.objects.select_for_update().get(pk=sesion.pk)
            if sesion_lock.cupo_maximo is not None:
                inscritos = sesion_lock.inscripciones.count()
                if inscritos >= sesion_lock.cupo_maximo:
                    messages.warning(request, 'La sesión acaba de llenarse. Ya no hay cupo disponible.')
                    return redirect('training:sesion_detail', pk=sesion.pk)
            InscripcionCapacitacion.objects.create(
                empleado=empleado,
                capacitacion=sesion.capacitacion,
                sesion=sesion,
                estado='no_iniciado',
                obligatoria=False,
                inscrito_por=request.user,
            )
    except IntegrityError:
        messages.info(request, 'Ya estabas inscrito en esta sesión.')
    else:
        messages.success(
            request,
            f'Inscripción confirmada a "{sesion.capacitacion.nombre}" ({sesion.codigo}).',
        )
    return redirect('training:mis_sesiones')


@login_required
@require_POST
def cancelar_inscripcion_sesion(request, pk):
    """El empleado cancela su inscripción antes de que inicie la sesión."""
    inscripcion = get_object_or_404(
        InscripcionCapacitacion.objects.select_related('sesion', 'empleado', 'capacitacion'),
        pk=pk,
    )
    empleado = _get_empleado(request)
    if empleado is None or inscripcion.empleado_id != empleado.id:
        messages.error(request, 'No puedes cancelar una inscripción que no es tuya.')
        return redirect('training:mis_sesiones')

    sesion = inscripcion.sesion
    if sesion is None:
        messages.error(request, 'Esta inscripción no pertenece a una sesión presencial.')
        return redirect('training:mis_sesiones')

    if sesion.estado != 'programada' or sesion.fecha_inicio <= date.today():
        messages.warning(
            request,
            'Ya no puedes cancelar: la sesión ya inició o cambió de estado. '
            'Habla con tu encargado si necesitas darte de baja.',
        )
        return redirect('training:mis_sesiones')

    inscripcion.delete()
    messages.success(request, f'Se canceló tu inscripción a "{sesion.capacitacion.nombre}".')
    return redirect('training:mis_sesiones')


class MisSesionesView(LoginRequiredMixin, ListView):
    """Sesiones presenciales del empleado logueado (pasadas, en curso, futuras)."""

    model = InscripcionCapacitacion
    template_name = 'training/sesiones/mis_sesiones.html'
    context_object_name = 'inscripciones'
    paginate_by = 20

    def get_queryset(self):
        empleado = _get_empleado(self.request)
        if empleado is None:
            return InscripcionCapacitacion.objects.none()
        return InscripcionCapacitacion.objects.filter(
            empleado=empleado, sesion__isnull=False,
        ).select_related('sesion', 'sesion__capacitacion', 'sesion__encargado').order_by(
            '-sesion__fecha_inicio', 'sesion__codigo',
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoy = date.today()
        for insc in ctx['inscripciones']:
            s = insc.sesion
            insc.puede_cancelar = (
                s.estado == 'programada' and s.fecha_inicio > hoy
            )
        ctx['hoy'] = hoy
        return ctx
