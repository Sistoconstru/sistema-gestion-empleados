"""Vistas del módulo de beneficios de retención en la fuente.

- Empleado: marcar `es_declarante`, listar sus trámites, crear/editar/cancelar
  un trámite propio.
- RRHH: bandeja de trámites por revisar, validar/rechazar/revocar, imprimir
  carta juramentada, marcar carta firmada.
"""
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.employees.models import Empleado

from .carta_juramentada import generar_carta_juramentada
from .models import (
    DependienteBeneficio, SoporteBeneficio, SoporteDependiente, TramiteBeneficio,
)
from .odoo_client import OdooBeneficioError, enviar_a_odoo
from .permisos import rrhh_required


# ============================================================================
# Helpers
# ============================================================================

def _empleado_de_usuario(usuario):
    try:
        return Empleado.objects.get(usuario=usuario)
    except Empleado.DoesNotExist:
        return None


def _validar_soporte_upload(archivo):
    """Rechaza archivos vacíos o mayores a 10 MB."""
    MAX = 10 * 1024 * 1024
    if not archivo:
        return None
    if archivo.size == 0:
        return 'archivo vacío'
    if archivo.size > MAX:
        return f'archivo {archivo.name} supera 10 MB'
    return None


# ============================================================================
# Empleado
# ============================================================================

@login_required
@require_POST
def marcar_declarante(request):
    """Al confirmar el modal '¿Eres declarante?' → guarda el flag y redirige."""
    emp = _empleado_de_usuario(request.user)
    if not emp:
        messages.error(request, 'Tu usuario no está vinculado a un empleado.')
        return redirect('employees:empleado_perfil')

    respuesta = (request.POST.get('respuesta') or '').strip()
    if respuesta == 'si':
        Empleado.objects.filter(pk=emp.pk).update(es_declarante=True)
        return redirect('beneficios_retencion:mis_tramites')
    # 'no' o cualquier otra respuesta → no habilita nada, vuelve al perfil
    messages.info(request,
                  'Si más adelante quedas como declarante, puedes activarlo desde tu perfil.')
    return redirect('employees:empleado_perfil')


@login_required
def mis_tramites(request):
    """Lista de trámites del propio empleado."""
    emp = _empleado_de_usuario(request.user)
    if not emp:
        messages.error(request, 'Tu usuario no está vinculado a un empleado.')
        return redirect('employees:empleado_perfil')

    if not emp.es_declarante:
        # Si intenta entrar sin haber confirmado, lo mandamos de vuelta al perfil.
        messages.info(request,
                      'Primero indica en tu perfil que eres declarante.')
        return redirect('employees:empleado_perfil')

    tramites = (TramiteBeneficio.objects
                .filter(empleado=emp)
                .order_by('-anio_aplicacion', 'tipo', '-fecha_creacion'))
    return render(request, 'beneficios_retencion/mis_tramites.html', {
        'tramites': tramites,
        'empleado': emp,
        'anio_actual': date.today().year,
        'tipos': TramiteBeneficio.TIPO_CHOICES,
    })


def _causal_sugerida(familiar):
    """Mapea un Familiar al código `causal` que mejor aplica para dependientes.

    - hijo con edad < 18 → hijo_menor_18
    - hijo 18-23 → hijo_18_23_estudiando (requiere certif. estudio)
    - hijo > 23 → hijo_mayor_23_dependiente (requiere certif. médico)
    - pareja → conyuge_dependiente
    - padre/madre/hermano/otro → familiar_dependiente
    """
    edad = familiar.edad
    tipo = familiar.tipo
    if tipo == 'hijo':
        if edad is None:
            return 'hijo_menor_18'
        if edad < 18:
            return 'hijo_menor_18'
        if edad <= 23:
            return 'hijo_18_23_estudiando'
        return 'hijo_mayor_23_dependiente'
    if tipo == 'pareja':
        return 'conyuge_dependiente'
    return 'familiar_dependiente'


