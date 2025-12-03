# Configuración de Fuentes Personalizadas

## Estado Actual

Se ha implementado un sistema robusto de gestión de fuentes para el creador de anuncios.

### Fuentes Disponibles

✅ **Twiggy** - Disponible (como Chalkboy.ttf)
✅ **Pinewood** - Disponible (como PINEWOOD.TTF)
❌ **Love Twist Sans** - Falta descargar

### Fuentes del Sistema (Fallback)

Disponibles en Windows, Linux y macOS:
- Arial
- Times New Roman
- Courier New
- Georgia
- Verdana
- Comic Sans MS

## Ubicación de Fuentes

```
apps/
  └── employees/
      └── fonts/
          ├── README.md                 # Documentación de fuentes
          ├── install_fonts.py          # Script de verificación
          ├── .gitignore                # Ignora archivos .ttf en git
          ├── Chalkboy.ttf              # Twiggy
          ├── PINEWOOD.TTF              # Pinewood
          └── [Love Twist Sans.ttf]     # Por descargar
```

## Orden de Búsqueda de Fuentes

El sistema busca fuentes en este orden:

1. **Carpeta del proyecto** (`apps/employees/fonts/`) ← **MÁXIMA PRIORIDAD**
2. Windows: `C:\Windows\Fonts`
3. Linux: `/usr/share/fonts/truetype`
4. Linux: `/usr/share/fonts/truetype/dejavu`
5. Linux: `/usr/share/fonts/truetype/liberation`
6. macOS: `/Library/Fonts`
7. macOS: `/System/Library/Fonts`
8. **Fallback automático**: Arial del sistema o fuente por defecto

## Ventajas del Sistema Actual

### ✅ Portabilidad
- Las fuentes se empacan con el proyecto
- Funciona en cualquier servidor sin instalación adicional
- Mismo resultado visual en desarrollo y producción

### ✅ Robustez
- Si falta una fuente: **NO falla**, usa fallback automático
- Búsqueda insensible a mayúsculas
- Compatible con Windows, Linux y macOS

### ✅ Mantenibilidad
- Script para verificar fuentes instaladas
- Documentación clara en la carpeta `fonts/`
- Logs informativos cuando usa fallback

### ✅ Seguridad en Git
- `.gitignore` excluye archivos .ttf (binarios grandes)
- Solo documentación y scripts en git
- Reduce tamaño del repositorio

## Cómo Descargar la Fuente Faltante

### Opción 1: Google Fonts (Recomendado)
1. Ve a https://fonts.google.com/
2. Busca "Love Twist Sans"
3. Descarga el archivo `.ttf` regular
4. Coloca el archivo en `apps/employees/fonts/`
5. Ejecuta: `python apps/employees/fonts/install_fonts.py`

### Opción 2: Otros Sitios
- DaFont.com
- FontSquirrel.com
- MyFonts.com

**IMPORTANTE**: Verifica que la licencia permita uso comercial y distribución.

## Verificar Fuentes Instaladas

Ejecuta:
```bash
python apps/employees/fonts/install_fonts.py
```

Salida esperada:
```
FUENTES PERSONALIZADAS (REQUERIDAS):
  [OK] Love Twist Sans: LoveTwistSans-Regular.ttf
  [OK] Twiggy: Chalkboy.ttf
  [OK] Pinewood: PINEWOOD.TTF
```

## En Producción (Linux/Docker)

El sistema funcionará perfectamente sin cambios, ya que:

1. Las fuentes están empaquetadas en `apps/employees/fonts/`
2. El código Python busca primero en esa carpeta
3. Si una fuente no está, usa automáticamente alternativas

**No se requiere**: Instalar fuentes en el servidor Linux.

## Código Relacionado

### Backend (Python)
- Archivo: `apps/employees/image_processing.py`
- Función: `renderizar_texto_en_imagen()`
- Prioridad de búsqueda implementada

### Frontend (HTML/Django)
- Archivo: `apps/employees/templates/employees/feed/anuncio_form.html`
- Selector de fuentes disponibles

## Próximos Pasos

1. Descargar "Love Twist Sans" de Google Fonts
2. Colocar en `apps/employees/fonts/`
3. Ejecutar: `python apps/employees/fonts/install_fonts.py`
4. Confirmar que las 3 fuentes aparezcan como `[OK]`
5. Listo para producción ✅

## Soporte

Si una fuente no se renderiza correctamente:

1. Verifica el log del servidor: `logs/django.log`
2. Busca mensajes como: `"Usando DejaVuSans como fallback para..."`
3. Confirma que el archivo `.ttf` existe en `apps/employees/fonts/`
4. Ejecuta `install_fonts.py` para diagnóstico

---

**Creado**: 2024
**Compatibilidad**: Windows, Linux, macOS
**Estado**: Listo para producción (excepto Love Twist Sans)
