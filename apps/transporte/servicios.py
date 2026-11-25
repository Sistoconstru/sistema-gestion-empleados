"""Los servicios asignados a cada vehículo, tal como los muestra SIGHU.

El tablero de servicios vive en Odoo: allá se crean, allá se les asigna
vehículo y conductor, allá se arman los viajes y allá se cobran. SIGHU no
los crea ni los modifica; los consulta para que el conductor sepa qué
tiene encima, marque cuándo sale y cierre cada entrega.

**Viajes.** Un viaje es una salida del camión con varios servicios
(paradas), en un orden de entrega que decide el coordinador. Para el
conductor es una sola salida: un botón para iniciar el viaje entero y, de
ahí, un cierre por parada, porque una puede tener devolución y otra no. Un
servicio sin viaje se muestra y se maneja solo, como siempre.

El cruce con la flota de SIGHU es `vehiculo.id` de Odoo contra
`Vehiculo.odoo_id`.

Se consulta en vivo. Si Odoo no responde no hay nada que mostrar, y eso se
dice en pantalla en vez de dejar un listado viejo que el conductor creería
vigente.
"""
import hashlib
import logging
from datetime import datetime

from django.utils import timezone

from .odoo_client import MODELO_SERVICIO, OdooTransporteError, listar_servicios
from .permisos import empleado_de, vehiculos_visibles

logger = logging.getLogger(__name__)

# Cuánto se espera a Odoo con alguien mirando la pantalla. El timeout
# general es de 30s, que para una página es una eternidad.
TIMEOUT_PANTALLA = 10

# Lo que se le pide a Odoo. Los cancelados no: Odoo los manda para que un
# espejo los retire, pero aquí se consulta en vivo y basta con no pedirlos.
ESTADOS_CONSULTA = 'asignado,en_curso,finalizado'

TIPOS = {
    'entrega_venta': 'Entrega de pedido',
    'traslado_intersede': 'Traslado entre sedes',
    'recepcion_mp': 'Madera / materia prima',
    'suelto': 'Flete suelto',
    'interno': 'Interno',
}

ESTADOS = {
    'asignado': 'Asignado',
    'en_curso': 'En curso',
    'finalizado': 'Finalizado',
    'cancelado': 'Cancelado',
}


def _texto(valor):
    return (valor or '').strip() if isinstance(valor, str) else ''


