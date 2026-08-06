"""Generación de la carta de vacaciones en PDF.

Ver docs/INTEGRACION_ODOO_VACACIONES.md para el modelo de datos subyacente.
La carta funciona como constancia impresa de la solicitud aprobada que el
empleado descarga habiendo aceptado un checkbox de consentimiento.
"""

import io
from datetime import date, timedelta
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)

from .utils.dias_habiles import clasificar_rango, proximo_dia_habil


# Rango en días para considerar que una compensación en dinero pertenece al
# mismo período que la solicitud de tiempo (para combinarlas en una sola carta).
DIAS_CERCANIA_COMPENSACION = 15


MESES_ES = [
    '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
]


def _fecha_larga(d):
    """Formato 'DD de MES del AAAA' (ej: '21 de julio del 2026')."""
    if not d:
        return '—'
    return f'{d.day:02d} de {MESES_ES[d.month]} del {d.year}'


def _fecha_larga_may(d):
    """Formato con mes/año en MAYÚSCULAS (ej: '03 DE AGOSTO DE 2026')."""
    if not d:
        return '—'
    return f'{d.day:02d} DE {MESES_ES[d.month].upper()} DE {d.year}'


def _saldo_restante_al_dia(empleado, solicitud, dias_habiles_actual, dias_dinero_actual, compensacion_pareada):
    """Calcula el saldo de vacaciones que le queda al empleado tras aprobar
    esta solicitud (y su compensación pareada, si aplica).

    Odoo lleva el saldo en DÍAS HÁBILES, así que solo se descuentan hábiles
    y días en dinero — los festivos dentro del rango de la solicitud no
    consumen saldo.

    Cálculo:
        saldo_restante = saldo_al_corte
                         - habiles/dinero de la solicitud actual (+ compensación pareada)
                         - habiles/dinero de OTRAS solicitudes aprobadas después del corte

    Retorna Decimal o None si no hay saldo/corte guardado.
    """
    from .models import SolicitudVacacion

    if empleado.saldo_vacaciones_dias is None or empleado.saldo_vacaciones_fecha_corte is None:
        return None

    fecha_corte = empleado.saldo_vacaciones_fecha_corte
    saldo = Decimal(empleado.saldo_vacaciones_dias)

    # Descontar la solicitud actual (y su compensación pareada si vino en la misma carta)
    consumo_actual = Decimal(dias_habiles_actual) + Decimal(dias_dinero_actual)

    # Otras solicitudes aprobadas del empleado después del corte,
    # excluyendo la actual y su compensación pareada (ya contadas arriba).
    excluir_ids = {solicitud.pk}
    if compensacion_pareada:
        excluir_ids.add(compensacion_pareada.pk)

    otras = (
        SolicitudVacacion.objects
        .filter(empleado=empleado, estado_local='aprobada_rrhh')
        .exclude(pk__in=excluir_ids)
    )

    consumo_otras = Decimal(0)
    for otra in otras:
        if otra.tipo == 'tiempo' and otra.fecha_inicio and otra.fecha_fin:
            if otra.fecha_inicio > fecha_corte:
                clas_o = clasificar_rango(otra.fecha_inicio, otra.fecha_fin)
                consumo_otras += Decimal(clas_o['habiles'])
        elif otra.tipo == 'pago_dinero' and otra.fecha_lote_nomina:
            if otra.fecha_lote_nomina > fecha_corte:
                consumo_otras += (otra.dias_compensados or Decimal(0))

    restante = saldo - consumo_actual - consumo_otras
    # No mostramos saldos negativos en la carta (Odoo maneja las reglas duras);
    # si sale negativo lo mostramos como 0 y confiamos en el bloqueo de Odoo.
    if restante < 0:
        restante = Decimal(0)
    return restante


def buscar_compensacion_del_periodo(solicitud):
    """Retorna una SolicitudVacacion de tipo=pago_dinero cercana en el tiempo
    a la solicitud de tiempo dada, o None si no hay.

    Cercanía: la fecha_lote_nomina de la compensación cae a menos de
    DIAS_CERCANIA_COMPENSACION días de fecha_inicio o fecha_fin de la solicitud.
    """
    from .models import SolicitudVacacion

    if solicitud.tipo != 'tiempo' or not solicitud.fecha_inicio:
        return None

    ventana_ini = solicitud.fecha_inicio - timedelta(days=DIAS_CERCANIA_COMPENSACION)
    ventana_fin = (solicitud.fecha_fin or solicitud.fecha_inicio) + timedelta(days=DIAS_CERCANIA_COMPENSACION)

    return (
        SolicitudVacacion.objects
        .filter(
            empleado=solicitud.empleado,
            tipo='pago_dinero',
            estado_local='aprobada_rrhh',
            fecha_lote_nomina__gte=ventana_ini,
            fecha_lote_nomina__lte=ventana_fin,
        )
        .order_by('-fecha_creacion')
        .first()
    )


