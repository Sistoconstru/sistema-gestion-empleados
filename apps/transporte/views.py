"""Flota: ver los vehículos y asignarles conductor.

La asignación es lo que más se usa y por eso vive aquí y no en el admin de
Django: la hace el coordinador, no un técnico. Al guardar se le avisa a
Odoo, que es el dueño del maestro; si Odoo no contesta, el cambio queda
registrado y se reintenta solo.
"""
import logging
from datetime import date
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.employees.models import Empleado

logger = logging.getLogger(__name__)


def _miles(n):
    """125487 → "125.487", como se escriben los números en Colombia."""
    return f'{n:,}'.replace(',', '.')


def _registrar_rechazo(servicio, error, que):
    """Deja el rechazo en el log, con el nivel que corresponde.

    Un 409 es parte de la operación: el coordinador movió algo. Un 400
    significa que SIGHU mandó un dato que no sirve, y eso es un error
    nuestro que hay que ir a mirar, no una situación normal.
    """
    identificador = servicio.ref or servicio.odoo_id
    registrar = logger.error if error.es_culpa_nuestra else logger.warning
    registrar('Odoo rechazó %s de %s (%s): %s',
              que, identificador, error.status_code, error.motivo)


def _con_punto(texto):
    """Cierra la frase si Odoo no la cerró, para que no se peguen dos."""
    texto = (texto or '').strip()
    if texto and texto[-1] not in '.!?:;':
        return texto + '.'
    return texto


def _de(que):
    """"el cierre" → "del cierre"; "la salida" → "de la salida"."""
    return f'del {que[3:]}' if que.startswith('el ') else f'de {que}'


def _mensaje_de_rechazo(error, que, identificador):
    """Lo que ve el conductor. Depende de si puede hacer algo o no.

    `que` llega con su artículo —"la salida", "el cierre"— porque el
    género cambia y una frase mal concordada se nota.
    """
    motivo = _con_punto(error.motivo)
    if error.es_culpa_nuestra:
        return (f'Odoo rechazó el dato {_de(que)} de {identificador}: '
                f'{motivo} Quedó registrado acá; avísale a sistemas, '
                f'no es algo que puedas corregir tú.')
    return f'Odoo no aceptó {que} de {identificador}: {motivo}'


def _decimal_o_none(texto):
    """Un decimal del formulario, aceptando coma o punto. None si no vale.

    El conductor escribe "0,519" o "0.519" según el teclado del celular;
    las dos quieren decir lo mismo.
    """
    texto = (texto or '').strip().replace(',', '.')
    if not texto:
        return None
    try:
        valor = Decimal(texto)
    except (InvalidOperation, ValueError):
        return None
    return valor if valor >= 0 else None

from .forms import (
    DocumentoVehiculoForm, GastoAdminForm, GastoVehiculoForm,
    RevisionGastoForm,
)
from .models import (
    CierreGastos, DocumentoVehiculo, GastoVehiculo, ServicioIniciado,
    Vehiculo,
)
from .odoo_client import (
    OdooConflictoError, OdooTransporteError, avisar_servicio_finalizado,
    avisar_servicio_iniciado,
)
from .permisos import (
    admin_transporte_required, conductores_a_cargo, conductores_vigentes,
    es_admin_transporte, es_conductor, empleado_de, gastos_visibles,
    transporte_required, vehiculos_visibles,
)
from .contabilidad import (
    ENVIADO, RECHAZADO, TIMEOUT_PANTALLA, enviar as enviar_cierre_a_odoo,
    enviar_anulacion as enviar_anulacion_a_odoo,
)
from .cuentas import (
    CierreImposible, anular_cierre, cerrar_cuenta, cuentas_abiertas,
)
from .licencias import estado_licencia, estados_de
from .servicios import servicios_visibles


@login_required
@transporte_required
def flota(request):
    """Listado de vehículos con el estado de sus documentos."""
    vehiculos = list(
        vehiculos_visibles(request.user)
        .select_related('conductor')
        .prefetch_related(Prefetch(
            'documentos',
            queryset=DocumentoVehiculo.objects.order_by('tipo', '-fecha_vencimiento'),
        ))
        .order_by('-activo', 'placa')
    )

    empleado = empleado_de(request.user)
    es_admin = es_admin_transporte(request.user)

    # Los conductores que este usuario puede asignar. El staff ve todos los
    # que tengan cargo de conductor; un coordinador, solo los suyos.
    if es_admin:
        if request.user.is_staff:
            asignables = conductores_vigentes()
        else:
            asignables = conductores_a_cargo(empleado)
    else:
        asignables = Empleado.objects.none()

    # Resumen para el encabezado: lo que exige atención.
    vencidos = por_vencer = 0
    for v in vehiculos:
        for d in v.documentos_vigentes():
            if not d.aplica:
                continue
            if d.esta_vencido:
                vencidos += 1
            elif d.por_vencer:
                por_vencer += 1

    # La licencia del conductor se mira acá, que es donde se le entrega el
    # camión. Una consulta para toda la flota, no una por vehículo.
    conductores_en_pantalla = [v.conductor for v in vehiculos if v.conductor_id]
    estados_licencia = estados_de(conductores_en_pantalla)
    for v in vehiculos:
        v.licencia = estados_licencia.get(v.conductor_id)
    sin_licencia_al_dia = sum(
        1 for v in vehiculos
        if v.activo and v.licencia and not v.licencia['al_dia'])

    return render(request, 'transporte/flota.html', {
        'vehiculos': vehiculos,
        'hoy': timezone.localdate(),
        'es_admin': es_admin,
        'asignables': asignables.order_by('apellidos', 'nombres'),
        'total_vencidos': vencidos,
        'total_por_vencer': por_vencer,
        'sin_conductor': sum(1 for v in vehiculos if v.activo and not v.conductor_id),
        'sin_licencia_al_dia': sin_licencia_al_dia,
        'es_solo_conductor': es_conductor(empleado) and not es_admin,
    })


