"""¿La licencia de conducción del conductor está al día?

SIGHU ya guardaba la licencia como un documento más del empleado, con su
fecha de vencimiento y su aviso a 30 días. Lo que faltaba era mirarla donde
importa: al lado del conductor al que se le entrega un camión. Tener el
papel cargado no es lo mismo que tenerlo vigente, y el módulo de transporte
no la estaba consultando en ningún lado.

Dos cosas se miran por separado porque fallan por separado:

- La vigencia: si la fecha ya pasó, el conductor no puede manejar y punto.
- La aprobación: una licencia que nadie de Talento Humano revisó es un
  archivo que el empleado subió. Puede estar perfecta, pero nadie lo ha
  verificado, y eso es justo lo que el aviso de vencimientos ignora, porque
  solo mira las aprobadas.
"""
import logging
from datetime import date

from django.db.models import F

logger = logging.getLogger(__name__)

# Código del tipo de documento en `TipoDocumentoEmpleado`.
CODIGO_LICENCIA = 'LIC_CONDUCIR'

# El mismo margen que usan los documentos del vehículo: un trámite de
# tránsito puede necesitar cita y examen médico.
DIAS_AVISO = 30

# Las claves ordenadas de lo más grave a lo más tranquilo. Sirve para
# ordenar listados por urgencia sin repetir el criterio en cada vista.
GRAVEDAD = ('sin_licencia', 'vencida', 'sin_fecha', 'por_vencer', 'vigente')


def _documento_de(empleado):
    """La licencia que vale para este empleado, si tiene alguna.

    Si hay varias —una renovación cargada sobre la anterior— vale la de
    vencimiento más lejano; las sin fecha quedan de últimas porque no
    prueban vigencia.
    """
    from apps.documents.models import DocumentoEmpleado

    return (DocumentoEmpleado.objects
            .filter(empleado=empleado,
                    tipo_documento__codigo=CODIGO_LICENCIA)
            .select_related('tipo_documento')
            .order_by(F('fecha_vencimiento').desc(nulls_last=True),
                      '-fecha_carga')
            .first())


def estado_licencia(empleado, hoy=None):
    """Cómo está la licencia de este empleado.

    Devuelve siempre un diccionario, nunca None, para que las plantillas no
    tengan que preguntarlo dos veces:

        clave      sin_licencia | vencida | sin_fecha | por_vencer | vigente
        texto      para mostrar tal cual
        documento  el DocumentoEmpleado, o None
        dias       días para vencer (negativo si ya venció), o None
        al_dia     False cuando no se puede dejar manejar a esta persona
        aprobada   si Talento Humano la revisó
    """
    return estado_licencia_de_documento(_documento_de(empleado), hoy)


def estados_de(empleados, hoy=None):
    """Lo mismo para varios, en una sola consulta.

    Los listados muestran la flota entera; preguntar documento por documento
    haría una consulta por conductor.
    """
    from apps.documents.models import DocumentoEmpleado

    hoy = hoy or date.today()
    empleados = list(empleados)
    if not empleados:
        return {}

    mejor = {}
    for doc in (DocumentoEmpleado.objects
                .filter(empleado__in=empleados,
                        tipo_documento__codigo=CODIGO_LICENCIA)
                .order_by(F('fecha_vencimiento').desc(nulls_last=True),
                          '-fecha_carga')):
        # El primero de cada empleado ya es el que vale, por el orden.
        mejor.setdefault(doc.empleado_id, doc)

    return {e.pk: estado_licencia_de_documento(mejor.get(e.pk), hoy)
            for e in empleados}


def estado_licencia_de_documento(doc, hoy=None):
    """La misma lectura, partiendo de un documento ya traído."""
    hoy = hoy or date.today()
    if doc is None:
        return {'clave': 'sin_licencia', 'texto': 'Sin licencia cargada',
                'documento': None, 'dias': None, 'al_dia': False,
                'aprobada': False}

    aprobada = doc.estado_aprobacion == 'aprobado'
    if doc.fecha_vencimiento is None:
        return {'clave': 'sin_fecha',
                'texto': 'Licencia sin fecha de vencimiento',
                'documento': doc, 'dias': None, 'al_dia': False,
                'aprobada': aprobada}

    dias = (doc.fecha_vencimiento - hoy).days
    if dias < 0:
        return {'clave': 'vencida',
                'texto': f'Licencia vencida hace {abs(dias)} '
                         f'día{"s" if abs(dias) != 1 else ""}',
                'documento': doc, 'dias': dias, 'al_dia': False,
                'aprobada': aprobada}
    if dias <= DIAS_AVISO:
        return {'clave': 'por_vencer',
                'texto': ('Licencia vence hoy' if dias == 0
                          else f'Licencia vence en {dias} '
                               f'día{"s" if dias != 1 else ""}'),
                'documento': doc, 'dias': dias, 'al_dia': True,
                'aprobada': aprobada}
    return {'clave': 'vigente',
            'texto': f'Licencia vigente hasta el {doc.fecha_vencimiento:%d/%m/%Y}',
            'documento': doc, 'dias': dias, 'al_dia': True,
            'aprobada': aprobada}


def conductores_sin_licencia_al_dia(hoy=None):
    """Conductores vigentes que hoy no deberían estar manejando.

    Incluye a los que no tienen licencia cargada y a los que la tienen sin
    fecha: en los dos casos SIGHU no puede afirmar que esté al día, y eso
    es tan reportable como una vencida.
    """
    from .permisos import conductores_vigentes

    hoy = hoy or date.today()
    conductores = list(conductores_vigentes().order_by('apellidos', 'nombres'))
    estados = estados_de(conductores, hoy)
    return [(e, estados[e.pk]) for e in conductores
            if not estados[e.pk]['al_dia']]