def _construir_estilos():
    base = getSampleStyleSheet()
    return {
        'body': ParagraphStyle(
            'body', parent=base['BodyText'],
            fontSize=11, leading=15, alignment=TA_JUSTIFY, spaceAfter=8,
        ),
        'meta': ParagraphStyle(
            'meta', parent=base['Normal'],
            fontSize=11, leading=14,
        ),
        'destinatario': ParagraphStyle(
            'destinatario', parent=base['Normal'],
            fontSize=11, leading=14,
        ),
        'asunto': ParagraphStyle(
            'asunto', parent=base['Normal'],
            fontSize=12, leading=15, alignment=TA_CENTER,
            spaceBefore=14, spaceAfter=14, fontName='Helvetica-Bold',
        ),
        'linea_desglose': ParagraphStyle(
            'linea_desglose', parent=base['Normal'],
            fontSize=11, leading=16, spaceAfter=2,
        ),
        'total': ParagraphStyle(
            'total', parent=base['Normal'],
            fontSize=12, leading=16, spaceBefore=6, spaceAfter=12,
            fontName='Helvetica-Bold',
        ),
        'nota': ParagraphStyle(
            'nota', parent=base['BodyText'],
            fontSize=10.5, leading=14, alignment=TA_JUSTIFY, spaceAfter=8,
        ),
        'firma_label': ParagraphStyle(
            'firma_label', parent=base['Normal'],
            fontSize=10, leading=13, alignment=TA_CENTER,
        ),
    }


