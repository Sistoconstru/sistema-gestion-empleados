# =============================================================================
# apps/organizational/admin.py
# =============================================================================

from django.contrib import admin
from .models import Sede, AreaEmpresa, Cargo

@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'ciudad', 'departamento', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'departamento', 'ciudad')
    search_fields = ('codigo', 'nombre', 'ciudad')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'activa')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'ciudad', 'departamento')
        }),
        ('Contacto', {
            'fields': ('telefono',)
        }),
    )

@admin.register(AreaEmpresa)
class AreaEmpresaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'area_padre', 'responsable', 'activa')
    list_filter = ('activa', 'area_padre')
    search_fields = ('codigo', 'nombre')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('area_padre', 'responsable')

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'area', 'nivel_jerarquico', 'salario_minimo', 'activo')
    list_filter = ('activo', 'area', 'nivel_jerarquico', 'requiere_licencia_conducir')
    search_fields = ('codigo', 'nombre', 'area__nombre')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'activo')
        }),
        ('Estructura', {
            'fields': ('area', 'cargo_jefe', 'nivel_jerarquico')
        }),
        ('Salarios', {
            'fields': ('salario_minimo', 'salario_maximo')
        }),
        ('Requisitos', {
            'fields': ('requiere_licencia_conducir', 'requiere_certificado_alturas')
        }),
    )