@login_required
@admin_transporte_required
@require_POST
def asignar_conductor(request, vehiculo_id):
    """Asigna, cambia o quita el conductor de un vehículo.

    El aviso a Odoo lo dispara el signal al guardar. Aquí solo se traduce el
    resultado a un mensaje que explique qué pasó, porque "se guardó pero
    Odoo no se enteró todavía" no es lo mismo que "se guardó".
    """
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)

    if vehiculo not in vehiculos_visibles(request.user):
        messages.error(request, 'Ese vehículo no es de tu flota.')
        return redirect('transporte:flota')

    if not vehiculo.activo:
        messages.error(
            request,
            f'{vehiculo.placa} está dado de baja en Odoo, no admite conductor.')
        return redirect('transporte:flota')

    conductor_id = (request.POST.get('conductor') or '').strip()
    desde_raw = (request.POST.get('desde') or '').strip()
    try:
        desde = date.fromisoformat(desde_raw) if desde_raw else timezone.localdate()
    except ValueError:
        messages.error(request, 'La fecha de inicio no es válida.')
        return redirect('transporte:flota')

    if desde > timezone.localdate():
        messages.error(request, 'La asignación no puede empezar en el futuro.')
        return redirect('transporte:flota')

    anterior = vehiculo.conductor

    if not conductor_id:
        if not anterior:
            messages.info(request, f'{vehiculo.placa} ya estaba sin conductor.')
            return redirect('transporte:flota')
        vehiculo.conductor = None
        vehiculo.save()
        messages.success(
            request,
            f'{vehiculo.placa} queda sin conductor. '
            f'{anterior.nombre_completo} ya no lo tiene asignado.')
        return redirect('transporte:flota')

    # Solo se puede asignar a alguien que este usuario administre.
    if request.user.is_staff:
        permitidos = conductores_vigentes()
    else:
        permitidos = conductores_a_cargo(empleado_de(request.user))

    nuevo = permitidos.filter(pk=conductor_id).first()
    if not nuevo:
        messages.error(
            request, 'Ese conductor no está entre los que puedes asignar.')
        return redirect('transporte:flota')

    if anterior and anterior.pk == nuevo.pk:
        messages.info(
            request, f'{nuevo.nombre_completo} ya conducía {vehiculo.placa}.')
        return redirect('transporte:flota')

    # Un conductor no puede tener dos vehículos a la vez: Odoo cierra la
    # asignación anterior, así que conviene que SIGHU muestre lo mismo.
    otro = Vehiculo.objects.filter(
        conductor=nuevo, activo=True).exclude(pk=vehiculo.pk).first()

    vehiculo.conductor = nuevo
    vehiculo.asignacion_desde = desde
    vehiculo.save()
    vehiculo.refresh_from_db()

    if otro:
        otro.conductor = None
        otro.save()
        messages.info(
            request,
            f'{nuevo.nombre_completo} dejó de tener asignado {otro.placa}.')

    if vehiculo.asignacion_sincronizada:
        messages.success(
            request,
            f'{nuevo.nombre_completo} queda asignado a {vehiculo.placa} '
            f'desde el {desde:%d/%m/%Y}. Odoo ya lo registró.')
    else:
        messages.warning(
            request,
            f'{nuevo.nombre_completo} queda asignado a {vehiculo.placa} '
            f'desde el {desde:%d/%m/%Y}, pero Odoo no respondió. '
            f'El aviso se reintenta solo; no hay que repetir la asignación.')

    return redirect('transporte:flota')


@login_required
@transporte_required
def detalle_vehiculo(request, vehiculo_id):
    """Ficha del vehículo con el historial completo de documentos."""
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)
    if vehiculo not in vehiculos_visibles(request.user):
        messages.error(request, 'Ese vehículo no es de tu flota.')
        return redirect('transporte:flota')

    documentos = vehiculo.documentos.order_by('tipo', '-fecha_vencimiento')
    vigentes = {d.tipo: d for d in vehiculo.documentos_vigentes()}

    # Un renglón por tipo, con su documento vigente o sin él. Se arma aquí
    # porque la plantilla no puede indexar un diccionario por variable y
    # resolverlo allá sale en un enredo de bucles anidados.
    estado_por_tipo = [
        {'nombre': nombre, 'doc': vigentes.get(codigo)}
        for codigo, nombre in DocumentoVehiculo.TIPOS
    ]

    return render(request, 'transporte/detalle_vehiculo.html', {
        'vehiculo': vehiculo,
        'documentos': documentos,
        'estado_por_tipo': estado_por_tipo,
        'es_admin': es_admin_transporte(request.user),
    })


# =========================================================================
# Servicios asignados
# =========================================================================

@login_required
@transporte_required
def servicios(request):
    """Los servicios que Odoo le asignó a cada vehículo.

    Es solo un listado: el tablero y la asignación son de Odoo. Aquí se
    muestran para que el conductor sepa qué tiene encima sin entrar a Odoo.
    """
    grupos, sin_vehiculo, error = servicios_visibles(request.user)

    asignados = [s for g in grupos for s in g['servicios']]
    es_admin = es_admin_transporte(request.user)

    return render(request, 'transporte/servicios.html', {
        'grupos': grupos,
        'sin_vehiculo': sin_vehiculo,
        'error': error,
        'es_admin': es_admin,
        'es_solo_conductor': es_conductor(empleado_de(request.user)) and not es_admin,
        'total': len(asignados),
        'atrasados': sum(1 for s in asignados
                         if s['urgencia']['clave'] == 'atrasado'),
        'de_hoy': sum(1 for s in asignados if s['urgencia']['clave'] == 'hoy'),
        'en_ruta': sum(1 for s in asignados
                       if s.get('inicio') and not s['inicio'].esta_entregado),
        'entregados': sum(1 for s in asignados
                          if s.get('inicio') and s['inicio'].esta_entregado),
        'novedades': ServicioIniciado.NOVEDADES,
    })


