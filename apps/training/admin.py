# =============================================================================
# apps/training/admin.py - CORREGIR CAPACITACIONES
# =============================================================================

from django.contrib import admin, messages
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from .models import (TipoCapacitacion, Capacitacion, CapacitacionCargo, ModuloCapacitacion,
                     Leccion, TipoContenido, ContenidoLeccion, InscripcionCapacitacion, ProgresoCapacitacion,
                     QuizLeccion, PreguntaQuiz, OpcionPreguntaQuiz, IntentoQuiz, RespuestaQuiz, CertificadoPlantilla,
                     SesionCapacitacion, AsistenciaSesion)
from .certificate_generator import CertificateGenerator
from apps.employees.models import Empleado


def _emitir_certificados_para(inscripciones_qs):
    """Asigna número + fecha de emisión a las inscripciones aprobadas que aún
    no las tengan. No genera PDFs — esos se renderizan al vuelo en la descarga.

    Devuelve (emitidos, omitidos, errores).
    """
    emitidos, omitidos, errores = 0, [], []
    inscripciones_qs = inscripciones_qs.select_related('empleado', 'capacitacion')
    for inscripcion in inscripciones_qs:
        try:
            if CertificateGenerator.emitir_certificado(inscripcion):
                emitidos += 1
            else:
                omitidos.append(
                    f"{inscripcion.empleado.nombre_completo} / {inscripcion.capacitacion.nombre}"
                )
        except Exception as exc:
            errores.append(
                f"{inscripcion.empleado.nombre_completo} / {inscripcion.capacitacion.nombre}: {exc}"
            )
    return emitidos, omitidos, errores

@admin.register(TipoCapacitacion)
class TipoCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')

