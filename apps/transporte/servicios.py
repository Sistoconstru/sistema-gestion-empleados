"""Los servicios asignados a cada vehículo, tal como los muestra SIGHU.

El tablero de servicios vive en Odoo: allá se crean, allá se les asigna el
vehículo y allá se cobran. SIGHU no los crea ni los modifica; los consulta
y los lista, para que el conductor sepa qué tiene asignado sin entrar a
Odoo y su jefe vea la carga de la flota.

El cruce es `vehiculo_id` de Odoo contra `Vehiculo.odoo_id`, y de ahí al
conductor que SIGHU tiene asignado. Odoo no manda conductor en el servicio
porque esa asignación es de SIGHU.

Se consulta en vivo. Si Odoo no responde no hay nada que mostrar, y eso se
dice en pantalla en vez de dejar un listado viejo que el conductor creería
vigente.
"""
import logging
from datetime import datetime

from django.utils import timezone

from .odoo_client import OdooTransporteError, listar_viajes_pendientes
from .permisos import empleado_de, es_admin_transporte, vehiculos_visibles

logger = logging.getLogger(__name__)

# Cuánto se espera a Odoo con alguien mirando la pantalla. El timeout
# general es de 30s, que para una página es una eternidad.
TIMEOUT_PANTALLA = 10

TIPOS = {
    'traslado_intersede': 'Traslado entre sedes',
    'entrega_venta': 'Entrega a cliente',
    'recepcion_materia_prima': 'Recepción de materia prima',
    'recepcion_compra': 'Recepción de materia prima',
}

# Los estados son de los documentos de Odoo. Se traducen a lo que significan
# para quien va a manejar, no al nombre técnico del modelo.
ESTADOS = {
    'draft': 'Borrador en Odoo',
    'borrador': 'Borrador en Odoo',
    'waiting': 'Esperando otra operación',
    'confirmed': 'Esperando inventario',
    'assigned': 'Listo para despachar',
    'done': 'Terminado',
    'cancel': 'Cancelado',
}


def _texto(valor):
    return (valor or '').strip() if isinstance(valor, str) else ''


def _texto_sede(bloque):
    """"Caldas · Existencias/VTAS" para un origen o destino interno."""
    if not isinstance(bloque, dict):
        return ''
    sede = bloque.get('sede') if isinstance(bloque.get('sede'), dict) else {}
    nombre = _texto(sede.get('nombre'))
    bodega = _texto(bloque.get('bodega'))
    if nombre and bodega:
        return f'{nombre} · {bodega}'
    return nombre or bodega


def _texto_lugar(bloque):
    """La dirección de una entrega.

    Se prefiere dirección y ciudad al nombre, porque el nombre del lugar es
    el del cliente y ese ya va en su propia columna: al conductor lo que le
    falta es para dónde arranca.
    """
    if not isinstance(bloque, dict):
        return ''
    lugar = bloque.get('lugar') if isinstance(bloque.get('lugar'), dict) else {}
    partes = [_texto(lugar.get('direccion')), _texto(lugar.get('ciudad'))]
    return ', '.join(p for p in partes if p) or _texto(lugar.get('nombre'))


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
    hoy. Y los atrasados tienen que saltar a la vista: en Odoo hay servicios
    programados hace meses que siguen sin despachar.
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


def normalizar(crudo):
    """Un servicio de Odoo en las pocas cosas que hay que mostrar.

    Se normaliza porque el payload cambia de forma según el tipo: un
    traslado entre sedes trae `sede` en origen y destino, y una entrega trae
    `lugar` con la dirección del cliente.
    """
    if not isinstance(crudo, dict):
        return None

    tipo = _texto(crudo.get('tipo'))
    estado = _texto(crudo.get('estado_documento'))
    cliente = crudo.get('cliente') if isinstance(crudo.get('cliente'), dict) else {}
    origen = crudo.get('origen') or {}
    destino = crudo.get('destino') or {}

    return {
        'ref': _texto(crudo.get('ref')),
        'tipo': tipo,
        'tipo_display': (TIPOS.get(tipo)
                         or tipo.replace('_', ' ').capitalize()
                         or 'Servicio'),
        'estado': estado,
        'estado_display': ESTADOS.get(estado) or estado.capitalize(),
        'pedido': _texto(crudo.get('pedido')),
        'fecha': _fecha(crudo.get('fecha_programada')),
        'origen': _texto_sede(origen) or _texto_lugar(origen),
        'destino': _texto_sede(destino) or _texto_lugar(destino),
        'cliente': _texto(cliente.get('nombre')),
        'cliente_nit': _texto(cliente.get('nit')),
        'toneladas': crudo.get('toneladas'),
        'distancia_km': crudo.get('distancia_km'),
        'vehiculo_odoo_id': crudo.get('vehiculo_id'),
        # La pareja que identifica el documento en Odoo. Es la clave con la
        # que se cruza el inicio que marca el conductor; `ref` es solo para
        # leerla.
        'odoo_modelo': _texto(crudo.get('odoo_modelo')),
        'odoo_id': crudo.get('odoo_id'),
    }


