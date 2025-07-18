
# Register your models here.

# =============================================================================
# apps/core/admin.py
# =============================================================================

from django.contrib import admin
from .models import ConfiguracionSistema, LogActividad

@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ('modulo', 'clave', 'tipo_dato', 'editable_usuario', 'fecha_actualizacion')
    list_filter = ('modulo', 'tipo_dato', 'editable_usuario')
    search_fields = ('modulo', 'clave', 'descripcion')
    
    fieldsets = (
        ('Configuración', {
            'fields': ('modulo', 'clave', 'valor', 'tipo_dato')
        }),
        ('Información Adicional', {
            'fields': ('descripcion', 'valor_defecto', 'editable_usuario')
        }),
    )

@admin.register(LogActividad)
class LogActividadAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'accion', 'modelo', 'ip_address', 'fecha_accion')
    list_filter = ('accion', 'modelo', 'fecha_accion')
    search_fields = ('usuario__username', 'modelo', 'accion')
    readonly_fields = ('fecha_accion',)
    
    def has_add_permission(self, request):
        return False  # No permitir agregar logs manualmente

