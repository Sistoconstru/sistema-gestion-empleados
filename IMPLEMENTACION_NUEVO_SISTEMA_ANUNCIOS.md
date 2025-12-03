# Implementación del Nuevo Sistema de Anuncios

## ✅ Lo que ya está hecho:

### 1. **Modelo Actualizado**
- Se agregó campo `imagen_renderizada` al modelo `Publicacion`
- Se creó archivo de migración

**Ubicación:** `apps/employees/models.py:840-846`

### 2. **Motor de Renderizado Mejorado**
- Función `renderizar_anuncio_v2()` con cálculo automático de tamaño de fuente
- Soporte para cuadros de título y contenido independientes
- Contorno/stroke de texto configurable
- Búsqueda inteligente de fuentes

**Ubicación:** `apps/employees/renderizado_anuncios.py`

### 3. **Template HTML Mejorado**
- Editor visual con preview en vivo
- Cuadros arrastables y redimensionables
- Controles de estilo (fuente, color, contorno)
- Controles de posicionamiento (X, Y, ancho, alto)

**Ubicación:** `apps/employees/templates/employees/feed/anuncio_crear_nuevo.html`

---

## ⏳ Pasos de Integración Manual:

### Paso 1: Aplicar Migraciones

```bash
cd c:\Sisto\SIGHU\sistema-gestion-empleados-mi-rama
python manage.py migrate employees
```

### Paso 2: Actualizar el Formulario

En el archivo `apps/employees/forms.py`, reemplaza la clase `AnuncioImportanteForm`:

```python
class AnuncioImportanteForm(forms.ModelForm):
    """Formulario NUEVO para crear anuncios importantes"""

    fecha_inicio = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        label='Fecha y hora de inicio'
    )

    fecha_fin = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        label='Fecha y hora de finalización'
    )

    class Meta:
        model = Publicacion
        fields = ['imagen', 'titulo', 'contenido', 'fecha_inicio', 'fecha_fin', 'estilos']
        widgets = {
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_imagen'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título (opcional)',
                'maxlength': '200',
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Contenido',
                'rows': 5,
            }),
            'estilos': forms.HiddenInput(),
        }

    def clean_imagen(self):
        """Validar que la imagen sea requerida"""
        imagen = self.cleaned_data.get('imagen')
        if not imagen:
            raise ValidationError('La imagen es requerida')
        return imagen

    def clean_contenido(self):
        """Validar que no esté vacío"""
        contenido = self.cleaned_data.get('contenido')
        if not contenido or not contenido.strip():
            raise ValidationError('El contenido es requerido')
        return contenido

    def clean_fecha_fin(self):
        """Validar que la fecha sea futura"""
        fecha_fin = self.cleaned_data.get('fecha_fin')
        if fecha_fin and fecha_fin <= timezone.now():
            raise ValidationError('La fecha de finalización debe ser futura')
        return fecha_fin

    def save(self, commit=True):
        """Renderizar imagen con texto y guardar"""
        instance = super().save(commit=False)

        if instance.estilos and instance.imagen:
            try:
                from .renderizado_anuncios import renderizar_anuncio_v2
                import json

                if isinstance(instance.estilos, str):
                    estilos = json.loads(instance.estilos)
                else:
                    estilos = instance.estilos or {}

                imagen_renderizada = renderizar_anuncio_v2(
                    instance.imagen,
                    instance.titulo or '',
                    instance.contenido,
                    estilos
                )

                instance.imagen_renderizada = imagen_renderizada

            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error al renderizar anuncio: {e}")

        if commit:
            instance.save()

        return instance
```

### Paso 3: Actualizar la Vista

En el archivo `apps/employees/feed_views.py`, modifica `CrearAnuncioImportanteView`:

```python
class CrearAnuncioImportanteView(LoginRequiredMixin, CreateView):
    """NUEVA VISTA para crear anuncios importantes (solo admins)"""
    model = Publicacion
    form_class = AnuncioImportanteForm
    template_name = 'employees/feed/anuncio_crear_nuevo.html'  # Cambiar a nuevo template
    success_url = reverse_lazy('employees:feed_list')

    def dispatch(self, request, *args, **kwargs):
        """Solo admins pueden acceder"""
        if not request.user.is_staff:
            return HttpResponseForbidden('No tienes permiso para crear anuncios importantes')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Establecer datos del anuncio"""
        empleado = Empleado.objects.filter(usuario=self.request.user).first()
        if not empleado:
            empleado = Empleado.objects.first()

        form.instance.autor = empleado
        form.instance.es_anuncio = True
        form.instance.es_importante = True
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Crear Anuncio Importante'
        return context
```