def resumen_de(servicio):
    """"Entrega a cliente: Caldas → Cra. 53 #96a-20, Medellín".

    Se guarda junto al inicio porque cuando Odoo cierra el documento el
    servicio desaparece de la consulta, y sin este texto el historial
    quedaría en un número de referencia que nadie reconoce.
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
    el cruce fino —modelo e id— se hace en memoria, que es más simple que
    armar un OR por cada servicio y da lo mismo con estos volúmenes.
    """
    from .models import ServicioIniciado

    ids = [s['odoo_id'] for s in servicios if s['odoo_id']]
    por_clave = {}
    if ids:
        for inicio in (ServicioIniciado.objects
                       .filter(odoo_id__in=ids, anulado_en__isnull=True)
                       .select_related('conductor', 'vehiculo')):
            por_clave[(inicio.odoo_modelo, inicio.odoo_id)] = inicio

    for s in servicios:
        s['inicio'] = por_clave.get((s['odoo_modelo'], s['odoo_id']))


def _orden(servicio):
    """Lo más viejo primero; lo que no tiene fecha, al final."""
    fecha = servicio['fecha']
    if not fecha:
        return (1, 0.0, servicio['ref'])
    try:
        return (0, fecha.timestamp(), servicio['ref'])
    except (OverflowError, OSError, ValueError):
        return (1, 0.0, servicio['ref'])


def servicios_visibles(usuario):
    """Los servicios de los vehículos que este usuario puede ver.

    Devuelve `(grupos, sin_vehiculo, error)`:

    - `grupos`: un renglón por vehículo visible, con sus servicios. El
      conductor solo tiene el suyo; el jefe y el director, los de sus
      conductores.
    - `sin_vehiculo`: los que Odoo todavía no le asignó a ningún vehículo.
      Solo se le muestran a quien administra la flota, y en una sección
      aparte: no son de nadie todavía, y si no se mostraran el coordinador
      se preguntaría dónde quedó el resto.
    - `error`: texto para la pantalla si no se pudo hablar con Odoo.

    Un servicio asignado a un vehículo de otra área simplemente no aparece.
    """
    vehiculos = list(vehiculos_visibles(usuario)
                     .select_related('conductor')
                     .filter(activo=True)
                     .order_by('placa'))

    try:
        crudos = listar_viajes_pendientes(timeout=TIMEOUT_PANTALLA)
    except OdooTransporteError as e:
        logger.warning('No se pudieron consultar los servicios en Odoo: %s', e)
        return [], [], (
            'No se pudo consultar Odoo en este momento, así que no se '
            'pueden mostrar los servicios. Volvé a intentar en un rato; '
            'si sigue igual, avisale a sistemas.')

    hoy = timezone.localdate()
    servicios = [s for s in (normalizar(c) for c in crudos) if s]
    for s in servicios:
        s['urgencia'] = _urgencia(s['fecha'], hoy)
        s['resumen'] = resumen_de(s)
    servicios.sort(key=_orden)
    _marcar_iniciados(servicios)

    # El botón de salida es del conductor del vehículo, no de su jefe: el
    # que sale es él, y la hora tiene que ser la real.
    empleado = empleado_de(usuario)
    grupos = [
        {'vehiculo': v,
         'es_mi_vehiculo': bool(empleado) and v.conductor_id == empleado.pk,
         'servicios': [s for s in servicios
                       if v.odoo_id and s['vehiculo_odoo_id'] == v.odoo_id]}
        for v in vehiculos
    ]

    sin_vehiculo = ([s for s in servicios if not s['vehiculo_odoo_id']]
                    if es_admin_transporte(usuario) else [])

    return grupos, sin_vehiculo, None