@admin.register(Capacitacion)
class CapacitacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'modalidad', 'es_externa_display', 'duracion_estimada_horas', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'modalidad', 'tipo', 'es_capacitacion_externa', 'fecha_creacion')
    search_fields = ('codigo', 'nombre', 'nombre_proveedor')

    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'tipo', 'modalidad', 'activa', 'nivel_dificultad')
        }),
        ('Capacitación Externa', {
            'fields': ('es_capacitacion_externa', 'nombre_proveedor', 'url_curso_externo', 'requiere_certificado_externo'),
            'description': 'Marcar "Es capacitación externa" si es ofrecida por un proveedor externo (Coursera, Udemy, etc.). Esto simplifica la gestión: solo necesitas la URL del curso.',
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('duracion_estimada_horas', 'puntaje_aprobacion', 'intentos_maximos', 'puntos_gamificacion', 'costo_inscripcion', 'emite_certificado')
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

    actions = ['emitir_certificados_pendientes']

    @admin.action(description='Emitir certificados pendientes (asignar número y fecha)')
    def emitir_certificados_pendientes(self, request, queryset):
        """Para cada capacitación seleccionada, asigna número de certificado y
        fecha de emisión a las inscripciones aprobadas que aún no los tienen.

        El PDF se renderiza al vuelo en cada descarga usando la plantilla actual,
        así que no se guarda archivo. Útil cuando se activa emite_certificado=True
        después de que algunos empleados ya aprobaron y quedaron sin número.
        """
        inscripciones = InscripcionCapacitacion.objects.filter(
            capacitacion__in=queryset,
            estado='aprobado',
            numero_certificado__in=['', None],
        )
        emitidos, omitidos, errores = _emitir_certificados_para(inscripciones)
        if emitidos:
            self.message_user(
                request,
                f'{emitidos} certificado(s) emitido(s) correctamente.',
                level=messages.SUCCESS,
            )
        if omitidos:
            self.message_user(
                request,
                f'{len(omitidos)} inscripción(es) omitida(s) por no cumplir condiciones (nota mínima, no es externa, capacitación emite certificado, etc).',
                level=messages.WARNING,
            )
        if errores:
            preview = '; '.join(errores[:3])
            self.message_user(
                request,
                f'{len(errores)} error(es) durante la emisión. Primeros: {preview}',
                level=messages.ERROR,
            )
        if not (emitidos or omitidos or errores):
            self.message_user(
                request,
                'No se encontraron inscripciones aprobadas sin certificado para emitir.',
                level=messages.INFO,
            )

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
        super().save_model(request, obj, form, change)


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
    list_display = ('empleado', 'capacitacion', 'sesion', 'estado', 'obligatoria', 'fecha_inscripcion', 'puntaje_final')
    list_filter = ('estado', 'obligatoria', 'sesion', 'fecha_inscripcion')
    search_fields = ('empleado__nombres', 'empleado__apellidos', 'capacitacion__nombre', 'sesion__codigo')
    autocomplete_fields = ('empleado', 'capacitacion', 'sesion')

    exclude = ('inscrito_por',)
    actions = ['emitir_certificado_inscripciones']

    def save_model(self, request, obj, form, change):
        # Asigna el usuario que inscribe solo al crear
        if not change:
            obj.inscrito_por = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description='Emitir certificado (asignar número) de las inscripciones seleccionadas')
    def emitir_certificado_inscripciones(self, request, queryset):
        """Asigna número y fecha de emisión a las inscripciones aprobadas que
        no los tienen. El PDF se renderiza al vuelo en cada descarga."""
        emitidos, omitidos, errores = _emitir_certificados_para(queryset)
        if emitidos:
            self.message_user(request, f'{emitidos} certificado(s) emitido(s).', level=messages.SUCCESS)
        if omitidos:
            self.message_user(
                request,
                f'{len(omitidos)} inscripción(es) omitida(s) (no aprobadas, no cumplen nota mínima, el curso no emite certificado o ya estaban emitidas).',
                level=messages.WARNING,
            )
        if errores:
            preview = '; '.join(errores[:3])
            self.message_user(request, f'{len(errores)} error(es). Primeros: {preview}', level=messages.ERROR)
        if not (emitidos or omitidos or errores):
            self.message_user(request, 'Sin cambios.', level=messages.INFO)

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


# -----------------------------------------------------------------------------
# Capacitaciones presenciales: sesiones + asistencia
# -----------------------------------------------------------------------------

class AsistenciaSesionInline(admin.TabularInline):
    model = AsistenciaSesion
    extra = 0
    fields = ('fecha', 'asistio', 'hora_llegada', 'observaciones', 'registrado_por')
    readonly_fields = ('registrado_por', 'fecha_registro')
    autocomplete_fields = ('inscripcion',)


@admin.register(SesionCapacitacion)
class SesionCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'capacitacion', 'modalidad', 'fecha_inicio', 'fecha_fin',
                    'encargado', 'estado', 'inscripcion_abierta', 'cupo_maximo', 'inscritos_count',
                    'acciones_sesion')
    list_filter = ('estado', 'modalidad', 'inscripcion_abierta', 'fecha_inicio')
    search_fields = ('codigo', 'capacitacion__nombre', 'capacitacion__codigo',
                     'lugar', 'encargado__nombres', 'encargado__apellidos')
    autocomplete_fields = ('capacitacion', 'encargado')
    date_hierarchy = 'fecha_inicio'
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'creado_por')

    fieldsets = (
        ('Capacitación y modalidad', {
            'fields': ('capacitacion', 'codigo', 'modalidad', 'estado')
        }),
        ('Programación', {
            'fields': ('lugar', 'fecha_inicio', 'fecha_fin', 'hora_inicio', 'hora_fin', 'encargado')
        }),
        ('Inscripción', {
            'fields': ('inscripcion_abierta', 'cupo_maximo',
                       'ventana_inscripcion_desde', 'ventana_inscripcion_hasta'),
            'description': 'Si "Inscripción abierta" está marcado y hoy está dentro de la ventana, '
                           'los empleados pueden auto-inscribirse desde el catálogo.',
        }),
        ('Aprobación', {
            'fields': ('porcentaje_asistencia_minimo',),
            'description': '% mínimo de días asistidos para aprobar la capacitación y emitir certificado.',
        }),
        ('Notas', {
            'fields': ('observaciones',),
            'classes': ('collapse',),
        }),
        ('Auditoría', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    def inscritos_count(self, obj):
        return obj.inscripciones.count()
    inscritos_count.short_description = 'Inscritos'

    def acciones_sesion(self, obj):
        from django.utils.html import format_html
        url = reverse('admin:training_sesioncapacitacion_inscribir_lote', args=[obj.pk])
        return format_html('<a class="button" href="{}">Inscribir empleados</a>', url)
    acciones_sesion.short_description = 'Acciones'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                '<uuid:sesion_id>/inscribir-lote/',
                self.admin_site.admin_view(self.inscribir_lote_view),
                name='training_sesioncapacitacion_inscribir_lote',
            ),
        ]
        return custom + urls

    def inscribir_lote_view(self, request, sesion_id):
        """Pantalla para inscribir uno o varios empleados a la sesión en un solo paso."""
        from apps.employees.models import Empleado
        sesion = SesionCapacitacion.objects.get(pk=sesion_id)

        ya_inscritos_ids = set(
            InscripcionCapacitacion.objects.filter(sesion=sesion).values_list('empleado_id', flat=True)
        )

        if request.method == 'POST':
            seleccionados = request.POST.getlist('empleados')
            obligatoria = request.POST.get('obligatoria') == 'on'
            if not seleccionados:
                self.message_user(request, 'No seleccionaste ningún empleado.', level=messages.WARNING)
                return HttpResponseRedirect(request.path)

            # Cupo restante
            cupo_restante = None
            if sesion.cupo_maximo is not None:
                cupo_restante = max(0, sesion.cupo_maximo - InscripcionCapacitacion.objects.filter(sesion=sesion).count())

            candidatos = [eid for eid in seleccionados if eid not in {str(x) for x in ya_inscritos_ids}]
            omitidos_por_duplicado = len(seleccionados) - len(candidatos)

            if cupo_restante is not None and len(candidatos) > cupo_restante:
                candidatos_a_inscribir = candidatos[:cupo_restante]
                omitidos_por_cupo = len(candidatos) - cupo_restante
            else:
                candidatos_a_inscribir = candidatos
                omitidos_por_cupo = 0

            empleados_qs = Empleado.objects.filter(id__in=candidatos_a_inscribir)
            creadas = 0
            errores = 0
            with transaction.atomic():
                for emp in empleados_qs:
                    try:
                        InscripcionCapacitacion.objects.create(
                            empleado=emp,
                            capacitacion=sesion.capacitacion,
                            sesion=sesion,
                            estado='no_iniciado',
                            obligatoria=obligatoria,
                            inscrito_por=request.user,
                        )
                        creadas += 1
                    except IntegrityError:
                        errores += 1

            if creadas:
                self.message_user(request, f'{creadas} empleado(s) inscrito(s) a la sesión.', level=messages.SUCCESS)
            if omitidos_por_duplicado:
                self.message_user(request, f'{omitidos_por_duplicado} ya estaban inscritos y se omitieron.', level=messages.INFO)
            if omitidos_por_cupo:
                self.message_user(request, f'{omitidos_por_cupo} no cupieron por cupo lleno.', level=messages.WARNING)
            if errores:
                self.message_user(request, f'{errores} fallaron por integridad y no se inscribieron.', level=messages.ERROR)
            return HttpResponseRedirect(reverse('admin:training_sesioncapacitacion_change', args=[sesion.pk]))

        # GET: mostrar formulario
        query = request.GET.get('q', '').strip()
        empleados = Empleado.objects.exclude(id__in=ya_inscritos_ids).select_related('estado').order_by('apellidos', 'nombres')
        if query:
            from django.db.models import Q
            empleados = empleados.filter(
                Q(nombres__icontains=query) | Q(apellidos__icontains=query) | Q(numero_documento__icontains=query)
            )
        # Limitar para no reventar la vista
        empleados = empleados[:500]

        cupo_disponible = sesion.cupo_disponible
        context = {
            **self.admin_site.each_context(request),
            'sesion': sesion,
            'empleados': empleados,
            'query': query,
            'cupo_disponible': cupo_disponible,
            'total_inscritos': InscripcionCapacitacion.objects.filter(sesion=sesion).count(),
            'opts': self.model._meta,
            'title': f'Inscribir empleados a {sesion.codigo}',
        }
        return render(request, 'admin/training/sesion_inscribir_lote.html', context)


@admin.register(AsistenciaSesion)
class AsistenciaSesionAdmin(admin.ModelAdmin):
    list_display = ('inscripcion', 'fecha', 'asistio', 'hora_llegada', 'registrado_por', 'fecha_registro')
    list_filter = ('asistio', 'fecha')
    search_fields = ('inscripcion__empleado__nombres', 'inscripcion__empleado__apellidos',
                     'inscripcion__capacitacion__nombre', 'inscripcion__sesion__codigo')
    autocomplete_fields = ('inscripcion',)
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha_registro',)