@login_required
def familiares_json(request):
    """Devuelve los familiares activos del empleado logueado, para prellenar
    el formulario de dependientes."""
    emp = _empleado_de_usuario(request.user)
    if not emp or not emp.es_declarante:
        return JsonResponse({'familiares': []})

    familiares = emp.familiares.filter(activo=True).order_by('tipo', 'fecha_nacimiento')
    data = []
    for f in familiares:
        data.append({
            'id': str(f.pk),
            'nombres': f.nombre_completo,
            'numero_documento': f.numero_documento or '',
            'parentesco': f.get_tipo_display(),
            'tipo': f.tipo,
            'edad': f.edad,
            'causal_sugerida': _causal_sugerida(f),
        })
    return JsonResponse({'familiares': data})


@login_required
def nuevo_tramite(request):
    """Formulario para cargar un trámite nuevo."""
    emp = _empleado_de_usuario(request.user)
    if not emp or not emp.es_declarante:
        return redirect('employees:empleado_perfil')

    if request.method == 'POST':
        return _procesar_nuevo_tramite(request, emp)

    return render(request, 'beneficios_retencion/nuevo_tramite.html', {
        'empleado': emp,
        'tipos': TramiteBeneficio.TIPO_CHOICES,
        'periodicidades': TramiteBeneficio.PERIODICIDAD_CHOICES,
        'causales': DependienteBeneficio.CAUSAL_CHOICES,
        'anio_actual': date.today().year,
    })


def _procesar_nuevo_tramite(request, emp):
    tipo = (request.POST.get('tipo') or '').strip()
    tipos_validos = {c for c, _ in TramiteBeneficio.TIPO_CHOICES}
    if tipo not in tipos_validos:
        messages.error(request, 'Tipo de beneficio inválido.')
        return redirect('beneficios_retencion:nuevo_tramite')

    try:
        anio = int(request.POST.get('anio_aplicacion') or 0)
    except (TypeError, ValueError):
        messages.error(request, 'Año de aplicación inválido.')
        return redirect('beneficios_retencion:nuevo_tramite')
    anio_actual = date.today().year
    if anio not in (anio_actual - 1, anio_actual, anio_actual + 1):
        messages.error(request, 'Año de aplicación fuera de rango.')
        return redirect('beneficios_retencion:nuevo_tramite')

    # Periodo del certificado según tipo
    if tipo == 'dependientes':
        periodo = anio
    else:
        periodo = anio - 1

    valor = None
    periodicidad = ''
    if tipo != 'dependientes':
        try:
            valor_raw = (request.POST.get('valor') or '').replace('.', '').replace(',', '.')
            valor = float(valor_raw) if valor_raw else None
        except ValueError:
            messages.error(request, 'Valor inválido.')
            return redirect('beneficios_retencion:nuevo_tramite')
        if not valor or valor <= 0:
            messages.error(request, 'El valor debe ser mayor a cero.')
            return redirect('beneficios_retencion:nuevo_tramite')
        periodicidad = (request.POST.get('periodicidad') or 'anual').strip()
        if periodicidad not in ('anual', 'mensual'):
            messages.error(request, 'Periodicidad inválida.')
            return redirect('beneficios_retencion:nuevo_tramite')

    observacion = (request.POST.get('observacion') or '').strip()

    # Soportes principales
    archivos_principales = request.FILES.getlist('soportes')
    if not archivos_principales:
        messages.error(request, 'Debes adjuntar al menos un soporte.')
        return redirect('beneficios_retencion:nuevo_tramite')
    for a in archivos_principales:
        err = _validar_soporte_upload(a)
        if err:
            messages.error(request, err)
            return redirect('beneficios_retencion:nuevo_tramite')

    # Dependientes (solo si aplica)
    dependientes_data = []
    if tipo == 'dependientes':
        nombres_list = request.POST.getlist('dep_nombres[]')
        docs_list = request.POST.getlist('dep_documento[]')
        parentescos = request.POST.getlist('dep_parentesco[]')
        causales_list = request.POST.getlist('dep_causal[]')
        causales_validas = {c for c, _ in DependienteBeneficio.CAUSAL_CHOICES}
        for i, nombre in enumerate(nombres_list):
            nombre = (nombre or '').strip()
            if not nombre:
                continue
            causal = (causales_list[i] if i < len(causales_list) else '').strip()
            if causal not in causales_validas:
                messages.error(request, f'Dependiente {nombre}: causal inválida.')
                return redirect('beneficios_retencion:nuevo_tramite')
            archivos_dep = request.FILES.getlist(f'dep_soportes_{i}')
            if not archivos_dep:
                messages.error(request,
                               f'Dependiente {nombre}: adjunta al menos un soporte.')
                return redirect('beneficios_retencion:nuevo_tramite')
            for a in archivos_dep:
                err = _validar_soporte_upload(a)
                if err:
                    messages.error(request, err)
                    return redirect('beneficios_retencion:nuevo_tramite')
            dependientes_data.append({
                'nombres': nombre,
                'numero_documento': (docs_list[i] if i < len(docs_list) else '').strip(),
                'parentesco': (parentescos[i] if i < len(parentescos) else '').strip(),
                'causal': causal,
                'archivos': archivos_dep,
            })
        if not dependientes_data:
            messages.error(request, 'Agrega al menos un dependiente.')
            return redirect('beneficios_retencion:nuevo_tramite')

    with transaction.atomic():
        tramite = TramiteBeneficio.objects.create(
            empleado=emp, tipo=tipo,
            anio_aplicacion=anio, periodo_certificado=periodo,
            valor=valor, periodicidad=periodicidad,
            observacion_empleado=observacion, estado='pendiente_rrhh',
        )
        for a in archivos_principales:
            SoporteBeneficio.objects.create(
                tramite=tramite, archivo=a,
                nombre_original=a.name, tipo_mime=a.content_type or '',
            )
        for d in dependientes_data:
            dep = DependienteBeneficio.objects.create(
                tramite=tramite,
                nombres=d['nombres'],
                numero_documento=d['numero_documento'],
                parentesco=d['parentesco'],
                causal=d['causal'],
            )
            for a in d['archivos']:
                SoporteDependiente.objects.create(
                    dependiente=dep, archivo=a,
                    nombre_original=a.name, tipo_mime=a.content_type or '',
                )

    messages.success(request, 'Trámite enviado. RRHH lo revisará y te avisará.')
    return redirect('beneficios_retencion:mis_tramites')


