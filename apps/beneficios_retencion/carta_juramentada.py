"""Generación de la carta juramentada de beneficios de retención.

Formato oficial con logo Construinmuniza. RRHH puede pedir ajustes finos
de texto después de usarlo con los primeros empleados.
"""
import io
import os
from datetime import date

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)


def _ruta_logo():
    """Busca el logo oficial en static/img/. Devuelve ruta absoluta o None."""
    for base in (
        getattr(settings, 'STATIC_ROOT', None),
        os.path.join(settings.BASE_DIR, 'static'),
        os.path.join(settings.BASE_DIR, 'staticfiles'),
    ):
        if not base:
            continue
        ruta = os.path.join(base, 'img', 'construinmuniza_logo.jpg')
        if os.path.exists(ruta):
            return ruta
    return None


MESES_ES = [
    '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
]


def _fecha_larga(d):
    if not d:
        return '—'
    return f'{d.day:02d} de {MESES_ES[d.month]} del {d.year}'


def _fmt_pesos(v):
    if v is None:
        return '—'
    return f'${v:,.0f}'.replace(',', '.')


def generar_carta_juramentada(tramite):
    """Devuelve bytes del PDF de la carta juramentada del trámite."""
    emp = tramite.empleado
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=LETTER,
        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
        topMargin=2.5 * cm, bottomMargin=2.5 * cm,
    )
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        'body', parent=styles['Normal'], fontName='Helvetica',
        fontSize=11, leading=15, alignment=TA_JUSTIFY, spaceAfter=8,
    )
    titulo = ParagraphStyle(
        'titulo', parent=styles['Title'], fontName='Helvetica-Bold',
        fontSize=13, alignment=TA_CENTER, spaceAfter=14, textColor=colors.HexColor('#1E3A5F'),
    )
    bold = ParagraphStyle(
        'bold', parent=body, fontName='Helvetica-Bold', spaceAfter=4,
    )
    small = ParagraphStyle(
        'small', parent=body, fontSize=9, textColor=colors.HexColor('#555'),
        alignment=TA_CENTER,
    )

    story = []

    # Encabezado con logo
    ruta_logo = _ruta_logo()
    if ruta_logo:
        try:
            logo = Image(ruta_logo, width=4.5 * cm, height=4.5 * cm, kind='proportional')
            logo.hAlign = 'CENTER'
            story.append(logo)
        except Exception:
            pass

    story.append(Paragraph('DECLARACIÓN JURAMENTADA PARA DEDUCCIÓN DE RETENCIÓN EN LA FUENTE', titulo))
    story.append(Paragraph(
        f'Construinmuniza S.A.S. &nbsp;·&nbsp; Madera inmunizada &nbsp;·&nbsp; '
        f'Expedida el {_fecha_larga(date.today())}',
        small,
    ))
    story.append(Spacer(1, 0.4 * cm))

    # Bloque del empleado
    datos_emp = [
        ['Empleado:', emp.nombre_completo],
        ['Documento:', f'{emp.tipo_documento} {emp.numero_documento}'],
        ['Cargo:', _cargo_actual(emp)],
        ['Sede:', str(emp.sede) if emp.sede_id else '—'],
    ]
    t = Table(datos_emp, colWidths=[3.5 * cm, 11.5 * cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))

    # Cuerpo declarativo
    story.append(Paragraph(
        'Yo, identificado como aparece al pie de mi firma, en mi calidad de trabajador '
        'de <b>Construinmuniza S.A.S.</b>, y con el fin de que la empresa pueda aplicar '
        'las deducciones correspondientes al cálculo de la retención en la fuente por '
        f'concepto de rentas de trabajo del año {tramite.anio_aplicacion}, '
        '<b>declaro bajo la gravedad del juramento</b> lo siguiente:',
        body,
    ))

    # Detalle del beneficio
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph('Beneficio declarado:', bold))

    detalle_rows = [
        ['Concepto:', tramite.get_tipo_display()],
        ['Año de aplicación:', str(tramite.anio_aplicacion)],
        ['Período del certificado:', str(tramite.periodo_certificado)],
    ]
    if tramite.valor is not None:
        detalle_rows.append([
            'Valor certificado:',
            f'{_fmt_pesos(tramite.valor)} ({tramite.get_periodicidad_display() or "anual"})',
        ])
    if tramite.observacion_empleado:
        detalle_rows.append(['Observación:', tramite.observacion_empleado])

    t = Table(detalle_rows, colWidths=[4.5 * cm, 10.5 * cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('LINEBELOW', (0, 0), (-1, -1), 0.3, colors.HexColor('#CBD5E1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4 * cm))

    # Dependientes (si aplica)
    dependientes = list(tramite.dependientes.all())
    if dependientes:
        story.append(Paragraph('Dependientes reportados:', bold))
        rows = [['#', 'Nombre', 'Documento', 'Parentesco', 'Causal']]
        for i, d in enumerate(dependientes, 1):
            rows.append([str(i), d.nombres, d.numero_documento or '—',
                         d.parentesco or '—', d.get_causal_display()])
        t = Table(rows, colWidths=[0.8 * cm, 5.2 * cm, 3 * cm, 2.5 * cm, 3.5 * cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A5F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3 * cm))

    # Cláusulas juramentadas
    story.append(Paragraph(
        '<b>1.</b> Los datos y soportes entregados son veraces y corresponden a la '
        'realidad económica del suscrito. Los certificados aportados son originales o '
        'copias fieles del documento emitido por la entidad correspondiente.',
        body,
    ))
    story.append(Paragraph(
        '<b>2.</b> Me obligo a informar por escrito a Construinmuniza S.A.S. cualquier '
        'cambio que modifique la procedencia o el valor de la presente deducción '
        '(cancelación del servicio, cambio del titular, retiro del dependiente, etc.) '
        'dentro de los cinco (5) días hábiles siguientes a su ocurrencia.',
        body,
    ))
    story.append(Paragraph(
        '<b>3.</b> Autorizo a Construinmuniza S.A.S. a suspender la aplicación de esta '
        'deducción si detecta inconsistencias, si vencen los soportes o si no entrego '
        'a tiempo los certificados de renovación anual.',
        body,
    ))
    story.append(Paragraph(
        '<b>4.</b> Reconozco que la aplicación indebida de esta deducción, por errores '
        'u omisiones que me sean atribuibles, podrá ser recuperada por la empresa a '
        'través de descuento en nómina, sin perjuicio de las responsabilidades legales '
        'que se deriven ante la DIAN.',
        body,
    ))

    story.append(Spacer(1, 1.5 * cm))

    # Firma
    firma_rows = [
        ['_________________________________', ''],
        [emp.nombre_completo, ''],
        [f'{emp.tipo_documento} {emp.numero_documento}', ''],
        ['Firma del trabajador', ''],
    ]
    t = Table(firma_rows, colWidths=[9 * cm, 6 * cm])
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 3), (0, 3), colors.HexColor('#555')),
        ('FONTSIZE', (0, 3), (0, 3), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph(
        f'Documento generado electrónicamente por SIGHU — trámite {tramite.pk}',
        small,
    ))

    doc.build(story)
    return buffer.getvalue()


def _cargo_actual(empleado):
    hist = empleado.historialcargo_set.filter(activo=True).select_related('cargo').first()
    if hist and hist.cargo:
        return hist.cargo.nombre
    return '—'
