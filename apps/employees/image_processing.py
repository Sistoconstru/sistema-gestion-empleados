# =============================================================================
# apps/employees/image_processing.py - Procesamiento de imágenes
# =============================================================================

from PIL import Image, ImageDraw, ImageFont
import json
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
import logging

logger = logging.getLogger(__name__)


def renderizar_texto_en_imagen(imagen_file, titulo, contenido, estilos):
    """
    Renderiza texto sobre una imagen usando Pillow.

    Args:
        imagen_file: Archivo de imagen (ImageField o UploadedFile)
        titulo: Título a renderizar
        contenido: Contenido a renderizar
        estilos: Dict con estilos (font_size, font_family, text_color, etc.)

    Returns:
        InMemoryUploadedFile con la imagen procesada
    """
    try:
        # Abrir imagen original
        img = Image.open(imagen_file)

        # Convertir a RGB si es necesario (para PNGs con transparencia)
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img

        # Obtener dimensiones de imagen
        ancho, alto = img.size

        # Extraer posicionamiento en píxeles
        text_position_x_px = estilos.get('text_position_x_px', 20)
        text_position_y_px = estilos.get('text_position_y_px', 20)

        # Extraer estilos de texto
        font_size_str = estilos.get('font_size', '1rem')
        font_family = estilos.get('font_family', 'Arial')
        text_color = estilos.get('text_color', '#000000')
        background_opacity = estilos.get('background_opacity', 100)

        # Convertir font_size a píxeles
        font_size_px = 16  # default
        if isinstance(font_size_str, str):
            if 'px' in font_size_str:
                font_size_px = int(font_size_str.replace('px', ''))
            elif 'rem' in font_size_str:
                font_size_px = int(float(font_size_str.replace('rem', '')) * 16)

        # Escalar tamaño de fuente proporcionalmente a la imagen
        # Si la imagen es muy grande, aumentar el tamaño de fuente
        image_scale = ancho / 600  # 600px es tamaño de referencia
        font_size_px = max(10, int(font_size_px * image_scale))  # Mínimo 10px

        # Intentar cargar fuente del sistema
        font = None

        # Mapeo de nombres de fuentes a archivos
        font_mapping = {
            'Arial': ['arial.ttf', 'Arial.ttf', 'LiberationSans-Regular.ttf'],
            'Times New Roman': ['times.ttf', 'Times New Roman.ttf', 'LiberationSerif-Regular.ttf'],
            'Courier New': ['cour.ttf', 'Courier New.ttf', 'LiberationMono-Regular.ttf'],
            'Georgia': ['georgia.ttf', 'Georgia.ttf'],
            'Verdana': ['verdana.ttf', 'Verdana.ttf'],
            'Comic Sans MS': ['comic.ttf', 'Comic Sans MS.ttf'],
        }

        # Rutas de búsqueda para diferentes sistemas operativos
        search_paths = [
            # Windows
            f"C:\\Windows\\Fonts",
            # Linux
            "/usr/share/fonts/truetype",
            "/usr/share/fonts/truetype/dejavu",
            "/usr/share/fonts/truetype/liberation",
            # macOS
            "/Library/Fonts",
            "/System/Library/Fonts",
        ]

        # Intentar encontrar la fuente
        font_names = font_mapping.get(font_family, [font_family + '.ttf', font_family + '.ttc'])

        for search_path in search_paths:
            if not font:
                for font_name in font_names:
                    try:
                        font_path = f"{search_path}/{font_name}"
                        font = ImageFont.truetype(font_path, font_size_px)
                        logger.info(f"Fuente cargada: {font_path}")
                        break
                    except:
                        continue
            if font:
                break

        # Si no se encontró fuente, usar Arial genérico o fuente por defecto con tamaño
        if not font:
            try:
                # Intentar con Arial.ttf directamente
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size_px)
                logger.warning(f"Usando DejaVuSans como fallback para {font_family}")
            except:
                try:
                    # Windows fallback
                    font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", font_size_px)
                except:
                    # Último recurso - fuente por defecto (sin tamaño personalizado)
                    font = ImageFont.load_default()
                    logger.warning(f"No se pudo cargar fuente {font_family}, usando default del sistema")

        # Convertir color hex a RGB
        text_color_rgb = hex_a_rgb(text_color)

        # Crear capa de dibujo
        draw = ImageDraw.Draw(img, 'RGBA')

        # Dibujar título si existe
        y_offset = text_position_y_px
        if titulo:
            # Título en negrita
            titulo_text = f"📢 {titulo}"
            draw.text((text_position_x_px, y_offset), titulo_text, fill=text_color_rgb, font=font)
            y_offset += int(font_size_px * 1.5)

        # Dibujar contenido línea por línea
        for linea in contenido.split('\n'):
            draw.text((text_position_x_px, y_offset), linea, fill=text_color_rgb, font=font)
            y_offset += int(font_size_px * 1.3)

        # Guardar imagen en buffer
        img_io = io.BytesIO()
        img.save(img_io, format='PNG', quality=95)
        img_io.seek(0)

        # Crear InMemoryUploadedFile
        archivo_procesado = InMemoryUploadedFile(
            img_io,
            'ImageField',
            'anuncio_renderizado.png',
            'image/png',
            img_io.getbuffer().nbytes,
            None
        )

        logger.info(f"Imagen procesada exitosamente: {ancho}x{alto}")

        return archivo_procesado

    except Exception as e:
        logger.error(f"Error al renderizar texto en imagen: {e}")
        # Retornar imagen original si hay error
        return imagen_file


def hex_a_rgb(hex_color):
    """
    Convierte color hex a tupla RGB.

    Args:
        hex_color: String en formato '#RRGGBB' o 'RRGGBB'

    Returns:
        Tupla (R, G, B) con valores 0-255
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (0, 0, 0)  # Default black


def limpiar_estilos_posicionamiento(estilos):
    """
    Elimina campos de posicionamiento después de renderizar en servidor.

    Args:
        estilos: Dict con estilos

    Returns:
        Dict actualizado sin posicionamiento
    """
    campos_eliminar = [
        'text_position_x_px',
        'text_position_y_px',
        'text_position_x',
        'text_position_y',
        'imagen_ancho',
        'imagen_alto'
    ]

    for campo in campos_eliminar:
        estilos.pop(campo, None)

    return estilos
