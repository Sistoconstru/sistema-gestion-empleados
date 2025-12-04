# =============================================================================
# apps/employees/renderizado_anuncios.py - NUEVO SISTEMA DE RENDERIZADO
# =============================================================================
# Sistema mejorado para renderizar anuncios con texto en imágenes
# Utiliza Pillow (PIL) para crear imágenes con texto superpuesto

from PIL import Image, ImageDraw, ImageFont
import io
import os
import logging
from django.core.files.uploadedfile import InMemoryUploadedFile

logger = logging.getLogger(__name__)


def obtener_fuente(font_family, font_size_px, sistema='win'):
    """
    Obtiene la fuente del sistema o del proyecto.

    Args:
        font_family: Nombre de la fuente (Arial, Times New Roman, etc.)
        font_size_px: Tamaño en píxeles
        sistema: 'win', 'linux' o 'mac'

    Returns:
        Objeto ImageFont o fuente por defecto
    """

    font_mapping = {
        'Arial': ['arial.ttf', 'Arial.ttf', 'LiberationSans-Regular.ttf'],
        'Times New Roman': ['times.ttf', 'Times New Roman.ttf', 'LiberationSerif-Regular.ttf'],
        'Courier New': ['cour.ttf', 'Courier New.ttf', 'LiberationMono-Regular.ttf'],
        'Georgia': ['georgia.ttf', 'Georgia.ttf'],
        'Verdana': ['verdana.ttf', 'Verdana.ttf'],
        'Comic Sans MS': ['comic.ttf', 'Comic Sans MS.ttf'],
        'Twiggy': ['Twiggy.ttf', 'Chalkboy.ttf'],
        'Pinewood': ['Pinewood.ttf', 'PINEWOOD.TTF'],
    }

    search_paths = [
        # Fuentes del proyecto
        os.path.join(os.path.dirname(__file__), 'fonts'),
        # Windows
        "C:\\Windows\\Fonts",
        # Linux
        "/usr/share/fonts/truetype",
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/truetype/liberation",
        # macOS
        "/Library/Fonts",
        "/System/Library/Fonts",
    ]

    font_names = font_mapping.get(font_family, [font_family + '.ttf'])

    def buscar_fuente_case_insensitive(search_path, font_names):
        """Busca fuentes case-insensitive"""
        try:
            if not os.path.exists(search_path):
                return None
            archivos = {f.lower(): os.path.join(search_path, f)
                       for f in os.listdir(search_path)
                       if f.lower().endswith(('.ttf', '.ttc'))}
            for font_name in font_names:
                font_lower = font_name.lower()
                if font_lower in archivos:
                    return archivos[font_lower]
        except:
            pass
        return None

    # Intentar encontrar la fuente
    for search_path in search_paths:
        font_path = buscar_fuente_case_insensitive(search_path, font_names)
        if font_path:
            try:
                return ImageFont.truetype(font_path, font_size_px)
            except:
                continue

    # Fallback a DejaVuSans
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size_px)
    except:
        try:
            return ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", font_size_px)
        except:
            return ImageFont.load_default()