@login_required
@require_POST
def cancelar_tramite(request, pk):
    """El empleado retira un trámite pendiente (aún no revisado por RRHH)."""
    emp = _empleado_de_usuario(request.user)
    if not emp:
        return redirect('employees:empleado_perfil')
    t = get_object_or_404(TramiteBeneficio, pk=pk, empleado=emp)
    if t.estado != 'pendiente_rrhh':
        messages.warning(request,
                         'Solo puedes cancelar trámites que aún están pendientes de RRHH.')
        return redirect('beneficios_retencion:mis_tramites')
    t.delete()
    messages.success(request, 'Trámite cancelado.')
    return redirect('beneficios_retencion:mis_tramites')


# ============================================================================
# RRHH
# ============================================================================

@rrhh_required
def bandeja_rrhh(request):
    """Bandeja de trámites por revisar + historial."""
    estado_filtro = (request.GET.get('estado') or 'pendiente_rrhh').strip()
    empleado_q = (request.GET.get('q') or '').strip()

    qs = TramiteBeneficio.objects.select_related('empleado', 'validado_por')
    if estado_filtro and estado_filtro != 'todos':
        qs = qs.filter(estado=estado_filtro)
    if empleado_q:
        from django.db.models import Q
        qs = qs.filter(
            Q(empleado__nombres__icontains=empleado_q) |
            Q(empleado__apellidos__icontains=empleado_q) |
            Q(empleado__numero_documento__icontains=empleado_q)
        )
    qs = qs.order_by('-fecha_creacion')[:200]

    return render(request, 'beneficios_retencion/bandeja_rrhh.html', {
        'tramites': qs,
        'estado_choices': TramiteBeneficio.ESTADO_CHOICES,
        'estado_filtro': estado_filtro,
        'empleado_q': empleado_q,
    })


