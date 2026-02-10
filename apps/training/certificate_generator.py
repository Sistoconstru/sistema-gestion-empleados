"""
Servicio de generación de certificados PDF
Genera certificados automáticamente al aprobar una capacitación
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from django.utils import timezone
from django.conf import settings
from io import BytesIO
import os
import logging
import tempfile

logger = logging.getLogger(__name__)


def get_file_for_reportlab(file_field):
    """
    Obtiene un archivo (ruta local o temporal) que ReportLab puede usar.
    Maneja tanto archivos locales (desarrollo) como remotos en S3 (producción).

    Similar al patrón usado con PIL/Pillow para documentos de empleado.

    Args:
        file_field: FileField o ImageField de Django

    Returns:
        tuple: (file_path, is_temp) donde file_path es la ruta utilizable
               e is_temp indica si debe eliminarse después de usar
    """
    if not file_field:
        return None, False

    try:
        # Intentar obtener path local (funciona en desarrollo con FileSystemStorage)
        if hasattr(file_field, 'path'):
            try:
                local_path = file_field.path
                if os.path.exists(local_path):
                    logger.debug(f"Usando archivo local: {local_path}")
                    return local_path, False
            except NotImplementedError:
                # El storage no soporta .path (S3, Google Cloud, etc.)
                pass
    except Exception as e:
        logger.debug(f"No se pudo acceder a path local: {str(e)}")

    # Si llegamos aquí, es un archivo remoto (S3) - leer y crear temporal
    try:
        logger.info(f"Leyendo archivo desde S3: {file_field.name}")

        # Determinar extensión
        ext = os.path.splitext(file_field.name)[1] or '.tmp'

        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)

        # Leer contenido desde S3 (igual que PIL con Image.open())
        with file_field.open('rb') as f:
            temp_file.write(f.read())

        temp_file.close()
        temp_path = temp_file.name

        logger.debug(f"Archivo temporal creado: {temp_path}")
        return temp_path, True

    except Exception as e:
        logger.error(f"Error leyendo archivo desde S3: {str(e)}")
        return None, False


class CertificateGenerator:
    """Generador de certificados PDF usando plantillas configurables"""

    @staticmethod
    def generar_certificado(inscripcion):
        """
        Genera un certificado PDF para una inscripción aprobada en capacitación INTERNA

        IMPORTANTE: Este método NO debe ser llamado para capacitaciones externas,
        ya que en esos casos el certificado es proporcionado por el proveedor externo.

        Args:
            inscripcion: InscripcionCapacitacion aprobada

        Returns:
            True si se generó correctamente, False en caso contrario
        """
        try:
            # VALIDACIÓN CRÍTICA: NO generar certificados para capacitaciones externas
            if inscripcion.capacitacion.es_externa():
                logger.error(
                    f"INTENTO DE GENERAR CERTIFICADO PARA CAPACITACIÓN EXTERNA - "
                    f"Inscripción: {inscripcion.id}, "
                    f"Capacitación: {inscripcion.capacitacion.nombre}. "
                    f"Los certificados externos deben ser proporcionados por el proveedor."
                )
                return False

            # Verificar que puede generar certificado
            if not inscripcion.puede_generar_certificado():
                logger.warning(f"Inscripción {inscripcion.id} no cumple condiciones para generar certificado")
                return False

            # Obtener plantilla
            plantilla = inscripcion.capacitacion.plantilla_certificado
            if not plantilla:
                logger.warning(f"Capacitación {inscripcion.capacitacion.codigo} no tiene plantilla de certificado")
                return False

            # Generar número de certificado único
            if not inscripcion.numero_certificado:
                inscripcion.generar_numero_certificado()

            # Lista para rastrear archivos temporales que deben eliminarse
            archivos_temporales = []

            # Crear PDF
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=landscape(A4))
            width, height = landscape(A4)

            # Configuración de colores (paleta sobria y elegante)
            color_dorado = colors.HexColor('#B8860B')  # Dorado oscuro
            color_azul_oscuro = colors.HexColor('#1a3a52')  # Azul oscuro elegante
            color_principal = color_azul_oscuro  # Color principal para títulos y destacados
            color_texto = colors.HexColor('#2c2c2c')  # Gris oscuro
            color_texto_claro = colors.HexColor('#666666')  # Gris medio

            # ===== IMAGEN DE FONDO (si existe) =====
            if plantilla.imagen_fondo:
                try:
                    fondo_path, is_temp = get_file_for_reportlab(plantilla.imagen_fondo)
                    if fondo_path:
                        if is_temp:
                            archivos_temporales.append(fondo_path)
                        # Dibujar la imagen de fondo cubriendo todo el certificado
                        c.drawImage(
                            fondo_path,
                            0,
                            0,
                            width=width,
                            height=height,
                            preserveAspectRatio=False,
                            mask='auto'
                        )
                except Exception as e:
                    logger.error(f"Error cargando imagen de fondo: {str(e)}")
                    # Si falla, continuar sin fondo

            # ===== MARCO SIMPLE (solo si NO hay imagen de fondo) =====
            if not plantilla.imagen_fondo:
                # Borde exterior dorado principal
                c.setStrokeColor(color_dorado)
                c.setLineWidth(4)
                c.rect(0.4*inch, 0.4*inch, width-0.8*inch, height-0.8*inch)

                # Borde interior más delgado
                c.setLineWidth(1)
                c.rect(0.5*inch, 0.5*inch, width-1*inch, height-1*inch)

            # ===== LOGO CENTRADO EN LA PARTE SUPERIOR =====
            if plantilla.logo:
                try:
                    logo_path, is_temp = get_file_for_reportlab(plantilla.logo)
                    if logo_path:
                        if is_temp:
                            archivos_temporales.append(logo_path)
                        # Tamaño del logo
                        logo_width = 2.4*inch
                        logo_height = 1.2*inch

                        # Calcular posición X para centrar (width/2 es el centro, restamos la mitad del ancho del logo)
                        logo_x = (width - logo_width) / 2
                        logo_y = height - 1.9*inch

                        c.drawImage(
                            logo_path,
                            logo_x,  # Centrado correctamente
                            logo_y,
                            width=logo_width,
                            height=logo_height,
                            preserveAspectRatio=True,
                            mask='auto'  # Soporte para transparencia
                        )
                except Exception as e:
                    logger.error(f"Error cargando logo: {str(e)}")

            # ===== TÍTULO DEL CERTIFICADO =====
            c.setFont("Helvetica-Bold", 28)
            c.setFillColor(color_azul_oscuro)
            c.drawCentredString(width/2, height - 2.3*inch, plantilla.titulo_certificado.upper())

           

            # Texto superior
            c.setFont("Helvetica", 14)
            c.setFillColor(color_texto)
            c.drawCentredString(width/2, height - 3.2*inch, plantilla.texto_superior)

            # Nombre del empleado (destacado)
            c.setFont("Helvetica-Bold", 22)
            c.setFillColor(color_principal)
            c.drawCentredString(
                width/2,
                height - 3.8*inch,
                inscripcion.empleado.nombre_completo.upper()
            )

            # Documento del empleado
            c.setFont("Helvetica", 12)
            c.setFillColor(color_texto)
            c.drawCentredString(
                width/2,
                height - 4.2*inch,
                f"Documento de Identidad: {inscripcion.empleado.numero_documento}"
            )

            # Texto inferior
            c.setFont("Helvetica", 14)
            c.drawCentredString(width/2, height - 4.7*inch, plantilla.texto_inferior)

            # Nombre de la capacitación
            c.setFont("Helvetica-Bold", 16)
            c.setFillColor(color_principal)
            # Dividir el nombre si es muy largo
            nombre_capacitacion = inscripcion.capacitacion.nombre
            if len(nombre_capacitacion) > 60:
                # Dividir en dos líneas
                palabras = nombre_capacitacion.split()
                mitad = len(palabras) // 2
                linea1 = ' '.join(palabras[:mitad])
                linea2 = ' '.join(palabras[mitad:])
                c.drawCentredString(width/2, height - 5.3*inch, linea1)
                c.drawCentredString(width/2, height - 5.6*inch, linea2)
                y_siguiente = height - 6.1*inch
            else:
                c.drawCentredString(width/2, height - 5.3*inch, nombre_capacitacion)
                y_siguiente = height - 5.8*inch

            # Información adicional
            c.setFont("Helvetica", 11)
            c.setFillColor(color_texto)

            info_lines = []
            if plantilla.incluir_duracion:
                info_lines.append(f"Duración: {inscripcion.capacitacion.duracion_estimada_horas} horas")

            if plantilla.incluir_calificacion and inscripcion.puntaje_final:
                info_lines.append(f"Calificación: {inscripcion.puntaje_final:.1f}/100")

            info_text = " • ".join(info_lines)
            c.drawCentredString(width/2, y_siguiente, info_text)

            # Número de certificado y fecha
            c.setFont("Helvetica", 10)
            fecha_actual = timezone.now()
            c.drawCentredString(
                width/2,
                y_siguiente - 0.5*inch,
                f"Certificado Nº: {inscripcion.numero_certificado}"
            )
            c.drawCentredString(
                width/2,
                y_siguiente - 0.7*inch,
                f"Fecha de Emisión: {fecha_actual.strftime('%d de %B de %Y')}"
            )

            # ===== SECCIÓN DE FIRMAS (DOS FIRMAS) =====
            y_firma = 1.6*inch

           

            # FIRMA IZQUIERDA: Responsable de la Capacitación
            x_firma_izq = width/4
            if plantilla.firma_responsable:
                try:
                    firma_path, is_temp = get_file_for_reportlab(plantilla.firma_responsable)
                    if firma_path:
                        if is_temp:
                            archivos_temporales.append(firma_path)
                        c.drawImage(
                            firma_path,
                            x_firma_izq - 0.9*inch,
                            y_firma + 0.3*inch,
                            width=1.8*inch,
                            height=0.6*inch,
                            preserveAspectRatio=True
                        )
                except Exception as e:
                    logger.error(f"Error cargando firma responsable: {str(e)}")

            # Línea para la firma izquierda
            c.setStrokeColor(color_texto_claro)
            c.setLineWidth(1)
            c.line(x_firma_izq - 1.2*inch, y_firma + 0.2*inch, x_firma_izq + 1.2*inch, y_firma + 0.2*inch)

            # Nombre y cargo del responsable
            if plantilla.nombre_responsable:
                c.setFont("Helvetica-Bold", 10)
                c.setFillColor(color_texto)
                c.drawCentredString(x_firma_izq, y_firma, plantilla.nombre_responsable)

            if plantilla.cargo_responsable:
                c.setFont("Helvetica", 9)
                c.setFillColor(color_texto_claro)
                c.drawCentredString(x_firma_izq, y_firma - 0.2*inch, plantilla.cargo_responsable)

            # FIRMA DERECHA: Director de Recursos Humanos
            x_firma_der = 3*width/4
            if plantilla.firma_rrhh:
                try:
                    firma_rrhh_path, is_temp = get_file_for_reportlab(plantilla.firma_rrhh)
                    if firma_rrhh_path:
                        if is_temp:
                            archivos_temporales.append(firma_rrhh_path)
                        c.drawImage(
                            firma_rrhh_path,
                            x_firma_der - 0.9*inch,
                            y_firma + 0.3*inch,
                            width=1.8*inch,
                            height=0.6*inch,
                            preserveAspectRatio=True
                        )
                except Exception as e:
                    logger.error(f"Error cargando firma RRHH: {str(e)}")

            # Línea para la firma derecha
            c.setStrokeColor(color_texto_claro)
            c.setLineWidth(1)
            c.line(x_firma_der - 1.2*inch, y_firma + 0.2*inch, x_firma_der + 1.2*inch, y_firma + 0.2*inch)

            # Nombre y cargo del Director de RRHH
            if plantilla.nombre_rrhh:
                c.setFont("Helvetica-Bold", 10)
                c.setFillColor(color_texto)
                c.drawCentredString(x_firma_der, y_firma, plantilla.nombre_rrhh)

            if plantilla.cargo_rrhh:
                c.setFont("Helvetica", 9)
                c.setFillColor(color_texto_claro)
                c.drawCentredString(x_firma_der, y_firma - 0.2*inch, plantilla.cargo_rrhh)

            # Pie de página
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.grey)
            c.drawCentredString(
                width/2,
                0.3*inch,
                "Este documento certifica la culminación exitosa de la capacitación mencionada"
            )

            # Finalizar PDF
            c.save()
            buffer.seek(0)

            # Guardar en el modelo
            filename = f"certificado_{inscripcion.numero_certificado}.pdf"
            inscripcion.certificado_generado.save(
                filename,
                ContentFile(buffer.getvalue()),
                save=False
            )
            inscripcion.fecha_emision_certificado = fecha_actual
            inscripcion.save()

            logger.info(
                f"Certificado generado exitosamente para inscripción {inscripcion.id} "
                f"(Empleado: {inscripcion.empleado.nombre_completo})"
            )
            return True

        except Exception as e:
            logger.error(f"Error generando certificado para inscripción {inscripcion.id}: {str(e)}")
            return False

        finally:
            # Limpiar archivos temporales descargados desde S3
            for temp_file in archivos_temporales:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                        logger.debug(f"Archivo temporal eliminado: {temp_file}")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar archivo temporal {temp_file}: {str(e)}")