@login_required
@transporte_required
@require_POST
def iniciar_servicio(request):
    """El conductor marca que salió a hacer un servicio.

    No se valida el servicio contra Odoo antes de guardar, y es a
    propósito: el camión ya arrancó y la salida no puede depender de que
    Odoo conteste. Lo que sí se fija aquí es a quién pertenece: el vehículo
    y el conductor salen de la sesión, nunca del formulario, así que lo
    peor que podría hacer alguien manipulando la página es crearse un
    registro suyo, que su jefe ve.
    """
    empleado = empleado_de(request.user)
    vehiculo = Vehiculo.objects.filter(
        conductor=empleado, activo=True).first() if empleado else None

    if not vehiculo:
        messages.error(
            request,
            'No tienes un vehículo asignado, así que no puedes iniciar un '
            'servicio. Habla con tu jefe para que te asigne uno.')
        return redirect('transporte:servicios')

    odoo_modelo = (request.POST.get('odoo_modelo') or '').strip()[:80]
    odoo_id_raw = (request.POST.get('odoo_id') or '').strip()
    if not odoo_modelo or not odoo_id_raw.isdigit():
        messages.error(request, 'No se pudo identificar el servicio.')
        return redirect('transporte:servicios')
    odoo_id = int(odoo_id_raw)

    ya = ServicioIniciado.objects.filter(
        odoo_modelo=odoo_modelo, odoo_id=odoo_id, anulado_en__isnull=True
    ).select_related('conductor').first()
    if ya:
        messages.info(
            request,
            f'Ese servicio ya estaba iniciado por {ya.conductor.nombre_completo} '
            f'a las {timezone.localtime(ya.iniciado_en):%H:%M}.')
        return redirect('transporte:servicios')

    kilometraje = (request.POST.get('kilometraje') or '').strip()
    servicio = ServicioIniciado.objects.create(
        odoo_modelo=odoo_modelo,
        odoo_id=odoo_id,
        ref=(request.POST.get('ref') or '').strip()[:60],
        tipo=(request.POST.get('tipo') or '').strip()[:40],
        resumen=(request.POST.get('resumen') or '').strip()[:200],
        vehiculo=vehiculo,
        conductor=empleado,
        kilometraje=int(kilometraje) if kilometraje.isdigit() else None,
    )

    rechazo = _avisar_inicio_a_odoo(servicio)
    if rechazo:
        aviso = _mensaje_de_rechazo(
            rechazo, 'la salida', servicio.ref or servicio.odoo_id)
        if not rechazo.es_culpa_nuestra:
            aviso += ' Habla con tu coordinador antes de arrancar.'
        messages.error(request, aviso)
        return redirect('transporte:servicios')

    messages.success(
        request,
        f'Servicio {servicio.ref or servicio.odoo_id} iniciado a las '
        f'{timezone.localtime(servicio.iniciado_en):%H:%M}. Buen viaje.')
    return redirect('transporte:servicios')


def _avisar_inicio_a_odoo(servicio):
    """Avisa la salida con timeout corto. Devuelve el rechazo si lo hubo.

    Tres desenlaces distintos:

    - Odoo lo acepta: queda sincronizado.
    - Odoo no contesta: queda pendiente y la sincronización lo reintenta.
    - Odoo lo rechaza (400 o 409): no se reintenta nunca más, porque
      repetir el aviso daría siempre lo mismo. El motivo se le muestra a
      quien lo marcó.

    Nunca interrumpe al conductor: el registro ya está guardado.
    """
    try:
        avisar_servicio_iniciado(servicio, timeout=5)
    except OdooConflictoError as e:
        ServicioIniciado.objects.filter(pk=servicio.pk).update(
            conflicto_odoo=True, ultimo_error=e.motivo[:300])
        _registrar_rechazo(servicio, e, 'la salida')
        return e
    except OdooTransporteError as e:
        ServicioIniciado.objects.filter(pk=servicio.pk).update(
            ultimo_error=str(e)[:300])
        logger.info('Salida de %s pendiente de avisar a Odoo: %s',
                    servicio.ref or servicio.odoo_id, e)
        return None
    ServicioIniciado.objects.filter(pk=servicio.pk).update(
        sincronizado=True, fecha_sincronizacion=timezone.now(),
        ultimo_error='', conflicto_odoo=False)
    return None


@login_required
@transporte_required
@require_POST
def entregar_servicio(request, inicio_id):
    """El conductor marca que ya entregó.

    Cierra el viaje del lado del conductor. El documento de Odoo lo cierra
    Odoo; esto es lo que solo el conductor sabe: que ya descargó.
    """
    servicio = get_object_or_404(ServicioIniciado, pk=inicio_id)
    empleado = empleado_de(request.user)

    if servicio.conductor_id != (empleado.pk if empleado else None):
        messages.error(request, 'Ese servicio no es tuyo.')
        return redirect('transporte:servicios')

    if not servicio.puede_entregarse:
        if servicio.esta_entregado:
            messages.info(
                request,
                f'Ese servicio ya lo entregaste a las '
                f'{timezone.localtime(servicio.entregado_en):%H:%M}.')
        else:
            messages.error(request, 'Ese servicio no está activo.')
        return redirect('transporte:servicios')

    km_raw = (request.POST.get('kilometraje_llegada') or '').strip()
    km_llegada = int(km_raw) if km_raw.isdigit() else None

    novedad = (request.POST.get('novedad') or '').strip()
    if novedad not in dict(ServicioIniciado.NOVEDADES):
        novedad = ServicioIniciado.SIN_NOVEDAD
    observacion = (request.POST.get('observacion') or '').strip()

    # Si hubo novedad, la observación no es opcional: una entrega parcial o
    # una devolución mueve inventario y de este texto sale el ajuste en
    # Odoo. "Hubo un problema" sin decir cuál no le sirve a nadie.
    if novedad != ServicioIniciado.SIN_NOVEDAD and not observacion:
        messages.error(
            request,
            'Marcaste una novedad, así que hay que explicar qué pasó: de '
            'ahí sale el ajuste en Odoo.')
        return redirect('transporte:servicios')

    toneladas = _decimal_o_none(request.POST.get('toneladas_entregadas'))

    # Un kilometraje de llegada menor al de salida es un dedazo, no un
    # viaje. Se rechaza en vez de guardarlo: un recorrido negativo daña
    # cualquier cuenta que se haga después con estos números.
    if (km_llegada is not None and servicio.kilometraje is not None
            and km_llegada < servicio.kilometraje):
        # El separador de miles se cambia sobre cada número, no sobre la
        # frase: hacerlo sobre todo el texto se lleva por delante las comas
        # de la redacción.
        messages.error(
            request,
            f'El kilometraje de llegada ({_miles(km_llegada)}) es menor que '
            f'el de salida ({_miles(servicio.kilometraje)}). Revisa el '
            f'número, o déjalo vacío y márcala sin kilometraje.')
        return redirect('transporte:servicios')

    servicio.entregado_en = timezone.now()
    servicio.kilometraje_llegada = km_llegada
    servicio.novedad = novedad
    servicio.observacion = observacion
    servicio.toneladas_entregadas = toneladas
    servicio.save(update_fields=['entregado_en', 'kilometraje_llegada',
                                 'novedad', 'observacion',
                                 'toneladas_entregadas'])

    rechazo = _avisar_entrega_a_odoo(servicio)
    if rechazo:
        aviso = _mensaje_de_rechazo(
            rechazo, 'el cierre', servicio.ref or servicio.odoo_id)
        if not rechazo.es_culpa_nuestra:
            aviso += ' Queda registrado acá; avísale a tu coordinador.'
        messages.error(request, aviso)
        return redirect('transporte:servicios')

    recorrido = ''
    if km_llegada is not None and servicio.kilometraje is not None:
        recorrido = f' Recorriste {_miles(km_llegada - servicio.kilometraje)} km.'
    aviso = ''
    if novedad != ServicioIniciado.SIN_NOVEDAD:
        aviso = (f' Quedó reportada la novedad: '
                 f'{servicio.get_novedad_display().lower()}.')
    messages.success(
        request,
        f'Entrega de {servicio.ref or servicio.odoo_id} registrada a las '
        f'{timezone.localtime(servicio.entregado_en):%H:%M}.{recorrido}{aviso}')
    return redirect('transporte:servicios')