@rrhh_required
def detalle_rrhh(request, pk):
    """Detalle de un trámite con acciones para RRHH."""
    tramite = get_object_or_404(
        TramiteBeneficio.objects
        .select_related('empleado', 'validado_por')
        .prefetch_related('soportes', 'dependientes__soportes'),
        pk=pk,
    )
    return render(request, 'beneficios_retencion/detalle_rrhh.html', {
        'tramite': tramite,
    })


def _notificar_empleado(tramite, codigo):
    """Crea notificación in-app para el empleado sobre el trámite."""
    from apps.notifications.models import Notificacion, TipoNotificacion

    usuario = getattr(tramite.empleado, 'usuario', None)
    if not usuario:
        return
    tipo = TipoNotificacion.objects.filter(codigo=codigo, activo=True).first()
    if not tipo:
        return
    datos = {
        'tipo': tramite.get_tipo_display(),
        'anio_aplicacion': tramite.anio_aplicacion,
        'motivo': tramite.observacion_rrhh or '—',
    }
    Notificacion.objects.create(
        usuario=usuario, tipo_notificacion=tipo,
        titulo=tipo.plantilla_titulo.format(**datos),
        mensaje=tipo.plantilla_mensaje.format(**datos),
        datos_adicionales={'tramite_id': str(tramite.pk), **datos},
    )


@rrhh_required
@require_POST
def validar_tramite(request, pk):
    """RRHH valida → intenta enviar a Odoo y notifica al empleado."""
    tramite = get_object_or_404(TramiteBeneficio, pk=pk)
    if tramite.estado not in ('pendiente_rrhh', 'error_envio_odoo', 'rechazado'):
        messages.warning(request, 'Este trámite no está en un estado que permita validar.')
        return redirect('beneficios_retencion:detalle_rrhh', pk=pk)

    tramite.validado_por = request.user
    tramite.validado_el = date.today()
    tramite.observacion_rrhh = (request.POST.get('observacion') or '').strip()
    tramite.estado = 'validado'
    tramite.save(update_fields=[
        'validado_por', 'validado_el', 'observacion_rrhh', 'estado',
        'fecha_actualizacion',
    ])

    try:
        enviar_a_odoo(tramite, estado='validado')
    except OdooBeneficioError as exc:
        tramite.estado = 'error_envio_odoo'
        tramite.ultimo_error_odoo = str(exc)[:1000]
        tramite.save(update_fields=['estado', 'ultimo_error_odoo', 'fecha_actualizacion'])
        messages.warning(
            request,
            f'Trámite marcado como validado, pero falló el envío a Odoo: {exc}. '
            'Podés reintentar desde el detalle.',
        )
        return redirect('beneficios_retencion:detalle_rrhh', pk=pk)

    _notificar_empleado(tramite, 'beneficio_ret_validado')
    messages.success(request,
                     'Trámite validado y enviado a Odoo. Notificamos al empleado para que firme la carta.')
    return redirect('beneficios_retencion:detalle_rrhh', pk=pk)


@rrhh_required
@require_POST
def rechazar_tramite(request, pk):
    """RRHH rechaza — queda en SIGHU con observación. NO se envía a Odoo."""
    tramite = get_object_or_404(TramiteBeneficio, pk=pk)
    if tramite.estado not in ('pendiente_rrhh', 'error_envio_odoo'):
        messages.warning(request, 'Este trámite no puede rechazarse en su estado actual.')
        return redirect('beneficios_retencion:detalle_rrhh', pk=pk)

    observacion = (request.POST.get('observacion') or '').strip()
    if not observacion:
        messages.error(request, 'Debes indicar el motivo del rechazo.')
        return redirect('beneficios_retencion:detalle_rrhh', pk=pk)

    tramite.estado = 'rechazado'
    tramite.observacion_rrhh = observacion
    tramite.validado_por = request.user
    tramite.validado_el = date.today()
    tramite.save(update_fields=[
        'estado', 'observacion_rrhh', 'validado_por', 'validado_el',
        'fecha_actualizacion',
    ])
    _notificar_empleado(tramite, 'beneficio_ret_rechazado')
    messages.success(request, 'Trámite rechazado. Se notificó al empleado.')
    return redirect('beneficios_retencion:detalle_rrhh', pk=pk)


