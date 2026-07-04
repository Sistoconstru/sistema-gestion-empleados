# =============================================================================
# apps/core/admin.py
# =============================================================================

from django.contrib import admin
from .models import ConfiguracionSistema, LogActividad, DocumentoCorporativo


@admin.register(DocumentoCorporativo)
class DocumentoCorporativoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'version', 'fecha_publicacion', 'activo', 'creado_por')
    list_filter = ('categoria', 'activo', 'fecha_publicacion')
    search_fields = ('titulo', 'descripcion', 'version')
    readonly_fields = ('id',)
    ordering = ('-fecha_publicacion',)

    fieldsets = (
        ('Información del documento', {
            'fields': ('titulo', 'descripcion', 'categoria', 'version', 'archivo', 'activo'),
        }),
        ('Vigencia', {
            'fields': ('fecha_publicacion', 'fecha_vigencia_desde', 'fecha_vigencia_hasta'),
            'classes': ('collapse',),
        }),
        ('Auditoría', {
            'fields': ('id', 'creado_por'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.creado_por_id:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)

# Registro del modelo ConfiguracionSistema en el admin de Django
@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista de configuraciones
    list_display = ('modulo', 'clave', 'tipo_dato', 'editable_usuario', 'fecha_actualizacion')
    # Filtros disponibles en la barra lateral
    list_filter = ('modulo', 'tipo_dato', 'editable_usuario')
    # Campos por los que se puede buscar
    search_fields = ('modulo', 'clave', 'descripcion')
    
    # Agrupación de campos en el formulario de edición
    fieldsets = (
        ('Configuración', {
            'fields': ('modulo', 'clave', 'valor', 'tipo_dato')
        }),
        ('Información Adicional', {
            'fields': ('descripcion', 'valor_defecto', 'editable_usuario')
        }),
    )

# Registro del modelo LogActividad en el admin de Django
@admin.register(LogActividad)
class LogActividadAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista de logs
    list_display = (
        'fecha_accion',
        'descripcion_corta',
        'usuario_display',
        'ip_address',
    )

    # Filtros disponibles en la barra lateral
    list_filter = (
        'accion',
        'modelo',
        'metodo_http',
        ('fecha_accion', admin.DateFieldListFilter),
        'usuario',
    )

    # Campos por los que se puede buscar
    search_fields = (
        'descripcion',
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'modelo',
        'accion',
        'objeto_id',
        'ip_address',
        'url_accedida',
    )

    # Campos que serán solo de lectura
    readonly_fields = (
        'fecha_accion',
        'descripcion',
        'usuario',
        'accion',
        'modelo',
        'objeto_id',
        'cambios_realizados_display',
        'ip_address',
        'user_agent',
        'metodo_http',
        'url_accedida',
    )

    # Orden por defecto (más recientes primero)
    ordering = ('-fecha_accion',)

    # Paginación
    list_per_page = 50

    # Configuración de campos en el formulario
    fieldsets = (
        ('Información General', {
            'fields': ('fecha_accion', 'descripcion', 'usuario', 'ip_address')
        }),
        ('Acción Realizada', {
            'fields': ('accion', 'modelo', 'objeto_id', 'metodo_http', 'url_accedida')
        }),
        ('Detalles Técnicos', {
            'fields': ('cambios_realizados_display', 'user_agent'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False  # No permitir agregar logs manualmente

    def has_delete_permission(self, request, obj=None):
        # Solo superusuarios pueden eliminar logs
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return False  # Los logs no deben ser editables

    def descripcion_corta(self, obj):
        """Muestra la descripción truncada"""
        if obj.descripcion:
            if len(obj.descripcion) > 80:
                return obj.descripcion[:80] + '...'
            return obj.descripcion
        return f"{obj.accion} - {obj.modelo}"
    descripcion_corta.short_description = 'Descripción de la Acción'
    descripcion_corta.admin_order_field = 'descripcion'

    def usuario_display(self, obj):
        """Muestra el usuario de forma más amigable"""
        if obj.usuario:
            return f"{obj.usuario.get_full_name() or obj.usuario.username}"
        return "Sistema"
    usuario_display.short_description = 'Usuario'
    usuario_display.admin_order_field = 'usuario'

    def accion_display(self, obj):
        """Muestra la acción con colores según el tipo"""
        from django.utils.html import format_html

        colores = {
            'crear': 'green',
            'modificar': 'blue',
            'eliminar': 'red',
            'cambiar_estado': 'orange',
            'cambiar_cargo': 'purple',
            'aprobar': 'darkgreen',
            'rechazar': 'darkred',
            'subir_archivo': 'teal',
        }

        color = colores.get(obj.accion, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.accion.replace('_', ' ').title()
        )
    accion_display.short_description = 'Acción'
    accion_display.admin_order_field = 'accion'

    def objeto_id_corto(self, obj):
        """Muestra solo los primeros 8 caracteres del UUID"""
        if obj.objeto_id:
            return str(obj.objeto_id)[:8] + '...'
        return '-'
    objeto_id_corto.short_description = 'ID Objeto'

    def cambios_realizados_display(self, obj):
        """Muestra los cambios en formato JSON legible"""
        from django.utils.html import format_html
        import json

        if obj.cambios_realizados:
            try:
                json_formateado = json.dumps(obj.cambios_realizados, indent=2, ensure_ascii=False)
                return format_html('<pre>{}</pre>', json_formateado)
            except:
                return str(obj.cambios_realizados)
        return 'Sin cambios registrados'
    cambios_realizados_display.short_description = 'Cambios Realizados'

    # Acciones personalizadas
    actions = ['exportar_logs_seleccionados']

    def exportar_logs_seleccionados(self, request, queryset):
        """Exporta los logs seleccionados a CSV"""
        import csv
        from django.http import HttpResponse
        from datetime import datetime

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="logs_auditoria_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Fecha/Hora',
            'Usuario',
            'Acción',
            'Modelo',
            'Objeto ID',
            'IP Address',
            'Método HTTP',
            'URL',
        ])

        for log in queryset:
            writer.writerow([
                log.fecha_accion.strftime('%Y-%m-%d %H:%M:%S'),
                log.usuario.username if log.usuario else 'Sistema',
                log.accion,
                log.modelo,
                log.objeto_id or '',
                log.ip_address,
                log.metodo_http,
                log.url_accedida,
            ])

        return response
    exportar_logs_seleccionados.short_description = 'Exportar logs seleccionados a CSV'