def _entero(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _fecha(valor):
    """ISO 8601 con offset, como lo manda Odoo, a datetime."""
    if not valor:
        return None
    texto = str(valor).strip().replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(texto)
    except ValueError:
        logger.warning('Fecha de servicio ilegible: %r', valor)
        return None


def _urgencia(fecha, hoy):
    """Qué tan encima está, en palabras.

    Un conductor no quiere leer una fecha y restar; quiere saber si es de
    hoy. Y los atrasados tienen que saltar a la vista.
    """
    if not fecha:
        return {'clave': 'sin_fecha', 'texto': 'Sin fecha programada'}

    dia = timezone.localtime(fecha).date() if timezone.is_aware(fecha) else fecha.date()
    dias = (dia - hoy).days
    if dias < 0:
        n = abs(dias)
        return {'clave': 'atrasado',
                'texto': f'Atrasado {n} día{"s" if n != 1 else ""}'}
    if dias == 0:
        return {'clave': 'hoy', 'texto': 'Hoy'}
    if dias == 1:
        return {'clave': 'pronto', 'texto': 'Mañana'}
    return {'clave': 'proximo', 'texto': f'En {dias} días'}


def _viaje(bloque):
    """El bloque `viaje` de un servicio, o None si va solo."""
    if not isinstance(bloque, dict):
        return None
    odoo_id = _entero(bloque.get('id'))
    if not odoo_id:
        return None
    return {
        'odoo_id': odoo_id,
        'numero': _texto(bloque.get('numero')),
        'salida': _fecha(bloque.get('salida')),
        'parada': _entero(bloque.get('parada')),
        'total_paradas': _entero(bloque.get('total_paradas')) or 0,
        'toneladas': bloque.get('toneladas_viaje'),
        'capacidad': bloque.get('capacidad'),
        'indicaciones': _texto(bloque.get('indicaciones')),
    }


def normalizar(crudo):
    """Un servicio de Odoo en lo que hay que mostrar y lo que hay que avisar.

    La pareja `odoo_modelo` + `odoo_id` es la que identifica el servicio
    al iniciarlo y al cerrarlo; `ref` (el SRV/...) y `documento` (la
    entrega o el traslado que lo originó) son para leer.
    """
    if not isinstance(crudo, dict):
        return None
    odoo_id = _entero(crudo.get('id'))
    if not odoo_id:
        return None

    tipo = _texto(crudo.get('tipo'))
    estado = _texto(crudo.get('estado'))
    destino = crudo.get('destino') if isinstance(crudo.get('destino'), dict) else {}
    cliente = crudo.get('cliente') if isinstance(crudo.get('cliente'), dict) else {}
    vehiculo = crudo.get('vehiculo') if isinstance(crudo.get('vehiculo'), dict) else {}
    conductor = crudo.get('conductor') if isinstance(crudo.get('conductor'), dict) else {}

    direccion = ', '.join(p for p in (_texto(destino.get('direccion')),
                                      _texto(destino.get('ciudad'))) if p)
    # Quién recibe: lo que escribió quien pidió el servicio, y si no hay,
    # el contacto de la dirección de entrega.
    contacto = _texto(crudo.get('contacto_sitio')) or ', '.join(
        p for p in (_texto(destino.get('contacto')),
                    _texto(destino.get('telefono'))) if p)

    return {
        'odoo_modelo': MODELO_SERVICIO,
        'odoo_id': odoo_id,
        'ref': _texto(crudo.get('numero')),
        'documento': _texto(crudo.get('documento')),
        'pedido': _texto(crudo.get('pedido')),
        'tipo': tipo,
        'tipo_display': (TIPOS.get(tipo)
                         or tipo.replace('_', ' ').capitalize()
                         or 'Servicio'),
        'estado': estado,
        'estado_display': ESTADOS.get(estado) or estado.capitalize(),
        'fecha': _fecha(crudo.get('fecha_programada')),
        'origen': _texto(crudo.get('origen')),
        'destino': _texto(destino.get('descripcion')) or direccion,
        'direccion': direccion,
        'zona': _texto(destino.get('zona')),
        'contacto': contacto,
        'cliente': _texto(cliente.get('nombre')),
        'cliente_nit': _texto(cliente.get('nit')),
        'toneladas': crudo.get('toneladas'),
        'que_se_mueve': _texto(crudo.get('que_se_mueve')),
        'indicaciones': _texto(crudo.get('indicaciones')),
        'urgente': crudo.get('urgente') is True,
        'vehiculo_odoo_id': _entero(vehiculo.get('id')),
        'placa': _texto(vehiculo.get('placa')),
        'conductor_cedula': _texto(conductor.get('cedula')),
        'fin_real': _fecha(crudo.get('fin_real')),
        # La última vez que alguien lo tocó en Odoo. Sirve para saber si la
        # pantalla quedó vieja y si una asignación es reciente.
        'actualizado': _fecha(crudo.get('actualizado')),
        'viaje': _viaje(crudo.get('viaje')),
    }


def resumen_de(servicio):
    """"Entrega de pedido: Planta Caldas → Obra La Ceja".

    Se guarda junto al inicio porque cuando Odoo cierra el servicio sale de
    la consulta, y sin este texto el historial quedaría en un número que
    nadie reconoce.
    """
    tramo = ' → '.join(p for p in (servicio.get('origen'),
                                   servicio.get('destino')) if p)
    partes = [servicio.get('tipo_display') or 'Servicio']
    if tramo:
        partes.append(tramo)
    return ': '.join(partes)[:200]


def _marcar_iniciados(servicios):
    """Le cuelga a cada servicio su inicio, si el conductor ya salió.

    Una sola consulta para toda la lista: se filtra por los ids de Odoo y
    el cruce fino —modelo e id— se hace en memoria.
    """
    from .models import ServicioIniciado

    ids = [s['odoo_id'] for s in servicios]
    por_clave = {}
    if ids:
        for inicio in (ServicioIniciado.objects
                       .filter(odoo_id__in=ids, anulado_en__isnull=True)
                       .select_related('conductor', 'vehiculo')):
            por_clave[(inicio.odoo_modelo, inicio.odoo_id)] = inicio

    for s in servicios:
        s['inicio'] = por_clave.get((s['odoo_modelo'], s['odoo_id']))


def _marca(fecha):
    """Una fecha como número para ordenar; lo que no tiene, al final."""
    if not fecha:
        return (1, 0.0)
    try:
        return (0, fecha.timestamp())
    except (OverflowError, OSError, ValueError):
        return (1, 0.0)


def _se_muestra(servicio, hoy, viajes_abiertos):
    """Lo que el conductor tiene por hacer, más lo que cerró hoy.

    Un servicio finalizado de días atrás ya no es trabajo y solo alarga la
    lista. Se dejan los de hoy, para que vea lo que acaba de cerrar, y los
    de un viaje que todavía tiene paradas por entregar: el viaje se lee
    entero o no se entiende en qué parada va.
    """
    if servicio['estado'] == 'cancelado':
        return False
    if servicio['estado'] != 'finalizado':
        return True
    viaje = servicio['viaje']
    if viaje and viaje['odoo_id'] in viajes_abiertos:
        return True
    fin = servicio['fin_real']
    return bool(fin) and timezone.localtime(fin).date() == hoy


def _armar_viaje(entrada):
    """Lo que la pantalla necesita saber del viaje, calculado una vez.

    - `sin_iniciar`: las paradas que todavía no tienen salida en SIGHU. Si
      hay alguna, se ofrece «Iniciar viaje»; al iniciar se crean solo esas,
      así que tocar el botón dos veces no duplica nada.
    - `inicio_deshacible`: la salida que se puede deshacer, si se puede. Se
      deshace para todas las paradas a la vez, porque salieron juntas.
    """
    paradas = entrada['paradas']
    paradas.sort(key=lambda s: (s['viaje']['parada'] or 999, s['odoo_id']))
    # El encabezado es el mismo en todas las paradas; se toma el de la que
    # más paradas cuenta, por si una llegó con el dato de antes.
    entrada['viaje'] = max((p['viaje'] for p in paradas),
                           key=lambda v: v['total_paradas'])

    inicios = [p['inicio'] for p in paradas if p['inicio']]
    entrada['sin_iniciar'] = [
        p for p in paradas
        if not p['inicio'] and p['estado'] in ('asignado', 'en_curso')]
    entrada['iniciado_en'] = min((i.iniciado_en for i in inicios), default=None)
    entrada['kilometraje_salida'] = next(
        (i.kilometraje for i in inicios if i.kilometraje is not None), None)
    # Todas o ninguna: si una parada ya se entregó, deshacer la salida de
    # las demás dejaría un viaje medio salido. Primero se quita la entrega.
    entrada['inicio_deshacible'] = (
        inicios[0] if inicios and all(i.puede_deshacerse for i in inicios)
        else None)
    entrada['conflicto_salida'] = next(
        (i for i in inicios if i.conflicto_odoo), None)
    entrada['entregadas'] = sum(
        1 for p in paradas
        if (p['inicio'] and p['inicio'].esta_entregado)
        or p['estado'] == 'finalizado')
    total = entrada['viaje']['total_paradas'] or len(paradas)
    entrada['total'] = max(total, len(paradas))
    # Paradas que Odoo cuenta pero que no llegaron en la consulta (de otro
    # vehículo, o fuera de la ventana de fechas). Se dice, para que el
    # conductor no crea que el viaje tiene menos entregas de las que tiene.
    entrada['faltan_en_lista'] = max(total - len(paradas), 0)
    return entrada


def _entradas(servicios):
    """Los servicios de un vehículo, con los de un mismo viaje juntos.

    Cada entrada es un servicio suelto o un viaje con sus paradas. Se
    ordenan por la hora a la que hay que salir: la del viaje, o la
    programada del servicio.
    """
    entradas, por_viaje = [], {}
    for s in servicios:
        viaje = s['viaje']
        if not viaje:
            entradas.append({'es_viaje': False, 'servicio': s})
            continue
        entrada = por_viaje.get(viaje['odoo_id'])
        if entrada is None:
            entrada = {'es_viaje': True, 'paradas': []}
            por_viaje[viaje['odoo_id']] = entrada
            entradas.append(entrada)
        entrada['paradas'].append(s)

    for entrada in por_viaje.values():
        _armar_viaje(entrada)

    def orden(e):
        if e['es_viaje']:
            fecha = e['viaje']['salida'] or min(
                (p['fecha'] for p in e['paradas'] if p['fecha']), default=None)
            return (_marca(fecha), e['viaje']['numero'])
        return (_marca(e['servicio']['fecha']), e['servicio']['ref'])

    entradas.sort(key=orden)
    return entradas


def servicios_visibles(usuario):
    """Los servicios de los vehículos que este usuario puede ver.

    Devuelve `(grupos, error)`:

    - `grupos`: un renglón por vehículo visible, con sus entradas (servicios
      sueltos y viajes). El conductor solo tiene el suyo; el jefe y el
      director, los de sus conductores.
    - `error`: texto para la pantalla si no se pudo hablar con Odoo.

    Un servicio asignado a un vehículo de otra área simplemente no aparece.
    Lo que no tiene conductor tampoco: Odoo no lo manda, porque asignarlo
    es trabajo del coordinador en Odoo.
    """
    vehiculos = list(vehiculos_visibles(usuario)
                     .select_related('conductor')
                     .filter(activo=True)
                     .order_by('placa'))

    try:
        crudos = listar_servicios(estado=ESTADOS_CONSULTA,
                                  timeout=TIMEOUT_PANTALLA)
    except OdooTransporteError as e:
        logger.warning('No se pudieron consultar los servicios en Odoo: %s', e)
        return [], (
            'No se pudo consultar Odoo en este momento, así que no se '
            'pueden mostrar los servicios. Volvé a intentar en un rato; '
            'si sigue igual, avisale a sistemas.')

    hoy = timezone.localdate()
    servicios = [s for s in (normalizar(c) for c in crudos) if s]
    viajes_abiertos = {s['viaje']['odoo_id'] for s in servicios
                       if s['viaje'] and s['estado'] in ('asignado', 'en_curso')}
    servicios = [s for s in servicios if _se_muestra(s, hoy, viajes_abiertos)]
    for s in servicios:
        s['urgencia'] = _urgencia(s['fecha'], hoy)
        s['resumen'] = resumen_de(s)
    servicios.sort(key=lambda s: (_marca(s['fecha']), s['ref']))
    _marcar_iniciados(servicios)

    # Los botones son del conductor del vehículo, no de su jefe: el que sale
    # es él, y la hora tiene que ser la real.
    empleado = empleado_de(usuario)
    grupos = []
    for v in vehiculos:
        suyos = [s for s in servicios
                 if v.odoo_id and s['vehiculo_odoo_id'] == v.odoo_id]
        grupos.append({
            'vehiculo': v,
            'es_mi_vehiculo': bool(empleado) and v.conductor_id == empleado.pk,
            'servicios': suyos,
            'entradas': _entradas(suyos),
        })

    return grupos, None


def firma(grupos):
    """Una huella corta de lo que muestra la pantalla de servicios.

    La pantalla la guarda al abrirse y cada tanto pregunta la de ahora; si
    cambió, se recarga. Entra lo que cambia lo que el conductor ve o puede
    hacer: qué servicios hay, en qué estado, cuándo los tocó Odoo por
    última vez (destino, hora, paradas...) y lo que se marcó en SIGHU.
    No entra la urgencia en palabras, que cambia sola a medianoche.
    """
    partes = []
    for g in grupos:
        partes.append(f'v{g["vehiculo"].pk}')
        for s in g['servicios']:
            inicio = s.get('inicio')
            viaje = s['viaje']
            partes.append('|'.join(str(x) for x in (
                s['odoo_id'], s['estado'],
                s['actualizado'].isoformat() if s['actualizado'] else '',
                viaje['odoo_id'] if viaje else '',
                viaje['parada'] if viaje else '',
                viaje['total_paradas'] if viaje else '',
                inicio.pk if inicio else '',
                inicio.entregado_en.isoformat() if inicio and inicio.entregado_en else '',
                int(bool(inicio and inicio.conflicto_odoo)),
                int(bool(inicio and inicio.conflicto_odoo_entrega)),
            )))
    return hashlib.sha1('\n'.join(partes).encode()).hexdigest()[:16]