@rrhh_required
@require_POST
def revocar_tramite(request, pk):
    """RRHH revoca un beneficio ya validado — avisa a Odoo con estado 'revocado'."""
    tramite = get_object_or_404(TramiteBeneficio, pk=pk)
    if tramite.estado != 'validado':
        messages.warning(request, 'Solo se pueden revocar trámites validados.')
        return redirect('beneficios_retencion:detalle_rrhh', pk=pk)

    observacion = (request.POST.get('observacion') or '').strip()
    if not observacion:
        messages.error(request, 'Debes indicar el motivo de la revocación.')
        return redirect('beneficios_retencion:detalle_rrhh', pk=pk)

    tramite.observacion_rrhh = observacion
    tramite.validado_por = request.user
    tramite.validado_el = date.today()
    tramite.save(update_fields=[
        'observacion_rrhh', 'validado_por', 'validado_el', 'fecha_actualizacion',
    ])

    try:
        enviar_a_odoo(tramite, estado='revocado')
    except OdooBeneficioError as exc:
        messages.error(request,
                       f'No se pudo notificar la revocación a Odoo: {exc}. Reintentá.')
        return redirect('beneficios_retencion:detalle_rrhh', pk=pk)

    tramite.estado = 'revocado'
    tramite.save(update_fields=['estado', 'fecha_actualizacion'])
    _notificar_empleado(tramite, 'beneficio_ret_revocado')
    messages.success(request, 'Beneficio revocado y notificado a Odoo.')
    return redirect('beneficios_retencion:detalle_rrhh', pk=pk)


@rrhh_required
@require_POST
def reintentar_envio_odoo(request, pk):
    """Reintento manual cuando quedó en estado_envio_odoo."""
    tramite = get_object_or_404(TramiteBeneficio, pk=pk)
    if tramite.estado not in ('validado', 'error_envio_odoo'):
        messages.warning(request, 'Este trámite no requiere reintento.')
        return redirect('beneficios_retencion:detalle_rrhh', pk=pk)
    try:
        enviar_a_odoo(tramite, estado='validado')
    except OdooBeneficioError as exc:
        tramite.estado = 'error_envio_odoo'
        tramite.ultimo_error_odoo = str(exc)[:1000]
        tramite.save(update_fields=['estado', 'ultimo_error_odoo', 'fecha_actualizacion'])
        messages.error(request, f'Odoo devolvió error: {exc}')
        return redirect('beneficios_retencion:detalle_rrhh', pk=pk)
    tramite.estado = 'validado'
    tramite.save(update_fields=['estado', 'fecha_actualizacion'])
    _notificar_empleado(tramite, 'beneficio_ret_validado')
    messages.success(request, 'Envío a Odoo exitoso.')
    return redirect('beneficios_retencion:detalle_rrhh', pk=pk)


@rrhh_required
def descargar_carta(request, pk):
    """Genera el PDF de la carta juramentada del trámite. Solo trámites validados."""
    tramite = get_object_or_404(TramiteBeneficio, pk=pk)
    if tramite.estado not in ('validado', 'revocado'):
        messages.warning(request,
                         'La carta juramentada solo se genera para trámites validados.')
        return redirect('beneficios_retencion:detalle_rrhh', pk=pk)

    if not tramite.carta_generada_el:
        TramiteBeneficio.objects.filter(pk=tramite.pk).update(
            carta_generada_el=timezone.now(),
        )

    pdf = generar_carta_juramentada(tramite)
    filename = (f'carta_juramentada_{tramite.empleado.numero_documento}_'
                f'{tramite.tipo}_{tramite.anio_aplicacion}.pdf')
    resp = HttpResponse(pdf, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


@rrhh_required
@require_POST
def marcar_carta_firmada(request, pk):
    """RRHH marca que el empleado firmó físicamente la carta."""
    tramite = get_object_or_404(TramiteBeneficio, pk=pk)
    TramiteBeneficio.objects.filter(pk=pk).update(
        carta_firmada=True, carta_firmada_el=timezone.now(),
    )
    messages.success(request, 'Carta marcada como firmada.')
    return redirect('beneficios_retencion:detalle_rrhh', pk=pk)