def _avisar_entrega_a_odoo(servicio):
    """Igual que la salida: devuelve el rechazo si Odoo la rechaza."""
    try:
        avisar_servicio_finalizado(servicio, timeout=5)
    except OdooConflictoError as e:
        ServicioIniciado.objects.filter(pk=servicio.pk).update(
            conflicto_odoo_entrega=True, ultimo_error_entrega=e.motivo[:300])
        _registrar_rechazo(servicio, e, 'el cierre')
        return e
    except OdooTransporteError as e:
        ServicioIniciado.objects.filter(pk=servicio.pk).update(
            ultimo_error_entrega=str(e)[:300])
        logger.info('Entrega de %s pendiente de avisar a Odoo: %s',
                    servicio.ref or servicio.odoo_id, e)
        return None
    ServicioIniciado.objects.filter(pk=servicio.pk).update(
        entrega_sincronizada=True,
        fecha_sincronizacion_entrega=timezone.now(),
        ultimo_error_entrega='', conflicto_odoo_entrega=False)
    return None


@login_required
@transporte_required
@require_POST
def deshacer_entrega(request, inicio_id):
    """Quita una entrega marcada por error, poco después de marcarla."""
    servicio = get_object_or_404(ServicioIniciado, pk=inicio_id)
    empleado = empleado_de(request.user)

    if servicio.conductor_id != (empleado.pk if empleado else None):
        messages.error(request, 'Ese servicio no es tuyo.')
        return redirect('transporte:servicios')

    if not servicio.puede_deshacer_entrega:
        if servicio.entrega_sincronizada:
            messages.error(
                request,
                'Odoo ya registró esa entrega, así que no se puede deshacer '
                'desde aquí. Avísale a tu jefe.')
        elif not servicio.esta_entregado:
            messages.info(request, 'Ese servicio todavía no está entregado.')
        else:
            messages.error(
                request,
                f'Ya pasaron más de {ServicioIniciado.MINUTOS_PARA_DESHACER} '
                f'minutos desde que la marcaste. Avísale a tu jefe.')
        return redirect('transporte:servicios')

    servicio.entregado_en = None
    servicio.kilometraje_llegada = None
    servicio.novedad = ServicioIniciado.SIN_NOVEDAD
    servicio.observacion = ''
    servicio.toneladas_entregadas = None
    servicio.conflicto_odoo_entrega = False
    servicio.ultimo_error_entrega = ''
    servicio.save(update_fields=[
        'entregado_en', 'kilometraje_llegada', 'novedad', 'observacion',
        'toneladas_entregadas', 'conflicto_odoo_entrega',
        'ultimo_error_entrega'])
    messages.success(
        request,
        f'Se quitó la entrega de {servicio.ref or servicio.odoo_id}. '
        f'El servicio vuelve a quedar en ruta.')
    return redirect('transporte:servicios')


@login_required
@transporte_required
@require_POST
def deshacer_inicio(request, inicio_id):
    """Anula un inicio marcado por error, poco después de marcarlo."""
    servicio = get_object_or_404(ServicioIniciado, pk=inicio_id)
    empleado = empleado_de(request.user)

    if servicio.conductor_id != (empleado.pk if empleado else None):
        messages.error(request, 'Ese servicio no es tuyo.')
        return redirect('transporte:servicios')

    if not servicio.puede_deshacerse:
        if servicio.sincronizado:
            messages.error(
                request,
                'Odoo ya registró esa salida, así que no se puede deshacer '
                'desde aquí. Avísale a tu jefe.')
        else:
            messages.error(
                request,
                f'Ya pasaron más de {ServicioIniciado.MINUTOS_PARA_DESHACER} '
                f'minutos desde que lo iniciaste. Avísale a tu jefe.')
        return redirect('transporte:servicios')

    servicio.anulado_en = timezone.now()
    servicio.anulado_por = request.user
    servicio.save(update_fields=['anulado_en', 'anulado_por'])
    messages.success(
        request,
        f'Se deshizo el inicio de {servicio.ref or servicio.odoo_id}. '
        f'Puedes volver a marcarlo cuando salgas.')
    return redirect('transporte:servicios')


# =========================================================================
# Documentos
# =========================================================================

