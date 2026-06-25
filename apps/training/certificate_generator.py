"""
Servicio de generación de certificados PDF.

Una sola implementación de render (`_render_pdf_bytes`) compartida entre:
- Descarga real del empleado (vía `generar_certificado(inscripcion)`).
- Vista previa de admin (vía `generar_preview_bytes(plantilla)`), con marca de
  agua "VISTA PREVIA" y datos de ejemplo.

Mantener un solo render evita que la previsualización divergiera del PDF real.
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.utils import timezone
from io import BytesIO
import os
import logging
import tempfile

logger = logging.getLogger(__name__)


def get_file_for_reportlab(file_field):
    """Devuelve (path, is_temp) que ReportLab puede usar para dibujar.

    Para storage local devuelve `file_field.path`. Para S3 descarga a un temporal
    que el caller debe eliminar después.
    """
    if not file_field:
        return None, False
    try:
        if hasattr(file_field, 'path'):
            try:
                local_path = file_field.path
                if os.path.exists(local_path):
                    return local_path, False
            except NotImplementedError:
                pass
    except Exception as e:
        logger.debug(f"No se pudo acceder a path local: {e}")

    try:
        ext = os.path.splitext(file_field.name)[1] or '.tmp'
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        with file_field.open('rb') as f:
            temp_file.write(f.read())
        temp_file.close()
        return temp_file.name, True
    except Exception as e:
        logger.error(f"Error leyendo archivo desde S3: {e}")
        return None, False


class CertificateGenerator:
    """Generador de certificados PDF usando plantillas configurables."""

    @staticmethod
    def _render_pdf_bytes(plantilla, datos, is_preview=False):
        """Renderiza el PDF y devuelve sus bytes. No persiste nada.

        Args:
            plantilla: CertificadoPlantilla
            datos: dict con claves nombre_empleado, documento_empleado,
                   capacitacion_nombre, duracion_horas, puntaje,
                   numero_certificado, fecha_emision (datetime).
            is_preview: si True, agrega marca de agua "VISTA PREVIA".
        """
        archivos_temporales = []
        try:
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=landscape(A4))
            width, height = landscape(A4)

            # Paleta
            color_dorado = colors.HexColor('#B8860B')
            color_azul_oscuro = colors.HexColor('#1a3a52')
            color_principal = color_azul_oscuro
            color_texto = colors.HexColor('#2c2c2c')
            color_texto_claro = colors.HexColor('#666666')

            # ===== FONDO =====
            if plantilla.imagen_fondo:
                fondo_path, is_temp = get_file_for_reportlab(plantilla.imagen_fondo)
                if fondo_path:
                    if is_temp:
                        archivos_temporales.append(fondo_path)
                    try:
                        c.drawImage(fondo_path, 0, 0, width=width, height=height,
                                    preserveAspectRatio=False, mask='auto')
                    except Exception as e:
                        logger.error(f"Error dibujando fondo: {e}")

            # ===== MARCO (si no hay fondo) =====
            if not plantilla.imagen_fondo:
                c.setStrokeColor(color_dorado)
                c.setLineWidth(4)
                c.rect(0.4*inch, 0.4*inch, width - 0.8*inch, height - 0.8*inch)
                c.setLineWidth(1)
                c.rect(0.5*inch, 0.5*inch, width - 1*inch, height - 1*inch)

            # ===== LOGO =====
            if plantilla.logo:
                logo_path, is_temp = get_file_for_reportlab(plantilla.logo)
                if logo_path:
                    if is_temp:
                        archivos_temporales.append(logo_path)
                    try:
                        logo_width, logo_height = 2.4*inch, 1.2*inch
                        c.drawImage(
                            logo_path,
                            (width - logo_width) / 2,
                            height - 1.9*inch,
                            width=logo_width, height=logo_height,
                            preserveAspectRatio=True, mask='auto',
                        )
                    except Exception as e:
                        logger.error(f"Error dibujando logo: {e}")

            # Helper de wrap centrado
            max_text_width = width - 2.4*inch

            def draw_wrapped(text, font_name, font_size, y_start,
                             line_height=None, fill_color=None):
                c.setFont(font_name, font_size)
                if fill_color is not None:
                    c.setFillColor(fill_color)
                if line_height is None:
                    line_height = font_size * 1.25
                lines = []
                current = ""
                for word in (text or "").split():
                    candidate = f"{current} {word}".strip()
                    if c.stringWidth(candidate, font_name, font_size) <= max_text_width:
                        current = candidate
                    else:
                        if current:
                            lines.append(current)
                        current = word
                if current:
                    lines.append(current)
                y = y_start
                for line in lines:
                    c.drawCentredString(width/2, y, line)
                    y -= line_height
                return y

            # ===== TÍTULO =====
            c.setFont("Helvetica-Bold", 28)
            c.setFillColor(color_azul_oscuro)
            c.drawCentredString(width/2, height - 2.3*inch, plantilla.titulo_certificado.upper())

            # ===== TEXTO SUPERIOR (wrap) =====
            y = height - 3.0*inch
            y = draw_wrapped(plantilla.texto_superior, "Helvetica", 14, y, fill_color=color_texto)

            # ===== NOMBRE DEL EMPLEADO =====
            y -= 0.35*inch
            c.setFont("Helvetica-Bold", 22)
            c.setFillColor(color_principal)
            c.drawCentredString(width/2, y, datos['nombre_empleado'].upper())

            # ===== DOCUMENTO =====
            y -= 0.4*inch
            c.setFont("Helvetica", 12)
            c.setFillColor(color_texto)
            c.drawCentredString(width/2, y,
                                f"Documento de Identidad: {datos['documento_empleado']}")

            # ===== TEXTO INFERIOR (wrap) =====
            y -= 0.5*inch
            y = draw_wrapped(plantilla.texto_inferior, "Helvetica", 14, y, fill_color=color_texto)

            # ===== NOMBRE CAPACITACIÓN (wrap) =====
            y -= 0.4*inch
            y = draw_wrapped(datos['capacitacion_nombre'], "Helvetica-Bold", 16, y,
                             line_height=0.32*inch, fill_color=color_principal)
            y_siguiente = y - 0.2*inch

            # ===== INFO ADICIONAL =====
            info_lines = []
            if plantilla.incluir_duracion and datos.get('duracion_horas'):
                info_lines.append(f"Duración: {datos['duracion_horas']} horas")
            if plantilla.incluir_calificacion and datos.get('puntaje') is not None:
                info_lines.append(f"Calificación: {datos['puntaje']:.1f}/100")
            if info_lines:
                c.setFont("Helvetica", 11)
                c.setFillColor(color_texto)
                c.drawCentredString(width/2, y_siguiente, " • ".join(info_lines))

            # ===== Nº DE CERTIFICADO Y FECHA =====
            c.setFont("Helvetica", 10)
            c.setFillColor(color_texto)
            c.drawCentredString(width/2, y_siguiente - 0.5*inch,
                                f"Certificado Nº: {datos['numero_certificado']}")
            c.drawCentredString(width/2, y_siguiente - 0.7*inch,
                                f"Fecha de Emisión: {datos['fecha_emision'].strftime('%d de %B de %Y')}")

            # ===== FIRMAS =====
            y_firma = 1.6*inch

            # Izquierda: Responsable
            x_firma_izq = width / 4
            if plantilla.firma_responsable:
                firma_path, is_temp = get_file_for_reportlab(plantilla.firma_responsable)
                if firma_path:
                    if is_temp:
                        archivos_temporales.append(firma_path)
                    try:
                        c.drawImage(firma_path,
                                    x_firma_izq - 0.9*inch, y_firma + 0.3*inch,
                                    width=1.8*inch, height=0.6*inch,
                                    preserveAspectRatio=True, mask='auto')
                    except Exception as e:
                        logger.error(f"Error dibujando firma responsable: {e}")
            c.setStrokeColor(color_texto_claro)
            c.setLineWidth(1)
            c.line(x_firma_izq - 1.2*inch, y_firma + 0.2*inch,
                   x_firma_izq + 1.2*inch, y_firma + 0.2*inch)
            if plantilla.nombre_responsable:
                c.setFont("Helvetica-Bold", 10)
                c.setFillColor(color_texto)
                c.drawCentredString(x_firma_izq, y_firma, plantilla.nombre_responsable)
            if plantilla.cargo_responsable:
                c.setFont("Helvetica", 9)
                c.setFillColor(color_texto_claro)
                c.drawCentredString(x_firma_izq, y_firma - 0.2*inch, plantilla.cargo_responsable)

            # Derecha: RRHH
            x_firma_der = 3 * width / 4
            if plantilla.firma_rrhh:
                firma_rrhh_path, is_temp = get_file_for_reportlab(plantilla.firma_rrhh)
                if firma_rrhh_path:
                    if is_temp:
                        archivos_temporales.append(firma_rrhh_path)
                    try:
                        c.drawImage(firma_rrhh_path,
                                    x_firma_der - 0.9*inch, y_firma + 0.3*inch,
                                    width=1.8*inch, height=0.6*inch,
                                    preserveAspectRatio=True, mask='auto')
                    except Exception as e:
                        logger.error(f"Error dibujando firma RRHH: {e}")
            c.line(x_firma_der - 1.2*inch, y_firma + 0.2*inch,
                   x_firma_der + 1.2*inch, y_firma + 0.2*inch)
            if plantilla.nombre_rrhh:
                c.setFont("Helvetica-Bold", 10)
                c.setFillColor(color_texto)
                c.drawCentredString(x_firma_der, y_firma, plantilla.nombre_rrhh)
            if plantilla.cargo_rrhh:
                c.setFont("Helvetica", 9)
                c.setFillColor(color_texto_claro)
                c.drawCentredString(x_firma_der, y_firma - 0.2*inch, plantilla.cargo_rrhh)

            # ===== PIE =====
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.grey)
            c.drawCentredString(width/2, 0.3*inch,
                                "Este documento certifica la culminación exitosa de la capacitación mencionada")

            # ===== MARCA DE AGUA (solo preview) =====
            if is_preview:
                c.saveState()
                c.setFont("Helvetica-Bold", 80)
                c.setFillColor(colors.HexColor('#cccccc'))
                c.translate(width/2, height/2)
                c.rotate(30)
                c.drawCentredString(0, 0, "VISTA PREVIA")
                c.restoreState()

            c.save()
            buffer.seek(0)
            return buffer.getvalue()
        finally:
            for tmp in archivos_temporales:
                try:
                    if os.path.exists(tmp):
                        os.unlink(tmp)
                except Exception as e:
                    logger.warning(f"No se pudo eliminar temporal {tmp}: {e}")

    @staticmethod
    def emitir_certificado(inscripcion):
        """Marca la inscripción como certificada (asigna número + fecha de emisión).

        No genera ni guarda PDF: el archivo se renderiza al vuelo en cada descarga
        usando `renderizar_pdf_inscripcion`. Así modificar la plantilla (logo,
        firmas, fondo, textos) se refleja inmediatamente en lo que ve el empleado.

        Devuelve True si la emisión queda OK (número asignado), False si no
        cumple condiciones.
        """
        try:
            if inscripcion.capacitacion.es_externa():
                logger.warning(
                    f"emitir_certificado llamado para capacitación externa "
                    f"(inscripción {inscripcion.id}). Externos no se emiten desde aquí."
                )
                return False
            if not inscripcion.puede_generar_certificado():
                logger.debug(f"Inscripción {inscripcion.id} no cumple condiciones para emitir certificado")
                return False
            if not inscripcion.capacitacion.plantilla_certificado:
                logger.warning(f"Capacitación {inscripcion.capacitacion.codigo} no tiene plantilla; no se emite")
                return False

            update_fields = []
            if not inscripcion.numero_certificado:
                inscripcion.generar_numero_certificado()
                update_fields.append('numero_certificado')
            if not inscripcion.fecha_emision_certificado:
                inscripcion.fecha_emision_certificado = timezone.now()
                update_fields.append('fecha_emision_certificado')
            if update_fields:
                inscripcion.save(update_fields=update_fields)

            logger.info(
                f"Certificado emitido para inscripción {inscripcion.id} "
                f"(empleado {inscripcion.empleado.nombre_completo}, num={inscripcion.numero_certificado})"
            )
            return True
        except Exception as e:
            logger.error(f"Error emitiendo certificado para inscripción {inscripcion.id}: {e}")
            return False

    @staticmethod
    def renderizar_pdf_inscripcion(inscripcion):
        """Renderiza al vuelo el PDF del certificado de una inscripción.

        Devuelve los bytes del PDF. Llamado por la vista de descarga — siempre
        usa la plantilla y datos más recientes, así que cambios en el diseño se
        ven inmediatamente. Levanta excepción si no hay plantilla.
        """
        plantilla = inscripcion.capacitacion.plantilla_certificado
        if not plantilla:
            raise ValueError(
                f"Capacitación {inscripcion.capacitacion.codigo} no tiene plantilla de certificado"
            )
        datos = {
            'nombre_empleado': inscripcion.empleado.nombre_completo,
            'documento_empleado': inscripcion.empleado.numero_documento,
            'capacitacion_nombre': inscripcion.capacitacion.nombre,
            'duracion_horas': inscripcion.capacitacion.duracion_estimada_horas,
            'puntaje': inscripcion.puntaje_final,
            'numero_certificado': inscripcion.numero_certificado or 'SIN-ASIGNAR',
            'fecha_emision': inscripcion.fecha_emision_certificado or timezone.now(),
        }
        return CertificateGenerator._render_pdf_bytes(plantilla, datos, is_preview=False)

    @staticmethod
    def generar_preview_bytes(plantilla):
        """Genera los bytes de un PDF de previsualización (datos de ejemplo + watermark).

        Usado por la vista de admin para que RRHH vea exactamente cómo quedará el
        certificado real con esa plantilla.
        """
        datos = {
            'nombre_empleado': 'Juan Carlos Pérez García',
            'documento_empleado': '1.234.567.890',
            'capacitacion_nombre': plantilla.capacitacion.nombre,
            'duracion_horas': plantilla.capacitacion.duracion_estimada_horas,
            'puntaje': 95.0,
            'numero_certificado': 'CERT-PREVIEW-0001',
            'fecha_emision': timezone.now(),
        }
        return CertificateGenerator._render_pdf_bytes(plantilla, datos, is_preview=True)
