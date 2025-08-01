# apps/documents/admin.py - AGREGAR ESTAS CORRECCIONES

from django.contrib import admin
from .models import TipoDocumentoEmpleado, TipoDocumentoCargo, DocumentoEmpleado

# Registro del modelo TipoDocumentoEmpleado en el admin de Django
@admin.register(TipoDocumentoEmpleado)
class TipoDocumentoEmpleadoAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista
    list_display = ('codigo', 'nombre', 'obligatorio', 'tiene_vencimiento', 'requiere_aprobacion', 'activo')
    # Filtros disponibles en la barra lateral
    list_filter = ('obligatorio', 'tiene_vencimiento', 'requiere_aprobacion', 'activo')
    # Campos por los que se puede buscar
    search_fields = ('codigo', 'nombre')

# Registro del modelo TipoDocumentoCargo en el admin de Django
@admin.register(TipoDocumentoCargo)
class TipoDocumentoCargoAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista
    list_display = ('tipo_documento', 'cargo')

# Registro del modelo DocumentoEmpleado en el admin de Django
@admin.register(DocumentoEmpleado)
class DocumentoEmpleadoAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista
    list_display = ('empleado', 'tipo_documento', 'nombre_archivo', 'estado_aprobacion', 'fecha_carga')
    # Filtros disponibles en la barra lateral
    list_filter = ('estado_aprobacion', 'tipo_documento', 'fecha_carga')
    # Campos por los que se puede buscar
    search_fields = ('empleado__nombres', 'empleado__apellidos', 'nombre_archivo')
    
    # Agrupación de campos en el formulario de edición
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
    
    # Excluir campos automáticos del formulario
    exclude = ('cargado_por', 'aprobado_por')
    
    def save_model(self, request, obj, form, change):
        """Asignar automáticamente usuarios"""
        if not change:  # Solo en creación
            obj.cargado_por = request.user
        super().save_model(request, obj, form, change)