### Paso 4: Actualizar el Feed para mostrar imagen renderizada

En `apps/employees/templates/employees/feed/feed_list.html`, cuando muestres anuncios, usa `imagen_renderizada` si existe:

```html
{% if publicacion.es_anuncio and publicacion.imagen_renderizada %}
    <img src="{{ publicacion.imagen_renderizada.url }}" alt="Anuncio">
{% elif publicacion.imagen %}
    <img src="{{ publicacion.imagen.url }}" alt="Publicación">
{% endif %}
```

---

## 📊 Estructura de Datos `estilos` JSON

El campo `estilos` ahora contiene:

```json
{
    "font_family": "Arial",
    "font_size": 20,
    "text_color": "#000000",
    "stroke_width": 2,
    "stroke_color": "#FFFFFF",
    "titulo_x": 20,
    "titulo_y": 20,
    "titulo_width": 200,
    "titulo_height": 80,
    "contenido_x": 20,
    "contenido_y": 120,
    "contenido_width": 200,
    "contenido_height": 150
}
```

---

## 🎯 Características del Nuevo Sistema

| Característica | Estado |
|---|---|
| Upload de imagen | ✅ |
| Editor de título | ✅ |
| Editor de contenido | ✅ |
| Selección de fuente | ✅ |
| Tamaño auto-escalable | ✅ |
| Color de texto | ✅ |
| Contorno/stroke | ✅ |
| Posicionamiento arrastrable | ✅ |
| Redimensionamiento de cuadros | ✅ |
| Preview en vivo | ✅ |
| Fechas de inicio/fin | ✅ |
| Renderizado con Pillow | ✅ |
| Guardado de imagen renderizada | ✅ |

---

## 🔧 Funciones Disponibles

### `renderizar_anuncio_v2(imagen_file, titulo, contenido, estilos)`
Renderiza un anuncio con texto superpuesto.

**Parámetros:**
- `imagen_file`: Archivo de imagen (ImageField o UploadedFile)
- `titulo`: Texto del título (puede ser vacío)
- `contenido`: Texto del contenido (requerido)
- `estilos`: Dict con configuración

**Retorna:** `InMemoryUploadedFile` con la imagen renderizada

### `obtener_fuente(font_family, font_size_px)`
Obtiene la fuente del sistema o del proyecto.

**Soporta:**
- Arial, Times New Roman, Courier New, Georgia, Verdana
- Comic Sans MS, Twiggy, Pinewood
- Búsqueda case-insensitive en Windows, Linux, macOS

### `calcular_font_size(ancho_cuadro_px, font_family, base_size_px=20)`
Calcula automáticamente el tamaño de fuente basado en el ancho del cuadro.

---

## 📝 Notas Importantes

1. **Migraciones:** No olvides ejecutar `python manage.py migrate` después de cambiar el modelo
2. **Fuentes:** El sistema busca automáticamente fuentes en:
   - `apps/employees/fonts/` (proyecto)
   - `C:\Windows\Fonts` (Windows)
   - `/usr/share/fonts/truetype` (Linux)
   - `/Library/Fonts` (macOS)
3. **Escalado:** Las imágenes se upscalear automáticamente si son < 800px para mejor calidad
4. **Limpieza:** Cambio a `overflow: visible` en preview permite ver todo el contenido
5. **Estilos:** El JSON de estilos es completamente flexible - puedes agregar más campos según necesites

---

## 🚀 Uso desde el Navegador

1. Ve a `/feed/anuncio/crear/` (solo admins)
2. Sube una imagen
3. Escribe el título (opcional) y contenido
4. Ajusta el estilo: fuente, color, contorno
5. Posiciona los cuadros de texto (arrastra o usa controles)
6. Establece fechas de inicio y fin
7. Haz clic en "Publicar Anuncio"
8. El sistema renderizará la imagen con el texto superpuesto

---

## 🎨 Personalización

Puedes agregar más fuentes editando el mapeo en `renderizado_anuncios.py:33-44`:

```python
font_mapping = {
    'Tu Fuente': ['archivo.ttf', 'alternativa.ttf'],
    # ...
}
```

---

## ✨ Ventajas del Nuevo Sistema

✅ **Más simple** - Cuadros independientes y claros
✅ **Sin bugs complejos** - Cálculo de escala simplificado
✅ **Mejor UX** - Preview en vivo y arrastrable
✅ **Auto-escalable** - Fuente se ajusta según tamaño del cuadro
✅ **Flexible** - Fácil de personalizar y extender
✅ **Robusto** - Manejo de errores y fallbacks integrados

---

**Creado:** 2025-12-01
**Autor:** Sistema de Anuncios Mejorado v2