@login_required
@admin_transporte_required
def registrar_documento(request, vehiculo_id):
    """Registrar o renovar un documento del vehículo.

    Vive en el módulo y no en el admin de Django porque lo hace el
    coordinador, que es quien tiene el papel en la mano.
    """
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)
    if vehiculo not in vehiculos_visibles(request.user):
        messages.error(request, 'Ese vehículo no es de tu flota.')
        return redirect('transporte:flota')

    if request.method == 'POST':
        form = DocumentoVehiculoForm(
            request.POST, request.FILES, vehiculo=vehiculo)
        if form.is_valid():
            doc = form.save(usuario=request.user)
            if doc.fecha_vencimiento:
                messages.success(
                    request,
                    f'{doc.get_tipo_display()} registrado para {vehiculo.placa}. '
                    f'Vence el {doc.fecha_vencimiento:%d/%m/%Y}; el aviso sale '
                    f'30 días antes.')
            else:
                messages.warning(
                    request,
                    f'{doc.get_tipo_display()} registrado, pero sin fecha de '
                    f'vencimiento: no se podrá avisar cuándo se vence.')
            return redirect('transporte:detalle_vehiculo', vehiculo_id=vehiculo.pk)
    else:
        inicial = {}
        tipo = request.GET.get('tipo')
        if tipo in dict(DocumentoVehiculo.TIPOS):
            inicial['tipo'] = tipo
        form = DocumentoVehiculoForm(initial=inicial, vehiculo=vehiculo)

    return render(request, 'transporte/documento_form.html', {
        'form': form,
        'vehiculo': vehiculo,
    })


# =========================================================================
# Gastos
# =========================================================================

@login_required
@transporte_required
def mis_gastos(request):
    """Lo que ve el conductor: su vehículo y los gastos que ha registrado."""
    empleado = empleado_de(request.user)
    if not empleado:
        messages.error(request, 'Tu usuario no tiene ficha de empleado.')
        return redirect('core:dashboard')

    vehiculo = Vehiculo.objects.filter(
        conductor=empleado, activo=True).select_related('conductor').first()

    gastos = list(GastoVehiculo.objects
                  .filter(conductor=empleado)
                  .select_related('vehiculo')
                  .order_by('-fecha', '-fecha_creacion')[:60])

    hoy = timezone.localdate()
    inicio_mes = hoy.replace(day=1)
    del_mes = [g for g in gastos if g.fecha >= inicio_mes]
    total_mes = sum(g.monto for g in del_mes if g.cuenta_como_costo)

    return render(request, 'transporte/mis_gastos.html', {
        'vehiculo': vehiculo,
        # Que el conductor vea el estado de su propia licencia: es el papel
        # que le piden a él en la vía, no al coordinador.
        'licencia': estado_licencia(empleado),
        'gastos': gastos,
        'total_mes': total_mes,
        'cantidad_mes': len(del_mes),
        'rechazados': sum(1 for g in gastos if g.estado == GastoVehiculo.RECHAZADO),
        'documentos': vehiculo.documentos_vigentes() if vehiculo else [],
    })


@login_required
@transporte_required
def registrar_gasto(request):
    """El conductor registra un gasto con el recibo.

    Ya no se exige tener vehículo asignado: hay gastos que no son de
    ningún carro, y el conductor sigue siendo conductor aunque ese día no
    tenga uno a su nombre. El suyo viene propuesto en el formulario.
    """
    empleado = empleado_de(request.user)
    if not es_conductor(empleado):
        messages.error(
            request,
            'Los gastos los registra el conductor. Si vas a registrar uno '
            'por él, hazlo desde Gastos de la flota.')
        return redirect('transporte:gastos_flota')

    vehiculo = Vehiculo.objects.filter(conductor=empleado, activo=True).first()

    if request.method == 'POST':
        form = GastoVehiculoForm(
            request.POST, request.FILES, vehiculo=vehiculo, conductor=empleado)
        if form.is_valid():
            gasto = form.save(usuario=request.user)
            messages.success(
                request,
                f'Gasto de {gasto.get_tipo_display().lower()} por '
                f'${_miles(int(gasto.monto))} registrado'
                f'{_donde(gasto)}. Queda pendiente de revisión.')
            return redirect('transporte:mis_gastos')
    else:
        form = GastoVehiculoForm(vehiculo=vehiculo, conductor=empleado)

    return render(request, 'transporte/gasto_form.html', {
        'form': form,
        'vehiculo': vehiculo,
    })


def _donde(gasto):
    """" para JYN 240", " para el servicio X", o nada."""
    partes = []
    if gasto.vehiculo_id:
        partes.append(f'para {gasto.vehiculo.placa}')
    if gasto.servicio_id:
        partes.append(f'en el servicio {gasto.servicio.ref or gasto.servicio.odoo_id}')
    return f' {" ".join(partes)}' if partes else ''


@login_required
@admin_transporte_required
def registrar_gasto_admin(request):
    """El coordinador registra un gasto a nombre de uno de sus conductores.

    Nace aprobado y con la marca de quién lo digitó: pedirle que después
    apruebe lo que él mismo registró no agrega control, solo pasos.
    """
    empleado = empleado_de(request.user)
    if request.user.is_staff:
        conductores = conductores_vigentes()
    else:
        conductores = conductores_a_cargo(empleado)

    if not conductores.exists():
        messages.error(request, 'No tienes conductores a cargo.')
        return redirect('transporte:gastos_flota')

    if request.method == 'POST':
        form = GastoAdminForm(request.POST, request.FILES,
                              conductores=conductores)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.registrado_por = request.user
            gasto.estado = GastoVehiculo.APROBADO
            gasto.revisado_por = request.user
            gasto.fecha_revision = timezone.now()
            gasto.save()
            messages.success(
                request,
                f'Gasto de {gasto.get_tipo_display().lower()} por '
                f'${_miles(int(gasto.monto))} registrado a nombre de '
                f'{gasto.conductor.nombre_completo}{_donde(gasto)}. '
                f'Queda aprobado.')
            return redirect('transporte:gastos_flota')
    else:
        form = GastoAdminForm(conductores=conductores)

    return render(request, 'transporte/gasto_form.html', {
        'form': form,
        'modo_admin': True,
    })