def hex_a_rgb(hex_color):
    """Convierte color hex a tupla RGB"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (0, 0, 0)


def calcular_font_size(ancho_cuadro_px, font_family, base_size_px=20):
    """
    Calcula automáticamente el tamaño de la fuente basado en el ancho del cuadro.
    Cuadros más anchos = letras más grandes.

    Args:
        ancho_cuadro_px: Ancho del cuadro de texto en píxeles
        font_family: Familia de fuente
        base_size_px: Tamaño base de referencia

    Returns:
        Tamaño de fuente en píxeles
    """
    # Fórmula: si el cuadro es muy ancho, aumentar la fuente
    # Escala lineal: cuadro de 300px = 20px, cuadro de 600px = 40px
    size = max(10, int((ancho_cuadro_px / 300) * base_size_px))
    return size


def ajustar_texto_a_ancho(texto, font, max_width, draw):
    """
    Divide el texto en líneas que caben en el ancho máximo.

    Args:
        texto: Texto a dividir
        font: Objeto ImageFont
        max_width: Ancho máximo en píxeles
        draw: Objeto ImageDraw para medir texto

    Returns:
        Lista de líneas que caben en el ancho máximo
    """
    if not max_width or max_width <= 0:
        return [texto]

    palabras = texto.split()
    lineas = []
    linea_actual = ""

    for palabra in palabras:
        linea_prueba = linea_actual + (" " if linea_actual else "") + palabra
        bbox = draw.textbbox((0, 0), linea_prueba, font=font)
        ancho_texto = bbox[2] - bbox[0]

        if ancho_texto <= max_width:
            linea_actual = linea_prueba
        else:
            if linea_actual:
                lineas.append(linea_actual)
            linea_actual = palabra

    if linea_actual:
        lineas.append(linea_actual)

    return lineas if lineas else [texto]


def dibujar_texto_con_contorno(draw, posicion, texto, font, color_relleno, ancho_contorno, color_contorno):
    """
    Dibuja texto con contorno (stroke) usando desplazamientos.

    Args:
        draw: Objeto ImageDraw
        posicion: (x, y) tupla de posición
        texto: Texto a dibujar
        font: Objeto ImageFont
        color_relleno: Tupla RGB del color del texto
        ancho_contorno: Ancho del contorno en píxeles
        color_contorno: Tupla RGB del color del contorno
    """
    x, y = posicion

    # Dibujar contorno primero (múltiples capas)
    if ancho_contorno > 0:
        for adj_x in range(-ancho_contorno, ancho_contorno + 1):
            for adj_y in range(-ancho_contorno, ancho_contorno + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((x + adj_x, y + adj_y), texto, fill=color_contorno, font=font)

    # Dibujar texto principal encima
    draw.text((x, y), texto, fill=color_relleno, font=font)


def renderizar_anuncio_v2(imagen_file, titulo, contenido, estilos):
    """
    NUEVO SISTEMA DE RENDERIZADO V2

    Renderiza un anuncio con texto superpuesto en una imagen.

    Args:
        imagen_file: Archivo de imagen (ImageField o UploadedFile)
        titulo: Texto del título (puede ser vacío)
        contenido: Texto del contenido (requerido)
        estilos: Dict con:
            - font_family: Nombre de la fuente
            - font_size: Tamaño base de fuente
            - text_color: Color en hex (#RRGGBB)
            - stroke_width: Ancho del contorno (0-10)
            - stroke_color: Color del contorno en hex
            - titulo_x, titulo_y: Posición del cuadro de título (píxeles)
            - titulo_width, titulo_height: Tamaño del cuadro de título
            - titulo_font_size: Tamaño específico del título
            - contenido_x, contenido_y: Posición del cuadro de contenido
            - contenido_width, contenido_height: Tamaño del cuadro de contenido
            - contenido_font_size: Tamaño específico del contenido

    Returns:
        InMemoryUploadedFile con la imagen renderizada
    """

    try:
        logger.info(f"Renderizando anuncio con estilos: {estilos}")
        # Abrir imagen original (ya debe estar en RGB/JPG gracias a clean_imagen del formulario)
        img = Image.open(imagen_file)
        logger.info(f"Modo de imagen original: {img.mode}")

        # Por seguridad, convertir a RGB si no lo está (en caso de que venga de otra fuente)
        if img.mode != 'RGB':
            logger.warning(f"Imagen no está en RGB, convirtiendo de {img.mode}")
            img = img.convert('RGB')

        ancho_original, alto_original = img.size

        # Upscale para mejor calidad si es necesaria
        escala_temporal = 1
        if ancho_original < 800:
            escala_temporal = 2
            img = img.resize((ancho_original * escala_temporal, alto_original * escala_temporal),
                           Image.Resampling.LANCZOS)

        ancho, alto = img.size
        draw = ImageDraw.Draw(img)

        # Extraer estilos
        font_family = estilos.get('font_family', 'Arial')
        font_size_base = int(estilos.get('font_size', 20))
        text_color = hex_a_rgb(estilos.get('text_color', '#000000'))
        stroke_width = int(estilos.get('stroke_width', 0))
        stroke_color = hex_a_rgb(estilos.get('stroke_color', '#000000'))

        # --- COMPATIBILIDAD: Convertir formato antiguo (text_position_x_px) al nuevo (titulo_x, contenido_x) ---
        # Si vienen estilos en el formato antiguo de publicacion_form.html, convertirlos
        if 'text_position_x_px' in estilos and 'titulo_x' not in estilos:
            logger.info("Detectado formato antiguo de estilos, convirtiendo a nuevo formato")
            text_x = int(estilos.get('text_position_x_px', 20))
            text_y = int(estilos.get('text_position_y_px', 20))
            text_width = int(estilos.get('text_width_px', 300))
            text_height = int(estilos.get('text_height_px', 300))

            # En formato antiguo, todo va al contenido, título está vacío
            estilos['titulo_x'] = 20
            estilos['titulo_y'] = 20
            estilos['titulo_width'] = 300
            estilos['titulo_height'] = 100

            estilos['contenido_x'] = text_x
            estilos['contenido_y'] = text_y
            estilos['contenido_width'] = text_width
            estilos['contenido_height'] = text_height

        # --- RENDERIZAR TÍTULO ---
        if titulo and titulo.strip():
            titulo_x = int(estilos.get('titulo_x', 20)) * escala_temporal
            titulo_y = int(estilos.get('titulo_y', 20)) * escala_temporal
            titulo_width = int(estilos.get('titulo_width', 300)) * escala_temporal
            titulo_height = int(estilos.get('titulo_height', 100)) * escala_temporal

            logger.info(f"TÍTULO: x={titulo_x}, y={titulo_y}, width={titulo_width}, height={titulo_height}")

            # Usar el font size específico del título si existe, sino calcular
            titulo_font_size = estilos.get('titulo_font_size')
            logger.info(f"titulo_font_size del estilos: {titulo_font_size}")

            if titulo_font_size:
                font_size = int(titulo_font_size) * escala_temporal
                logger.info(f"Usando titulo_font_size específico: {font_size}px")
            else:
                # Calcular font size basado en ancho del cuadro
                font_size = calcular_font_size(titulo_width, font_family, font_size_base)
                logger.info(f"Calculando font_size: {font_size}px")

            font = obtener_fuente(font_family, font_size)

            # Ajustar texto al ancho
            lineas_titulo = ajustar_texto_a_ancho(titulo, font, titulo_width - 20, draw)

            # Dibujar líneas de título
            y_offset = titulo_y + 10
            line_height = int(font_size * 1.5)

            for linea in lineas_titulo:
                if y_offset + line_height > titulo_y + titulo_height:
                    break  # No cabe más texto
                dibujar_texto_con_contorno(draw, (titulo_x + 10, y_offset), linea, font,
                                         text_color, stroke_width, stroke_color)
                y_offset += line_height

        # --- RENDERIZAR CONTENIDO ---
        if contenido and contenido.strip():
            contenido_x = int(estilos.get('contenido_x', 20)) * escala_temporal
            contenido_y = int(estilos.get('contenido_y', 150)) * escala_temporal
            contenido_width = int(estilos.get('contenido_width', 300)) * escala_temporal
            contenido_height = int(estilos.get('contenido_height', 300)) * escala_temporal

            logger.info(f"CONTENIDO: x={contenido_x}, y={contenido_y}, width={contenido_width}, height={contenido_height}")

            # Usar el font size específico del contenido si existe, sino calcular
            contenido_font_size = estilos.get('contenido_font_size')
            logger.info(f"contenido_font_size del estilos: {contenido_font_size}")

            if contenido_font_size:
                font_size = int(contenido_font_size) * escala_temporal
                logger.info(f"Usando contenido_font_size específico: {font_size}px")
            else:
                # Calcular font size basado en ancho del cuadro
                font_size = calcular_font_size(contenido_width, font_family, font_size_base)
                logger.info(f"Calculando font_size: {font_size}px")

            font = obtener_fuente(font_family, font_size)

            # Ajustar texto al ancho
            lineas_contenido = ajustar_texto_a_ancho(contenido, font, contenido_width - 20, draw)

            # Dibujar líneas de contenido
            y_offset = contenido_y + 10
            line_height = int(font_size * 1.3)

            for linea in lineas_contenido:
                if y_offset + line_height > contenido_y + contenido_height:
                    break  # No cabe más texto
                dibujar_texto_con_contorno(draw, (contenido_x + 10, y_offset), linea, font,
                                         text_color, stroke_width, stroke_color)
                y_offset += line_height

        # Downscale si fue upscaleada
        if escala_temporal > 1:
            img = img.resize((ancho_original, alto_original), Image.Resampling.LANCZOS)

        # Guardar a buffer
        img_io = io.BytesIO()
        img.save(img_io, format='PNG', optimize=False)
        img_io.seek(0)

        # Crear archivo para Django
        archivo_procesado = InMemoryUploadedFile(
            img_io,
            'ImageField',
            'anuncio_renderizado.png',
            'image/png',
            img_io.getbuffer().nbytes,
            None
        )

        logger.info(f"Anuncio renderizado exitosamente: {ancho_original}x{alto_original}")
        return archivo_procesado

    except Exception as e:
        logger.error(f"Error al renderizar anuncio: {e}")
        return imagen_file  # Retornar imagen original si hay error
