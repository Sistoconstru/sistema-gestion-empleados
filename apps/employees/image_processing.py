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
    Renderiza texto sobre una imagen usando Pillow con alta calidad.

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

        # Upscale para mejor calidad de renderizado (antialiasing)
        # Si la imagen es pequeña, aumentar escala temporal para renderizar con más precisión
        escala_temporal = 1
        if ancho < 800:
            escala_temporal = 2
            ancho_escalado = ancho * escala_temporal
            alto_escalado = alto * escala_temporal
            img = img.resize((ancho_escalado, alto_escalado), Image.Resampling.LANCZOS)
            ancho, alto = img.size
            logger.info(f"Imagen upscalada de {ancho//escala_temporal}x{alto//escala_temporal} a {ancho}x{alto} para mejor renderizado")

        # Extraer posicionamiento en píxeles y escalar si aplicamos upscale
        text_position_x_px = int(estilos.get('text_position_x_px', 20) * escala_temporal)
        text_position_y_px = int(estilos.get('text_position_y_px', 20) * escala_temporal)

        # Extraer dimensiones del cuadro de texto (si existen)
        # Primero intentar obtener los valores ya escalados a píxeles de imagen
        text_width = estilos.get('text_width_px', None)  # En píxeles de imagen
        text_height = estilos.get('text_height_px', None)  # En píxeles de imagen

        # Si no existen, usar los antiguos valores (compatibilidad con ediciones anteriores)
        if not text_width:
            text_width = estilos.get('text_width', None)  # En píxeles de navegador
            if text_width:
                text_width = int(text_width * escala_temporal)

        if not text_height:
            text_height = estilos.get('text_height', None)  # En píxeles de navegador
            if text_height:
                text_height = int(text_height * escala_temporal)

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

        # Calcular escala de fuente basándose en el tamaño real
        # Ahora tenemos text_width_px en píxeles de imagen, así que usamos eso directamente

        if text_width and text_width > 0:
            # El cuadro tiene un ancho específico en píxeles de imagen
            # Escalar la fuente proporcionalmente al ancho del cuadro
            # En preview, el cuadro era más pequeño (navegador), ahora es mucho más grande (imagen)
            # Por eso usamos text_width directamente - ya está en píxeles de imagen

            # Ajuste: la fuente debe ser proporcional al cuadro de texto
            # Si el cuadro es 400px de ancho, la fuente debe ser proporcionalmente más grande
            # que si fuera 200px de ancho

            # Estimación: aproximadamente 2 caracteres por 24px de fuente
            # Entonces caracteres_por_linea = ancho / (font_size * 0.6)

            # Mantener la escala base pero aplicar al ancho del cuadro
            image_scale = ancho / 600
            font_size_px = max(8, int(font_size_px * image_scale))
            logger.info(f"Escala por imagen: {image_scale}, tamaño de fuente: {font_size_px}px")
        else:
            # Sin cuadro específico, escalar por imagen
            image_scale = ancho / 600  # 600px es tamaño de referencia
            font_size_px = max(10, int(font_size_px * image_scale))  # Mínimo 10px
            logger.info(f"Escala por imagen: {image_scale}, tamaño final: {font_size_px}px")

        # Escalar fuente también si aplicamos upscale temporal
        font_size_px = int(font_size_px * escala_temporal)

        logger.info(f"Dimensiones del cuadro: width_px={text_width}, height_px={text_height}")
        logger.info(f"Tamaño de fuente final: {font_size_px}px")
        logger.info(f"Control de altura: max_y={'calculado' if max_y else 'sin limite'}, text_height={text_height}, alto_imagen={alto}")

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
            'Love Twist Sans': ['LoveTwistSans-Regular.ttf', 'LoveTwistSans.ttf', 'lovetwtistsans.ttf'],
            'Twiggy': ['Twiggy.ttf', 'Chalkboy.ttf', 'Twiggy-Regular.ttf'],  # Chalkboy es el archivo real
            'Pinewood': ['Pinewood.ttf', 'PINEWOOD.TTF', 'Pinewood-Regular.ttf'],
        }

        # Obtener ruta del directorio de fuentes del proyecto
        import os
        project_fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')

        # Rutas de búsqueda para diferentes sistemas operativos
        search_paths = [
            # Primero: Fuentes del proyecto (máxima prioridad)
            project_fonts_dir,
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

        def buscar_fuente_case_insensitive(search_path, font_names):
            """Busca fuentes case-insensitive en un directorio"""
            try:
                import os
                if not os.path.exists(search_path):
                    return None

                archivos = {f.lower(): os.path.join(search_path, f) for f in os.listdir(search_path) if f.lower().endswith(('.ttf', '.ttc'))}

                for font_name in font_names:
                    font_lower = font_name.lower()
                    if font_lower in archivos:
                        return archivos[font_lower]
            except:
                pass
            return None

        for search_path in search_paths:
            if not font:
                # Primero intentar búsqueda case-insensitive
                font_path = buscar_fuente_case_insensitive(search_path, font_names)
                if font_path:
                    try:
                        font = ImageFont.truetype(font_path, font_size_px)
                        logger.info(f"Fuente cargada (case-insensitive): {font_path}")
                        break
                    except Exception as e:
                        logger.debug(f"Error cargando {font_path}: {e}")
                        continue

                # Si no, intentar exacto
                for font_name in font_names:
                    try:
                        font_path = f"{search_path}/{font_name}"
                        font = ImageFont.truetype(font_path, font_size_px)
                        logger.info(f"Fuente cargada (exact): {font_path}")
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

        # Obtener configuración de contorno
        stroke_width = int(estilos.get('text_stroke', 0)) if estilos.get('text_stroke') else 0
        stroke_color_hex = estilos.get('stroke_color', '#000000')
        stroke_color_rgb = hex_a_rgb(stroke_color_hex)
        text_align = estilos.get('text_align', 'left')

        # Crear capa de dibujo con RGBA para mejor calidad
        draw = ImageDraw.Draw(img, 'RGBA')

        # Función para ajustar texto al ancho disponible con word wrap
        def ajustar_texto_a_ancho(texto, font, max_width):
            """Divide texto en líneas que caben en el ancho máximo"""
            if not max_width or max_width <= 0:
                return [texto]

            lineas = []
            para_actual = ""

            for palabra in texto.split():
                linea_prueba = para_actual + (" " if para_actual else "") + palabra
                bbox = draw.textbbox((0, 0), linea_prueba, font=font)
                ancho_texto = bbox[2] - bbox[0]

                if ancho_texto <= max_width:
                    para_actual = linea_prueba
                else:
                    if para_actual:
                        lineas.append(para_actual)
                    para_actual = palabra

                    # Si una sola palabra es muy grande, agregarla de todas formas
                    if not lineas or lineas[-1] != palabra:
                        bbox_palabra = draw.textbbox((0, 0), palabra, font=font)
                        if (bbox_palabra[2] - bbox_palabra[0]) > max_width:
                            lineas.append(palabra)
                            para_actual = ""

            if para_actual:
                lineas.append(para_actual)

            return lineas if lineas else [texto]

        # Función para dibujar texto con contorno y mejor calidad
        def draw_text_with_stroke(draw, position, text, font, fill, stroke_width, stroke_color):
            """Dibuja texto con contorno usando desplazamientos"""
            x, y = position
            if stroke_width > 0:
                # Dibujar contorno primero (múltiples capas) con mejor cobertura
                for adj_x in range(-stroke_width, stroke_width + 1):
                    for adj_y in range(-stroke_width, stroke_width + 1):
                        if adj_x != 0 or adj_y != 0:
                            draw.text((x + adj_x, y + adj_y), text, fill=stroke_color, font=font)
            # Dibujar texto principal encima con mejor renderizado
            draw.text((x, y), text, fill=fill, font=font)

        # Calcular ancho máximo para el contenido
        max_content_width = None
        if text_width:
            max_content_width = text_width - 40  # padding horizontal

        # Dibujar título si existe
        y_offset = text_position_y_px

        # Solo establecer límite de altura si text_height es significativamente pequeño
        # (es decir, el usuario realmente redimensionó el cuadro)
        # Si text_height es None o muy grande, permitir todo el contenido
        max_y = None
        if text_height and text_height > 0 and text_height < (alto - text_position_y_px) * 0.8:
            max_y = text_position_y_px + text_height

        if titulo:
            titulo_text = f"📢 {titulo}"
            titulo_lineas = ajustar_texto_a_ancho(titulo_text, font, max_content_width)

            for linea_titulo in titulo_lineas:
                # Verificar si la línea cabe dentro de los límites de altura
                if max_y and y_offset >= max_y:
                    break
                draw_text_with_stroke(draw, (text_position_x_px, y_offset), linea_titulo, font, text_color_rgb, stroke_width, stroke_color_rgb)
                y_offset += int(font_size_px * 1.5)

        # Dibujar contenido línea por línea con ajuste de ancho
        lineas_contenido = []
        for parrafo in contenido.split('\n'):
            lineas_contenido.extend(ajustar_texto_a_ancho(parrafo, font, max_content_width))

        for linea in lineas_contenido:
            # Verificar si la línea cabe dentro de los límites de altura
            if max_y and y_offset >= max_y:
                break
            draw_text_with_stroke(draw, (text_position_x_px, y_offset), linea, font, text_color_rgb, stroke_width, stroke_color_rgb)
            y_offset += int(font_size_px * 1.3)

        # Si upscaleamos, downscalear con LANCZOS para antialiasing perfecto
        if escala_temporal > 1:
            ancho_final = ancho // escala_temporal
            alto_final = alto // escala_temporal
            img = img.resize((ancho_final, alto_final), Image.Resampling.LANCZOS)
            logger.info(f"Imagen downscalada de vuelta a {ancho_final}x{alto_final} con antialiasing")

        # Guardar imagen en buffer con máxima calidad
        img_io = io.BytesIO()
        # Usar JPEG de alta calidad o PNG según sea necesario
        img.save(img_io, format='PNG', optimize=False)  # No optimizar para mantener calidad
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
        'imagen_alto',
        'text_width',
        'text_height',
        'text_width_px',
        'text_height_px'
    ]

    for campo in campos_eliminar:
        estilos.pop(campo, None)

    # Mantener estilos de renderizado (contorno, alineación, etc.)
    # ya que se usan en feed_list.html para mostrar
    return estilos