def generar_carta_vacaciones(solicitud):
    """Genera el PDF de la carta de vacaciones. Retorna bytes.

    La solicitud debe estar en estado 'aprobada_rrhh'. Si es tipo=tiempo y
    existe una compensación en dinero del mismo período, se incluye como
    línea adicional.
    """
    empleado = solicitud.empleado
    hoy = date.today()
    ciudad = (empleado.sede.nombre if empleado.sede else 'Caldas').strip()

    # Desglose
    if solicitud.tipo == 'tiempo' and solicitud.fecha_inicio and solicitud.fecha_fin:
        clas = clasificar_rango(solicitud.fecha_inicio, solicitud.fecha_fin)
        dias_habiles = clas['habiles']
        dias_no_habiles = clas['festivos']
        fecha_regreso = proximo_dia_habil(solicitud.fecha_fin)
    else:
        dias_habiles = 0
        dias_no_habiles = 0
        fecha_regreso = None

    # Compensación en dinero del mismo período (si aplica)
    compensacion = buscar_compensacion_del_periodo(solicitud) if solicitud.tipo == 'tiempo' else None
    dias_dinero = Decimal('0')
    valor_dinero = Decimal('0')
    fecha_lote = None
    if solicitud.tipo == 'pago_dinero':
        dias_dinero = solicitud.dias_compensados or Decimal('0')
        valor_dinero = solicitud.valor_compensacion or Decimal('0')
        fecha_lote = solicitud.fecha_lote_nomina
    elif compensacion:
        dias_dinero = compensacion.dias_compensados or Decimal('0')
        valor_dinero = compensacion.valor_compensacion or Decimal('0')
        fecha_lote = compensacion.fecha_lote_nomina

    total_dias = Decimal(dias_habiles) + Decimal(dias_no_habiles) + dias_dinero

    # Documento
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=LETTER,
        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
        topMargin=2.5 * cm, bottomMargin=2.5 * cm,
        title=f'Carta vacaciones {empleado.nombre_completo}',
        author='Construinmuniza — SIGHU',
    )
    st = _construir_estilos()
    story = []

    # Encabezado: ciudad + fecha
    story.append(Paragraph(f'{ciudad}, {_fecha_larga(hoy)}', st['meta']))
    story.append(Spacer(1, 0.8 * cm))

    # Destinatario
    doc_num = empleado.numero_documento
    story.append(Paragraph('Señor(a)', st['destinatario']))
    story.append(Paragraph(f'<b>{empleado.nombre_completo.upper()}</b>', st['destinatario']))
    story.append(Paragraph(f'<b>CC {doc_num}</b>', st['destinatario']))

    # Asunto
    if solicitud.tipo == 'pago_dinero':
        asunto = 'Asunto: Compensación de vacaciones en dinero'
    elif compensacion:
        asunto = 'Asunto: Vacaciones disfrutadas en dinero y/o hábiles'
    else:
        asunto = 'Asunto: Vacaciones disfrutadas'
    story.append(Paragraph(asunto, st['asunto']))

    # Cuerpo principal
    if solicitud.tipo == 'tiempo':
        rango_txt = (
            f'({_fecha_larga(solicitud.fecha_inicio)} al '
            f'{_fecha_larga(solicitud.fecha_fin)})'
        )
        parrafo = (
            f'Por medio de la presente se le informa que según su solicitud de '
            f'vacaciones serán otorgadas <b>{dias_habiles}</b> días hábiles '
            f'distribuidos así {rango_txt}'
        )
        if compensacion and dias_dinero > 0:
            parrafo += (
                f' y <b>{int(dias_dinero):02d}</b> días en dinero según la '
                f'verificación correspondiente, los cuales serán pagados '
                f'en el lote de nómina del <b>{_fecha_larga(fecha_lote)}</b>'
            )
        parrafo += '. '
        if fecha_regreso:
            parrafo += f'Regresa el <b>{_fecha_larga_may(fecha_regreso)}</b> en su horario habitual.'
        story.append(Paragraph(parrafo, st['body']))
    else:
        # tipo=pago_dinero (compensación pura, sin días de tiempo)
        parrafo = (
            f'Por medio de la presente se le informa que se le aplicó una '
            f'compensación de vacaciones en dinero por <b>{int(dias_dinero):02d}</b> '
            f'días, por valor de <b>${valor_dinero:,.0f}</b>, en el lote de '
            f'nómina del <b>{_fecha_larga(fecha_lote)}</b>.'
        ).replace(',', '.')
        story.append(Paragraph(parrafo, st['body']))

    story.append(Spacer(1, 0.3 * cm))

    # Desglose de días
    if solicitud.tipo == 'tiempo':
        story.append(Paragraph(f'<b>{dias_habiles:02d}</b>&nbsp;&nbsp;días hábiles', st['linea_desglose']))
        story.append(Paragraph(f'<b>{dias_no_habiles:02d}</b>&nbsp;&nbsp;días festivos', st['linea_desglose']))
    if dias_dinero > 0:
        story.append(Paragraph(f'<b>{int(dias_dinero):02d}</b>&nbsp;&nbsp;días en dinero', st['linea_desglose']))
    story.append(Paragraph(f'<b>Total: {int(total_dias)} días</b>', st['total']))

    # Nota del saldo restante — se calcula descontando los días hábiles
    # (y compensados en dinero) de esta solicitud y de otras solicitudes ya
    # aprobadas después del corte. Odoo lleva el saldo en hábiles, así que
    # los festivos incluidos en el rango NO consumen saldo.
    restante = _saldo_restante_al_dia(
        empleado, solicitud, dias_habiles, dias_dinero, compensacion,
    )
    if restante is not None:
        saldo_txt = f'{restante:.1f}'.rstrip('0').rstrip('.')
        story.append(Paragraph(
            f'<b>NOTA:</b> Recuerde que le quedan <b>{saldo_txt} días</b> '
            f'hábiles por pagar y disfrutar.',
            st['nota'],
        ))

    story.append(Spacer(1, 1.5 * cm))

    # Firmas — dos columnas
    firma_data = [
        [
            Paragraph('Firma RRHH', st['firma_label']),
            Paragraph('Firma empleado', st['firma_label']),
        ],
        [
            Paragraph('&nbsp;', st['firma_label']),
            Paragraph('&nbsp;', st['firma_label']),
        ],
        [
            Paragraph('_______________________', st['firma_label']),
            Paragraph('_______________________', st['firma_label']),
        ],
        [
            Paragraph('<b>Talento Humano</b>', st['firma_label']),
            Paragraph(f'<b>{empleado.nombre_completo}</b><br/>CC {doc_num}', st['firma_label']),
        ],
    ]
    firma_tbl = Table(firma_data, colWidths=[8 * cm, 8 * cm])
    firma_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(KeepTogether(firma_tbl))

    # Pie discreto con constancia
    story.append(Spacer(1, 1.2 * cm))
    pie_texto = (
        f'<font size=8 color="#6c757d"><i>Documento generado por SIGHU '
        f'el {hoy.strftime("%d/%m/%Y")} como constancia de la solicitud '
        f'{solicitud.pk}. El empleado declaró estar al tanto de sus '
        f'vacaciones aprobadas al descargar este documento.</i></font>'
    )
    story.append(Paragraph(pie_texto, st['firma_label']))

    doc.build(story)
    return buf.getvalue()