@login_required
@transporte_required
def editar_gasto(request, gasto_id):
    """Corregir un gasto que todavía nadie ha revisado."""
    gasto = get_object_or_404(GastoVehiculo, pk=gasto_id)
    empleado = empleado_de(request.user)

    if gasto.conductor_id != (empleado.pk if empleado else None):
        messages.error(request, 'Ese gasto no es tuyo.')
        return redirect('transporte:mis_gastos')
    if not gasto.editable_por_conductor:
        messages.error(
            request,
            f'Ese gasto ya fue {gasto.get_estado_display().lower()} y no se '
            f'puede cambiar. Si hay un error, avísale a tu jefe.')
        return redirect('transporte:mis_gastos')

    if request.method == 'POST':
        form = GastoVehiculoForm(
            request.POST, request.FILES, instance=gasto,
            vehiculo=gasto.vehiculo, conductor=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gasto corregido.')
            return redirect('transporte:mis_gastos')
    else:
        form = GastoVehiculoForm(
            instance=gasto, vehiculo=gasto.vehiculo, conductor=empleado)

    return render(request, 'transporte/gasto_form.html', {
        'form': form,
        'vehiculo': gasto.vehiculo,
        'gasto': gasto,
    })


@login_required
@admin_transporte_required
def gastos_flota(request):
    """Los gastos de los conductores a cargo, con filtros y cuentas.

    Los totales se suman en la base y no recorriendo los gastos en
    memoria: con el histórico de un par de años, traerlos todos para sumar
    en Python deja de ser gratis.
    """
    visibles = gastos_visibles(request.user)
    gastos = visibles.select_related(
        'vehiculo', 'conductor', 'revisado_por', 'registrado_por', 'servicio')

    filtros = {}

    estado = (request.GET.get('estado') or '').strip()
    if estado in dict(GastoVehiculo.ESTADOS):
        gastos = gastos.filter(estado=estado)
        filtros['estado'] = estado

    conductor_id = (request.GET.get('conductor') or '').strip()
    if conductor_id:
        gastos = gastos.filter(conductor_id=conductor_id)
        filtros['conductor'] = conductor_id

    vehiculo_id = (request.GET.get('vehiculo') or '').strip()
    if vehiculo_id == 'sin':
        # "Sin vehículo" es un filtro útil por sí mismo: son los gastos que
        # van a la cuenta del conductor y a la de ningún carro.
        gastos = gastos.filter(vehiculo__isnull=True)
        filtros['vehiculo'] = 'sin'
    elif vehiculo_id:
        gastos = gastos.filter(vehiculo_id=vehiculo_id)
        filtros['vehiculo'] = vehiculo_id

    servicio_id = (request.GET.get('servicio') or '').strip()
    if servicio_id:
        gastos = gastos.filter(servicio_id=servicio_id)
        filtros['servicio'] = servicio_id

    desde = _fecha_o_none(request.GET.get('desde'))
    hasta = _fecha_o_none(request.GET.get('hasta'))
    if desde:
        gastos = gastos.filter(fecha__gte=desde)
        filtros['desde'] = desde.isoformat()
    if hasta:
        gastos = gastos.filter(fecha__lte=hasta)
        filtros['hasta'] = hasta.isoformat()

    gastos = gastos.order_by('-fecha', '-fecha_creacion')

    # Los totales son de lo filtrado, no del mes: si el jefe acotó a un
    # conductor y a unas fechas, lo que quiere ver es esa cuenta.
    resumen = gastos.aggregate(
        costo=Sum('monto', filter=GastoVehiculo.filtro_costo()),
        deuda=Sum('monto', filter=GastoVehiculo.filtro_deuda_conductor()),
        cantidad=Count('id'),
    )

    por_conductor = (gastos.values('conductor_id',
                                   'conductor__nombres',
                                   'conductor__apellidos')
                     .annotate(costo=Sum('monto', filter=GastoVehiculo.filtro_costo()),
                               deuda=Sum('monto', filter=GastoVehiculo.filtro_deuda_conductor()),
                               cantidad=Count('id'))
                     .order_by('conductor__apellidos'))

    por_vehiculo = (gastos.values('vehiculo_id', 'vehiculo__placa')
                    .annotate(costo=Sum('monto', filter=GastoVehiculo.filtro_costo()),
                              cantidad=Count('id'))
                    .order_by('vehiculo__placa'))

    empleado = empleado_de(request.user)
    if request.user.is_staff:
        conductores = conductores_vigentes()
    else:
        conductores = conductores_a_cargo(empleado)

    return render(request, 'transporte/gastos_flota.html', {
        'gastos': list(gastos[:200]),
        'total_filtrado': resumen['cantidad'] or 0,
        'estados': GastoVehiculo.ESTADOS,
        'estado_filtro': filtros.get('estado', ''),
        'conductor_filtro': filtros.get('conductor', ''),
        'vehiculo_filtro': filtros.get('vehiculo', ''),
        'servicio_filtro': filtros.get('servicio', ''),
        'desde': filtros.get('desde', ''),
        'hasta': filtros.get('hasta', ''),
        'hay_filtros': bool(filtros),
        'conductores': conductores.order_by('apellidos', 'nombres'),
        'vehiculos': vehiculos_visibles(request.user).order_by('placa'),
        'pendientes': visibles.filter(estado=GastoVehiculo.PENDIENTE).count(),
        'costo_total': resumen['costo'] or 0,
        'deuda_total': resumen['deuda'] or 0,
        'por_conductor': list(por_conductor),
        'por_vehiculo': list(por_vehiculo),
    })


def _fecha_o_none(texto):
    try:
        return date.fromisoformat((texto or '').strip())
    except ValueError:
        return None


# =========================================================================
# Cuentas y cierres
# =========================================================================

@login_required
@admin_transporte_required
def cuentas(request):
    """Lo que cada conductor y cada vehículo tiene sin cerrar."""
    por_conductor, por_vehiculo = cuentas_abiertas(request.user)

    cierres = (CierreGastos.objects
               .filter(_cierres_del_usuario(request.user))
               .select_related('conductor', 'vehiculo', 'cerrado_por',
                               'anulado_por')
               .order_by('-fecha_cierre')[:40])

    return render(request, 'transporte/cuentas.html', {
        'por_conductor': por_conductor,
        'por_vehiculo': por_vehiculo,
        'cierres': list(cierres),
        'total_abierto_conductores': sum(c['costo'] for c in por_conductor),
        'total_deuda_conductores': sum(c['deuda'] for c in por_conductor),
        'pendientes_en_cuentas': sum(c['pendientes'] for c in por_conductor),
    })


def _cierres_del_usuario(usuario):
    """Los cierres de los conductores y vehículos que este usuario ve."""
    from django.db.models import Q

    if usuario.is_staff:
        return Q()
    empleado = empleado_de(usuario)
    return (Q(conductor__in=conductores_a_cargo(empleado))
            | Q(vehiculo__in=vehiculos_visibles(usuario)))


@login_required
@admin_transporte_required
@require_POST
def cerrar_cuenta_vista(request, ambito, sujeto_id):
    """Cierra la cuenta de un conductor o de un vehículo."""
    if ambito == CierreGastos.CONDUCTOR:
        permitidos = (conductores_vigentes() if request.user.is_staff
                      else conductores_a_cargo(empleado_de(request.user)))
        sujeto = permitidos.filter(pk=sujeto_id).first()
        if not sujeto:
            messages.error(request, 'Ese conductor no está a tu cargo.')
            return redirect('transporte:cuentas')
    elif ambito == CierreGastos.VEHICULO:
        sujeto = vehiculos_visibles(request.user).filter(pk=sujeto_id).first()
        if not sujeto:
            messages.error(request, 'Ese vehículo no es de tu flota.')
            return redirect('transporte:cuentas')
    else:
        messages.error(request, 'Ámbito de cierre desconocido.')
        return redirect('transporte:cuentas')

    try:
        cierre = cerrar_cuenta(
            ambito, sujeto, request.user,
            observaciones=request.POST.get('observaciones', ''),
            base=gastos_visibles(request.user))
    except CierreImposible as e:
        messages.error(request, str(e))
        return redirect('transporte:cuentas')

    messages.success(
        request,
        f'Cuenta de {cierre.sujeto} cerrada: {cierre.cantidad} gasto'
        f'{"s" if cierre.cantidad != 1 else ""} por '
        f'${_miles(int(cierre.total_costo))}'
        + (f', más ${_miles(int(cierre.total_deuda))} de multas a su cargo'
           if cierre.total_deuda else '')
        + '. La cuenta arranca de cero.')

    # El cierre ya está firmado; esto es lo que sigue. Se intenta acá para
    # que el jefe sepa en el momento si llegó, pero si no llega no se
    # deshace nada: queda en cola.
    _contar_a_odoo(request, cierre)
    return redirect('transporte:detalle_cierre', cierre_id=cierre.pk)


def _contar_a_odoo(request, cierre):
    """Manda el cierre a la contabilidad y cuenta en pantalla qué pasó.

    Tres desenlaces y tres mensajes distintos, porque lo que tiene que
    hacer quien cerró la cuenta es distinto en cada uno: nada, esperar, o
    ir a hablar con quien lleva la contabilidad.
    """
    resultado, detalle = enviar_cierre_a_odoo(cierre, timeout=TIMEOUT_PANTALLA)
    if resultado == ENVIADO:
        messages.info(
            request,
            'Ya está en la contabilidad de Odoo'
            + (f' como {detalle}.' if detalle else '.'))
    elif resultado == RECHAZADO:
        messages.warning(
            request,
            f'Odoo no aceptó el cierre: {detalle} El cierre vale igual en '
            f'SIGHU, pero allá no quedó contabilizado y no se reintenta '
            f'solo.')
    else:
        messages.info(
            request,
            'Odoo no contestó ahora mismo, así que el cierre quedó en cola. '
            'Se reintenta solo; no hay que volver a cerrar nada.')


@login_required
@admin_transporte_required
def detalle_cierre(request, cierre_id):
    """El detalle de un cierre: sus renglones y sus totales congelados."""
    cierre = get_object_or_404(
        CierreGastos.objects.select_related(
            'conductor', 'vehiculo', 'cerrado_por', 'anulado_por'),
        pk=cierre_id)

    if not CierreGastos.objects.filter(
            _cierres_del_usuario(request.user), pk=cierre.pk).exists():
        messages.error(request, 'Ese cierre no es de tu flota.')
        return redirect('transporte:cuentas')

    return render(request, 'transporte/cierre_detalle.html', {
        'cierre': cierre,
        'gastos': list(cierre.gastos().order_by('-fecha', '-fecha_creacion')),
    })


@login_required
@admin_transporte_required
@require_POST
def anular_cierre_vista(request, cierre_id):
    """Deshace un cierre mal hecho y devuelve los gastos a la cuenta."""
    cierre = get_object_or_404(CierreGastos, pk=cierre_id)
    if not CierreGastos.objects.filter(
            _cierres_del_usuario(request.user), pk=cierre.pk).exists():
        messages.error(request, 'Ese cierre no es de tu flota.')
        return redirect('transporte:cuentas')

    ya_estaba_en_odoo = cierre.sincronizado

    try:
        anular_cierre(cierre, request.user, request.POST.get('motivo', ''))
    except CierreImposible as e:
        messages.error(request, str(e))
        return redirect('transporte:detalle_cierre', cierre_id=cierre.pk)

    messages.success(
        request,
        f'Cierre de {cierre.sujeto} anulado. Sus {cierre.cantidad} gasto'
        f'{"s" if cierre.cantidad != 1 else ""} volvieron a la cuenta abierta.')

    # Si Odoo ya lo tenía, hay que decírselo: esos mismos gastos van a
    # volver a llegar en el cierre siguiente y sin el aviso quedarían
    # contabilizados dos veces.
    if ya_estaba_en_odoo:
        cierre.refresh_from_db()
        resultado, detalle = enviar_anulacion_a_odoo(
            cierre, timeout=TIMEOUT_PANTALLA)
        if resultado == ENVIADO:
            messages.info(request, 'Odoo ya sabe que el cierre dejó de valer.')
        elif resultado == RECHAZADO:
            messages.warning(
                request,
                f'Odoo no aceptó la anulación: {detalle} Ese cierre ya estaba '
                f'contabilizado allá: hay que reversarlo a mano, porque sus '
                f'gastos van a volver a llegar en el próximo cierre.')
        else:
            messages.warning(
                request,
                'Ese cierre ya estaba en Odoo y no se pudo avisar la '
                'anulación ahora. Queda en cola y se reintenta solo.')
    return redirect('transporte:cuentas')


@login_required
@admin_transporte_required
@require_POST
def reenviar_cierre_odoo(request, cierre_id):
    """Vuelve a intentar el envío a la contabilidad, a mano.

    Existe para los rechazados, que son los únicos que el reintento
    automático no toca: una vez que alguien arregló del lado de Odoo lo
    que lo hizo fallar —una cuenta sin configurar, un vehículo que allá no
    existía— hace falta algo que lo empuje de nuevo. Los que están en cola
    también se pueden empujar, aunque no haga falta esperar al cron.
    """
    cierre = get_object_or_404(CierreGastos, pk=cierre_id)
    if not CierreGastos.objects.filter(
            _cierres_del_usuario(request.user), pk=cierre.pk).exists():
        messages.error(request, 'Ese cierre no es de tu flota.')
        return redirect('transporte:cuentas')

    destino = redirect('transporte:detalle_cierre', cierre_id=cierre.pk)

    if not cierre.esta_activo:
        if not cierre.sincronizado:
            messages.info(
                request,
                'Ese cierre está anulado y nunca llegó a Odoo. No hay nada '
                'que enviar.')
            return destino
        # Lo que falta mandar de un cierre anulado es la anulación, no el
        # cierre: reenviarlo lo volvería a contabilizar.
        resultado, detalle = enviar_anulacion_a_odoo(
            cierre, timeout=TIMEOUT_PANTALLA)
        if resultado == ENVIADO:
            messages.success(request, 'Odoo ya sabe que el cierre dejó de valer.')
        else:
            messages.warning(request, f'Sigue sin poder avisarse: {detalle}')
        return destino

    if cierre.sincronizado:
        messages.info(
            request,
            'Ese cierre ya está en Odoo'
            + (f' como {cierre.odoo_ref}.' if cierre.odoo_ref else '.')
            + ' Si allá quedó mal, se corrige allá.')
        return destino

    # Se limpia la marca de rechazo antes de intentar: si vuelve a fallar,
    # la vuelve a poner con el motivo nuevo, que es el que sirve.
    CierreGastos.objects.filter(pk=cierre.pk).update(conflicto_odoo=False)
    cierre.refresh_from_db()
    _contar_a_odoo(request, cierre)
    return destino


@login_required
@admin_transporte_required
@require_POST
def revisar_gasto(request, gasto_id):
    """Aprobar o rechazar un gasto."""
    gasto = get_object_or_404(GastoVehiculo, pk=gasto_id)
    # Por el gasto y no por el vehículo: uno sin vehículo también se revisa.
    if not gastos_visibles(request.user).filter(pk=gasto.pk).exists():
        messages.error(request, 'Ese gasto no es de tus conductores.')
        return redirect('transporte:gastos_flota')

    if gasto.cerrado:
        # Aprobar o rechazar cambia si entra al costo, y el total del cierre
        # ya quedó firmado con este renglón adentro.
        messages.error(
            request,
            'Ese gasto ya está en una cuenta cerrada. Si hay que cambiarlo, '
            'anula el cierre primero.')
        return redirect('transporte:gastos_flota')

    form = RevisionGastoForm(request.POST)
    if not form.is_valid():
        for errores in form.errors.values():
            for e in errores:
                messages.error(request, e)
        return redirect('transporte:gastos_flota')

    decision = form.cleaned_data['decision']
    gasto.estado = (GastoVehiculo.APROBADO if decision == 'aprobar'
                    else GastoVehiculo.RECHAZADO)
    gasto.observaciones_revision = form.cleaned_data['observaciones']
    gasto.revisado_por = request.user
    gasto.fecha_revision = timezone.now()
    gasto.save()

    verbo = 'aprobado' if decision == 'aprobar' else 'rechazado'
    messages.success(
        request, f'Gasto de {gasto.conductor.nombre_completo} {verbo}.')

    # Al rechazar, el conductor tiene que enterarse: si no, el gasto queda en
    # el limbo y nadie lo corrige.
    if decision == 'rechazar' and gasto.conductor.usuario_id:
        _avisar_rechazo(gasto)

    return redirect('transporte:gastos_flota')


def _avisar_rechazo(gasto):
    """Notifica al conductor que su gasto fue rechazado."""
    try:
        from apps.notifications.models import Notificacion, TipoNotificacion
        tipo, _ = TipoNotificacion.objects.get_or_create(
            codigo='gasto_vehiculo_rechazado',
            defaults={
                'nombre': 'Gasto de vehículo rechazado',
                'plantilla_titulo': '{titulo}',
                'plantilla_mensaje': '{mensaje}',
                'enviar_push': True,
            },
        )
        titulo = f'Gasto rechazado — {gasto.vehiculo.placa}'
        cuerpo = (
            f'Tu gasto de {gasto.get_tipo_display().lower()} del '
            f'{gasto.fecha:%d/%m/%Y} fue rechazado. '
            f'Motivo: {gasto.observaciones_revision}')
        Notificacion.objects.create(
            usuario=gasto.conductor.usuario,
            tipo_notificacion=tipo,
            titulo=titulo[:200],
            mensaje=cuerpo,
            datos_adicionales={'gasto_id': str(gasto.pk)},
        )
        try:
            from apps.notifications.push_utils import send_push
            send_push(gasto.conductor.usuario, titulo, cuerpo,
                      url='/transporte/mis-gastos/')
        except Exception as e:
            logger.warning('Push de rechazo no enviado: %s', e)
    except Exception as e:
        logger.error('No se pudo avisar el rechazo del gasto %s: %s', gasto.pk, e)
