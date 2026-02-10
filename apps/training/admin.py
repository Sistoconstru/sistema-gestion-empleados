# =============================================================================
# apps/training/admin.py - CORREGIR CAPACITACIONES
# =============================================================================

from django.contrib import admin
from .models import (TipoCapacitacion, Capacitacion, CapacitacionCargo, ModuloCapacitacion,
                     Leccion, TipoContenido, ContenidoLeccion, InscripcionCapacitacion, ProgresoCapacitacion,
                     QuizLeccion, PreguntaQuiz, OpcionPreguntaQuiz, IntentoQuiz, RespuestaQuiz, CertificadoPlantilla)

@admin.register(TipoCapacitacion)
class TipoCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')

@admin.register(Capacitacion)
class CapacitacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'es_externa_display', 'duracion_estimada_horas', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'tipo', 'es_capacitacion_externa', 'fecha_creacion')
    search_fields = ('codigo', 'nombre', 'nombre_proveedor')

    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'tipo', 'activa', 'nivel_dificultad')
        }),
        ('Capacitación Externa', {
            'fields': ('es_capacitacion_externa', 'nombre_proveedor', 'url_curso_externo', 'requiere_certificado_externo'),
            'description': 'Marcar "Es capacitación externa" si es ofrecida por un proveedor externo (Coursera, Udemy, etc.). Esto simplifica la gestión: solo necesitas la URL del curso.',
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('duracion_estimada_horas', 'puntaje_aprobacion', 'intentos_maximos', 'puntos_gamificacion', 'costo_inscripcion')
        }),
        ('Vigencia', {
            'fields': ('fecha_vigencia_inicio', 'fecha_vigencia_fin', 'version')
        }),
        ('Opciones Avanzadas', {
            'fields': ('visible_en_catalogo', 'permite_certificacion_manual', 'requiere_prerequisitos'),
            'classes': ('collapse',)
        }),
    )

    exclude = ('creada_por', 'proveedor_externo', 'url_inscripcion_externa', 'permite_autocompletado')

    def es_externa_display(self, obj):
        """Muestra si es externa con ícono"""
        if obj.es_externa():
            return '🌐 Externa'
        return '📚 Interna'
    es_externa_display.short_description = 'Tipo'

    def save_model(self, request, obj, form, change):
        # Asigna el usuario que crea la capacitación solo al crear
        if not change:
            obj.creada_por = request.user
        super().save_model(request, obj, form, change)

@admin.register(CapacitacionCargo)
class CapacitacionCargoAdmin(admin.ModelAdmin):
    list_display = ('capacitacion', 'cargo', 'obligatoria', 'dias_plazo_completar')
    list_filter = ('obligatoria',)
    
    exclude = ('asignado_por',)
    
    def save_model(self, request, obj, form, change):
        # Asigna el usuario que realiza la asignación solo al crear
        if not change:
            obj.asignado_por = request.user

class OpcionPreguntaQuizInline(admin.TabularInline):
    model = OpcionPreguntaQuiz
    extra = 4  # Número de opciones vacías a mostrar
    fields = ('texto', 'es_correcta', 'retroalimentacion', 'orden')

class PreguntaQuizInline(admin.StackedInline):
    model = PreguntaQuiz
    extra = 1
    fields = ('texto', 'tipo', 'puntaje', 'imagen', 'explicacion', 'orden')
    
@admin.register(QuizLeccion)
class QuizLeccionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'leccion', 'porcentaje_aprobacion', 'intentos_maximos', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'porcentaje_aprobacion')
    search_fields = ('titulo', 'descripcion', 'leccion__nombre')
    inlines = [PreguntaQuizInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('leccion', 'titulo', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('porcentaje_aprobacion', 'tiempo_limite', 'intentos_maximos')
        }),
    )

@admin.register(PreguntaQuiz)
class PreguntaQuizAdmin(admin.ModelAdmin):
    list_display = ('texto_corto', 'quiz', 'tipo', 'puntaje', 'orden')
    list_filter = ('tipo', 'quiz')
    search_fields = ('texto', 'explicacion')
    inlines = [OpcionPreguntaQuizInline]
    
    def texto_corto(self, obj):
        return obj.texto[:50] + '...' if len(obj.texto) > 50 else obj.texto
    texto_corto.short_description = 'Pregunta'

@admin.register(IntentoQuiz)
class IntentoQuizAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'quiz', 'fecha_inicio', 'puntaje_obtenido', 'aprobado')
    list_filter = ('aprobado', 'fecha_inicio')
    search_fields = ('usuario__username', 'quiz__titulo')
    readonly_fields = ('fecha_inicio', 'fecha_fin', 'puntaje_obtenido', 'tiempo_utilizado', 'aprobado')

@admin.register(RespuestaQuiz)
class RespuestaQuizAdmin(admin.ModelAdmin):
    list_display = ('intento', 'pregunta', 'es_correcta', 'fecha_respuesta')
    list_filter = ('es_correcta', 'fecha_respuesta')
    search_fields = ('intento__usuario__username', 'pregunta__texto')
    readonly_fields = ('intento', 'pregunta', 'opcion_seleccionada', 'es_correcta', 'fecha_respuesta')

@admin.register(ModuloCapacitacion)
class ModuloCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'capacitacion', 'orden', 'duracion_estimada_minutos', 'activo', 'modulo_prerequisito')
    list_filter = ('activo', 'capacitacion')
    ordering = ('capacitacion', 'orden')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "modulo_prerequisito":
            # Excluir el módulo actual de la lista de prerequisitos
            if request.resolver_match.kwargs.get('object_id'):
                kwargs["queryset"] = ModuloCapacitacion.objects.exclude(
                    id=request.resolver_match.kwargs['object_id']
                )
            # Añadir "--------" como opción para indicar "sin prerequisito"
            kwargs["empty_label"] = "--------"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Leccion)
class LeccionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'modulo', 'orden', 'duracion_estimada_minutos', 'activa')
    list_filter = ('activa', 'modulo__capacitacion')
    ordering = ('modulo', 'orden')

@admin.register(TipoContenido)
class TipoContenidoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'requiere_archivo', 'requiere_url')
    list_filter = ('requiere_archivo', 'requiere_url')

@admin.register(ContenidoLeccion)
class ContenidoLeccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'leccion', 'tipo_contenido', 'orden', 'obligatorio')
    list_filter = ('tipo_contenido', 'obligatorio')
    ordering = ('leccion', 'orden')

@admin.register(InscripcionCapacitacion)
class InscripcionCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'capacitacion', 'estado', 'obligatoria', 'fecha_inscripcion', 'puntaje_final')
    list_filter = ('estado', 'obligatoria', 'fecha_inscripcion')
    search_fields = ('empleado__nombres', 'empleado__apellidos', 'capacitacion__nombre')
    
    exclude = ('inscrito_por',)
    
    def save_model(self, request, obj, form, change):
        # Asigna el usuario que inscribe solo al crear
        if not change:
            obj.inscrito_por = request.user
        super().save_model(request, obj, form, change)

@admin.register(ProgresoCapacitacion)
class ProgresoCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('inscripcion', 'contenido', 'completado', 'porcentaje_visto', 'numero_visitas')
    list_filter = ('completado',)

@admin.register(CertificadoPlantilla)
class CertificadoPlantillaAdmin(admin.ModelAdmin):
    list_display = ('capacitacion', 'titulo_certificado', 'incluir_calificacion', 'incluir_duracion', 'nota_minima_certificado', 'ver_vista_previa')
    search_fields = ('capacitacion__nombre', 'titulo_certificado')
    list_filter = ('incluir_calificacion', 'incluir_duracion')
    readonly_fields = ('vista_previa_info',)

    fieldsets = (
        ('Capacitación', {
            'fields': ('capacitacion',)
        }),
        ('Textos del Certificado', {
            'fields': ('titulo_certificado', 'texto_superior', 'texto_inferior')
        }),
        ('Logo de la Empresa', {
            'fields': ('logo',),
            'description': 'Logo de la empresa (se mostrará centrado en la parte superior)'
        }),
        ('Imagen de Fondo', {
            'fields': ('imagen_fondo',),
            'description': 'Imagen decorativa de fondo con arabescos, marcos ornamentales, etc. (recomendado: diseño en PNG transparente)'
        }),
        ('Firma del Responsable de la Capacitación', {
            'fields': ('firma_responsable', 'nombre_responsable', 'cargo_responsable'),
            'description': 'Datos y firma del creador/responsable de la capacitación'
        }),
        ('Firma de Recursos Humanos', {
            'fields': ('firma_rrhh', 'nombre_rrhh', 'cargo_rrhh'),
            'description': 'Datos y firma del Director de Recursos Humanos'
        }),
        ('Configuración', {
            'fields': ('vista_previa_info', 'incluir_calificacion', 'incluir_duracion', 'nota_minima_certificado'),
            'description': 'Configura qué información mostrar en el certificado'
        }),
    )

    def ver_vista_previa(self, obj):
        """Botón para ver vista previa del certificado"""
        from django.urls import reverse
        from django.utils.html import format_html

        url = reverse('training:vista_previa_certificado', kwargs={'plantilla_id': obj.pk})
        return format_html(
            '<a class="button" href="{}" target="_blank" style="'
            'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
            'color: white; '
            'padding: 6px 12px; '
            'border-radius: 4px; '
            'text-decoration: none; '
            'display: inline-block; '
            'font-weight: 600; '
            'font-size: 12px;">'
            '<i class="fas fa-eye"></i> Ver Vista Previa'
            '</a>',
            url
        )
    ver_vista_previa.short_description = 'Acciones'
    ver_vista_previa.allow_tags = True

    def vista_previa_info(self, obj):
        """Muestra información de ayuda y botón de vista previa en el formulario de edición"""
        from django.urls import reverse
        from django.utils.html import format_html

        if obj.pk:
            url = reverse('training:vista_previa_certificado', kwargs={'plantilla_id': obj.pk})
            return format_html(
                '<div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0;">'
                '<p style="margin: 0 0 10px 0; color: #1565c0; font-weight: bold;">'
                '<i class="fas fa-info-circle"></i> Vista Previa del Certificado</p>'
                '<p style="margin: 0 0 15px 0; color: #555;">Puedes ver cómo se verá el certificado con los datos configurados. '
                'Se mostrará con información de ejemplo.</p>'
                '<a href="{}" target="_blank" class="button" style="'
                'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                'color: white; '
                'padding: 10px 20px; '
                'border-radius: 4px; '
                'text-decoration: none; '
                'display: inline-block; '
                'font-weight: 600;">'
                '<i class="fas fa-eye"></i> Abrir Vista Previa en Nueva Pestaña'
                '</a>'
                '</div>',
                url
            )
        else:
            return format_html(
                '<div style="background: #fff3e0; padding: 15px; border-radius: 8px;">'
                '<p style="margin: 0; color: #e65100;">'
                '<i class="fas fa-info-circle"></i> Guarda la plantilla primero para ver la vista previa'
                '</p>'
                '</div>'
            )
    vista_previa_info.short_description = ''
