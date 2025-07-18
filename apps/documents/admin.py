# apps/documents/admin.py - AGREGAR ESTAS CORRECCIONES

from django.contrib import admin
from .models import TipoDocumentoEmpleado, TipoDocumentoCargo, DocumentoEmpleado

@admin.register(TipoDocumentoEmpleado)
class TipoDocumentoEmpleadoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'obligatorio', 'tiene_vencimiento', 'requiere_aprobacion', 'activo')
    list_filter = ('obligatorio', 'tiene_vencimiento', 'requiere_aprobacion', 'activo')
    search_fields = ('codigo', 'nombre')

@admin.register(TipoDocumentoCargo)
class TipoDocumentoCargoAdmin(admin.ModelAdmin):
    list_display = ('tipo_documento', 'cargo')

@admin.register(DocumentoEmpleado)
class DocumentoEmpleadoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'tipo_documento', 'nombre_archivo', 'estado_aprobacion', 'fecha_carga')
    list_filter = ('estado_aprobacion', 'tipo_documento', 'fecha_carga')
    search_fields = ('empleado__nombres', 'empleado__apellidos', 'nombre_archivo')
    
    fieldsets = (
        ('Información del Documento', {
            'fields': ('empleado', 'tipo_documento', 'nombre_archivo', 'archivo')
        }),
        ('Fechas', {
            'fields': ('fecha_documento', 'fecha_vencimiento')
        }),
        ('Aprobación', {
            'fields': ('estado_aprobacion', 'observaciones')  # Quitar aprobado_por del form
        }),
    )
    
    # EXCLUIR campos automáticos
    exclude = ('cargado_por', 'aprobado_por')
    
    def save_model(self, request, obj, form, change):
        """Asignar automáticamente usuarios"""
        if not change:  # Solo en creación
            obj.cargado_por = request.user
        super().save_model(request, obj, form, change)
