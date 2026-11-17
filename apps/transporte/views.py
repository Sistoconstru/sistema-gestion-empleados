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
from django.db.models import Prefetch
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

from .forms import DocumentoVehiculoForm, GastoVehiculoForm, RevisionGastoForm
from .models import (
    DocumentoVehiculo, GastoVehiculo, ServicioIniciado, Vehiculo,
)
from .odoo_client import (
    OdooConflictoError, OdooTransporteError, avisar_servicio_finalizado,
    avisar_servicio_iniciado,
)
from .permisos import (
    admin_transporte_required, conductores_a_cargo, es_admin_transporte,
    es_conductor, empleado_de, transporte_required, vehiculos_visibles,
)
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
            from .permisos import conductores_vigentes
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

    return render(request, 'transporte/flota.html', {
        'vehiculos': vehiculos,
        'hoy': timezone.localdate(),
        'es_admin': es_admin,
        'asignables': asignables.order_by('apellidos', 'nombres'),
        'total_vencidos': vencidos,
        'total_por_vencer': por_vencer,
        'sin_conductor': sum(1 for v in vehiculos if v.activo and not v.conductor_id),
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
        from .permisos import conductores_vigentes
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
        'gastos': gastos,
        'total_mes': total_mes,
        'cantidad_mes': len(del_mes),
        'rechazados': sum(1 for g in gastos if g.estado == GastoVehiculo.RECHAZADO),
        'documentos': vehiculo.documentos_vigentes() if vehiculo else [],
    })


@login_required
@transporte_required
def registrar_gasto(request):
    """El conductor registra un gasto con el recibo."""
    empleado = empleado_de(request.user)
    vehiculo = Vehiculo.objects.filter(conductor=empleado, activo=True).first()

    if not vehiculo:
        messages.error(
            request,
            'No tienes un vehículo asignado, así que no puedes registrar '
            'gastos. Habla con tu jefe para que te asigne uno.')
        return redirect('transporte:mis_gastos')

    if request.method == 'POST':
        form = GastoVehiculoForm(
            request.POST, request.FILES, vehiculo=vehiculo, conductor=empleado)
        if form.is_valid():
            gasto = form.save()
            monto = f'{gasto.monto:,.0f}'.replace(',', '.')
            messages.success(
                request,
                f'Gasto de {gasto.get_tipo_display().lower()} por ${monto} '
                f'registrado. Queda pendiente de revisión.')
            return redirect('transporte:mis_gastos')
    else:
        form = GastoVehiculoForm(vehiculo=vehiculo, conductor=empleado)

    return render(request, 'transporte/gasto_form.html', {
        'form': form,
        'vehiculo': vehiculo,
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
    """Lo que ve el jefe: los gastos de sus conductores, para revisarlos."""
    vehiculos = vehiculos_visibles(request.user)
    gastos = (GastoVehiculo.objects
              .filter(vehiculo__in=vehiculos)
              .select_related('vehiculo', 'conductor', 'revisado_por')
              .order_by('-fecha', '-fecha_creacion'))

    estado = request.GET.get('estado')
    if estado in dict(GastoVehiculo.ESTADOS):
        gastos = gastos.filter(estado=estado)

    hoy = timezone.localdate()
    inicio_mes = hoy.replace(day=1)
    todos = GastoVehiculo.objects.filter(vehiculo__in=vehiculos)
    del_mes = [g for g in todos if g.fecha >= inicio_mes]

    return render(request, 'transporte/gastos_flota.html', {
        'gastos': list(gastos[:200]),
        'estado_filtro': estado or '',
        'estados': GastoVehiculo.ESTADOS,
        'pendientes': todos.filter(estado=GastoVehiculo.PENDIENTE).count(),
        'total_mes': sum(g.monto for g in del_mes if g.cuenta_como_costo),
        'multas_conductor_mes': sum(
            g.monto for g in del_mes
            if g.tipo == GastoVehiculo.MULTA
            and g.responsable == GastoVehiculo.RESPONSABLE_CONDUCTOR
            and g.estado != GastoVehiculo.RECHAZADO),
    })


@login_required
@admin_transporte_required
@require_POST
def revisar_gasto(request, gasto_id):
    """Aprobar o rechazar un gasto."""
    gasto = get_object_or_404(GastoVehiculo, pk=gasto_id)
    if gasto.vehiculo not in vehiculos_visibles(request.user):
        messages.error(request, 'Ese gasto no es de tu flota.')
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
