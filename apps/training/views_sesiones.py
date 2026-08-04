"""Vistas para capacitaciones presenciales con sesiones programadas.

Cubre la Fase 2 del módulo:
- Catálogo de sesiones abiertas donde el empleado puede auto-inscribirse.
- Detalle de sesión con acción inscribirse.
- Listado "mis sesiones presenciales" para el empleado.
- Cancelación de la propia inscripción antes de iniciar la sesión.
"""

from datetime import date, timedelta
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from apps.employees.models import Empleado
from .models import AsistenciaSesion, InscripcionCapacitacion, SesionCapacitacion

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


# =============================================================================
# Vistas para el encargado de una sesión (tomar asistencia)
# =============================================================================

class SesionesACargoView(LoginRequiredMixin, ListView):
    """Sesiones donde el usuario logueado es el encargado."""

    model = SesionCapacitacion
    template_name = 'training/sesiones/a_cargo.html'
    context_object_name = 'sesiones'
    paginate_by = 20

    def get_queryset(self):
        empleado = _get_empleado(self.request)
        if empleado is None:
            return SesionCapacitacion.objects.none()
        return SesionCapacitacion.objects.filter(
            encargado=empleado,
        ).select_related('capacitacion').annotate(
            total_inscritos=Count('inscripciones'),
        ).order_by('-fecha_inicio', 'codigo')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['empleado'] = _get_empleado(self.request)
        ctx['hoy'] = date.today()
        return ctx


def _dias_de_sesion(sesion):
    """Genera las fechas calendario que abarca la sesión."""
    dias = []
    d = sesion.fecha_inicio
    while d <= sesion.fecha_fin:
        dias.append(d)
        d += timedelta(days=1)
    return dias


def _guard_encargado(request, sesion):
    """Retorna (empleado, error_response) — error si no es encargado ni staff."""
    empleado = _get_empleado(request)
    if empleado is None:
        return None, HttpResponseForbidden('Tu usuario no está vinculado a un empleado.')
    es_encargado = sesion.encargado_id == empleado.id
    es_staff = request.user.is_staff or request.user.is_superuser
    if not (es_encargado or es_staff):
        return None, HttpResponseForbidden('Solo el encargado de la sesión puede tomar asistencia.')
    return empleado, None


@login_required
def tomar_asistencia(request, pk):
    """Matriz inscritos × días para que el encargado marque asistencia.

    GET: muestra la tabla.
    POST: recibe checkboxes con name="asis_<inscripcion_id>_<YYYY-MM-DD>" y
    sincroniza (create/update/delete implícito = no-marcado → asistio=False).
    """
    sesion = get_object_or_404(
        SesionCapacitacion.objects.select_related('capacitacion', 'encargado'),
        pk=pk,
    )
    empleado, err = _guard_encargado(request, sesion)
    if err is not None:
        return err

    dias = _dias_de_sesion(sesion)
    inscripciones = list(
        InscripcionCapacitacion.objects.filter(sesion=sesion)
        .select_related('empleado').order_by('empleado__apellidos', 'empleado__nombres')
    )

    if request.method == 'POST':
        # Índice existente {(inscripcion_id, fecha): AsistenciaSesion}
        existentes = {
            (a.inscripcion_id, a.fecha): a
            for a in AsistenciaSesion.objects.filter(
                inscripcion__in=inscripciones, fecha__in=dias,
            )
        }
        marcados = set()
        for key in request.POST:
            if not key.startswith('asis_'):
                continue
            try:
                _, insc_id, fecha_str = key.split('_', 2)
                fecha = date.fromisoformat(fecha_str)
            except ValueError:
                continue
            marcados.add((insc_id, fecha))

        creadas = actualizadas = descontadas = 0
        insc_ids = {str(i.pk) for i in inscripciones}
        with transaction.atomic():
            for insc in inscripciones:
                for dia in dias:
                    key = (insc.pk, dia)
                    debe_estar = (str(insc.pk), dia) in marcados
                    existente = existentes.get(key)
                    if existente is None and debe_estar:
                        AsistenciaSesion.objects.create(
                            inscripcion=insc, fecha=dia, asistio=True,
                            registrado_por=empleado,
                        )
                        creadas += 1
                    elif existente is not None and existente.asistio != debe_estar:
                        existente.asistio = debe_estar
                        existente.registrado_por = empleado
                        existente.save(update_fields=['asistio', 'registrado_por', 'fecha_registro'])
                        actualizadas += 1
                        if not debe_estar:
                            descontadas += 1

        total = creadas + actualizadas
        if total:
            partes = []
            if creadas:
                partes.append(f'{creadas} nueva(s)')
            if actualizadas:
                partes.append(f'{actualizadas} actualizada(s)')
            messages.success(request, 'Asistencia guardada: ' + ', '.join(partes) + '.')
        else:
            messages.info(request, 'No hubo cambios en la asistencia.')
        return redirect('training:tomar_asistencia', pk=sesion.pk)

    # GET: construir matriz para la plantilla
    asistencias_map = {
        (a.inscripcion_id, a.fecha): a
        for a in AsistenciaSesion.objects.filter(
            inscripcion__in=inscripciones, fecha__in=dias,
        )
    }
    filas = []
    for insc in inscripciones:
        celdas = []
        presentes = 0
        for dia in dias:
            asis = asistencias_map.get((insc.pk, dia))
            asistio = bool(asis and asis.asistio)
            if asistio:
                presentes += 1
            celdas.append({
                'fecha': dia,
                'name': f'asis_{insc.pk}_{dia.isoformat()}',
                'asistio': asistio,
                'observaciones': asis.observaciones if asis else '',
            })
        porcentaje = int(round(100 * presentes / len(dias))) if dias else 0
        filas.append({
            'inscripcion': insc,
            'celdas': celdas,
            'presentes': presentes,
            'porcentaje': porcentaje,
            'cumple_minimo': porcentaje >= sesion.porcentaje_asistencia_minimo,
        })

    return render(request, 'training/sesiones/tomar_asistencia.html', {
        'sesion': sesion,
        'dias': dias,
        'filas': filas,
        'hoy': date.today(),
        'total_dias': len(dias),
    })
