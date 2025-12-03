# Fuentes Personalizadas para Anuncios

Este directorio contiene las fuentes TrueType (.ttf) utilizadas en el procesamiento de anuncios.

## Fuentes Incluidas

Las siguientes fuentes están disponibles para seleccionar en el creador de anuncios:

- **Love Twist Sans** - Fuente moderna y creativa
- **Twiggy** - Fuente decorativa vintage
- **Pinewood** - Fuente rústica y natural

## Fuentes del Sistema

Además de las fuentes personalizadas, el sistema también usa:
- Arial (sistema)
- Times New Roman (sistema)
- Courier New (sistema)
- Georgia (sistema)
- Verdana (sistema)
- Comic Sans MS (sistema)

## Instalación de Fuentes

### Windows
1. Coloca los archivos `.ttf` en esta carpeta
2. (Opcional) También puedes instalar en `C:\Windows\Fonts\` haciendo clic derecho → Instalar

### Linux (Servidor)
1. Coloca los archivos `.ttf` en esta carpeta
2. El sistema los encontrará automáticamente

### macOS
1. Coloca los archivos `.ttf` en esta carpeta
2. (Opcional) También puedes copiarlos a `/Library/Fonts/`

## Prioridad de Búsqueda

El sistema busca fuentes en este orden:
1. **Carpeta del proyecto** (`apps/employees/fonts/`) - ✅ MÁXIMA PRIORIDAD
2. Windows: `C:\Windows\Fonts`
3. Linux: `/usr/share/fonts/truetype`
4. Linux: `/usr/share/fonts/truetype/dejavu`
5. Linux: `/usr/share/fonts/truetype/liberation`
6. macOS: `/Library/Fonts`
7. macOS: `/System/Library/Fonts`
8. **Fallback**: Arial del sistema o fuente por defecto

## Si Faltan Fuentes

Si una fuente no está disponible:
- ✅ El sistema NO falla
- ✅ Usa automáticamente una fuente alternativa (Arial, DejaVuSans, o fuente por defecto)
- 📝 Registra un aviso en los logs
- 📮 El anuncio se publica normalmente

## Agregar Nuevas Fuentes

1. Descarga el archivo `.ttf` de la fuente
2. Colócalo en esta carpeta (`apps/employees/fonts/`)
3. Actualiza `apps/employees/image_processing.py` en la sección `font_mapping` si es necesario
4. Actualiza `apps/employees/templates/employees/feed/anuncio_form.html` para agregar la opción en el selector
5. Reinicia Django

## Licencias

Asegúrate de que las fuentes tengan licencia que permita su uso comercial y distribución.

- **Google Fonts**: Fuentes de código abierto con licencias permisivas (SIL Open Font License)
- **DaFont**: Verifica la licencia específica de cada fuente
- **FontSquirrel**: Fuentes verificadas como libres de derechos para web

## Ejemplos de Descargas

### Google Fonts (Recomendado)
Visita https://fonts.google.com/ y busca:
- "Love Twist Sans"
- "Twiggy"
- "Pinewood"

Descarga el archivo `.ttf` regular (no Bold, Italic, etc.)
