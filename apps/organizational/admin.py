# =============================================================================
# apps/organizational/admin.py
# =============================================================================

from django.contrib import admin
from apps.evaluations.models import EvaluacionCargo
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
        # Optimiza la consulta incluyendo relaciones
        return super().get_queryset(request).select_related('area_padre', 'responsable')

class EvaluacionCargoInline(admin.TabularInline):
    model = EvaluacionCargo
    extra = 1
    autocomplete_fields = ['evaluacion']
    fields = ['evaluacion']  # Solo mostrar el campo evaluación

    def get_readonly_fields(self, request, obj=None):
        """Hacer todos los campos readonly excepto evaluacion"""
        return []


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'area', 'rol_automatico', 'nivel_jerarquico', 'activo')
    inlines = [EvaluacionCargoInline]
    list_filter = ('activo', 'area', 'nivel_jerarquico', 'rol_automatico')
    search_fields = ('codigo', 'nombre', 'area__nombre')

    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'activo')
        }),
        ('Estructura Organizacional', {
            'fields': ('area', 'cargo_jefe', 'nivel_jerarquico')
        }),
        ('Rol del Sistema', {
            'fields': ('rol_automatico',),
            'description': 'Rol que se asignará automáticamente a empleados con este cargo'
        }),
        ('Salarios', {
            'fields': ('salario_minimo', 'salario_maximo')
        }),
        ('Requisitos', {
            'fields': ('requiere_licencia_conducir', 'requiere_certificado_alturas')
        }),
    )

    def get_queryset(self, request):
        # Optimiza la consulta incluyendo relaciones
        return super().get_queryset(request).select_related('area', 'rol_automatico')

    def save_formset(self, request, form, formset, change):
        """
        Sobrescribe save_formset para asignar automáticamente el usuario logueado
        al campo 'asignado_por' en EvaluacionCargo
        """
        # Guardar instancias sin commit para poder modificarlas
        instances = formset.save(commit=False)

        for instance in instances:
            # Si es una instancia de EvaluacionCargo
            if isinstance(instance, EvaluacionCargo):
                # Siempre asignar el usuario logueado (para nuevas y existentes sin asignación)
                if not instance.pk or not instance.asignado_por_id:
                    # Nueva instancia (no tiene pk) o existente sin asignado_por
                    instance.asignado_por = request.user
            instance.save()

        # Guardar relaciones many-to-many
        formset.save_m2m()

        # Procesar eliminaciones
        for obj in formset.deleted_objects:
            obj.delete()

