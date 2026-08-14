# =============================================================================
# apps/organizational/admin.py
# =============================================================================

from django.contrib import admin
from apps.evaluations.models import EvaluacionCargo
from .models import Sede, AreaEmpresa, Cargo, CentroCosto, ResolucionSena, SalarioMinimoAnual, SeguimientoReemplazosSena

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
    list_display = ('codigo', 'nombre', 'area', 'rol_automatico', 'crea_usuario_sistema', 'es_cargo_aprendiz', 'excluido_control_asistencia', 'excluido_gestion_asistencia', 'nivel_jerarquico', 'activo')
    inlines = [EvaluacionCargoInline]
    list_filter = ('activo', 'area', 'nivel_jerarquico', 'rol_automatico', 'crea_usuario_sistema', 'es_cargo_aprendiz', 'excluido_control_asistencia', 'excluido_gestion_asistencia')
    search_fields = ('codigo', 'nombre', 'area__nombre')

    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'activo')
        }),
        ('Estructura Organizacional', {
            'fields': ('area', 'cargo_jefe', 'nivel_jerarquico')
        }),
        ('Rol del Sistema', {
            'fields': ('rol_automatico', 'crea_usuario_sistema'),
            'description': 'Rol que se asignará automáticamente a empleados con este cargo. Desmarca "¿Crea usuario en el sistema?" para cargos sin acceso (ej: aprendiz en etapa lectiva).'
        }),
        ('SENA', {
            'fields': ('es_cargo_aprendiz',),
            'description': 'Los cargos marcados como aprendiz SENA cuentan para la cuota de la resolución vigente.',
        }),
        ('Asistencia', {
            'fields': ('excluido_control_asistencia', 'excluido_gestion_asistencia'),
            'description': (
                'Dos exclusiones distintas: '
                '"No se le registra asistencia" = no aparece como subordinado (gerente + directores). '
                '"No gestiona asistencia de otros" = no ve el tile ni recibe recordatorios ni se le mide (solo gerente típicamente). '
                'Los directores mantienen la gestión de la asistencia de su equipo.'
            ),
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


@admin.register(CentroCosto)
class CentroCostoAdmin(admin.ModelAdmin):
    list_display = ('referencia', 'cuenta_analitica', 'nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo',)
    search_fields = ('cuenta_analitica', 'referencia', 'nombre')
    ordering = ('referencia',)


@admin.register(ResolucionSena)
class ResolucionSenaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha_expedicion', 'fecha_vigencia_inicio', 'fecha_vigencia_fin',
                    'cuota_aprendices', 'total_trabajadores_base', 'esta_vigente')
    list_filter = ('fecha_vigencia_inicio',)
    search_fields = ('numero', 'observaciones')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'creado_por')
    fieldsets = (
        ('Identificación', {
            'fields': ('numero', 'fecha_expedicion'),
        }),
        ('Vigencia', {
            'fields': ('fecha_vigencia_inicio', 'fecha_vigencia_fin'),
            'description': 'Deja fecha fin vacío si esta resolución sigue vigente hasta que llegue una nueva.',
        }),
        ('Cuota', {
            'fields': ('cuota_aprendices', 'total_trabajadores_base'),
        }),
        ('Documentación', {
            'fields': ('archivo_pdf', 'observaciones'),
        }),
        ('Auditoría', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    def esta_vigente(self, obj):
        from datetime import date
        hoy = date.today()
        if obj.fecha_vigencia_inicio > hoy:
            return False
        if obj.fecha_vigencia_fin and obj.fecha_vigencia_fin < hoy:
            return False
        return True
    esta_vigente.boolean = True
    esta_vigente.short_description = 'Vigente hoy'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(SalarioMinimoAnual)
class SalarioMinimoAnualAdmin(admin.ModelAdmin):
    list_display = ('year', 'valor_formateado', 'decreto', 'fecha_expedicion', 'actualizado_por', 'fecha_actualizacion')
    list_filter = ('year',)
    search_fields = ('year', 'decreto')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'actualizado_por')

    fieldsets = (
        ('Vigencia', {'fields': ('year',)}),
        ('Valor', {'fields': ('valor', 'decreto', 'fecha_expedicion')}),
        ('Notas', {'fields': ('observaciones',)}),
        ('Auditoría', {
            'fields': ('actualizado_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    def valor_formateado(self, obj):
        return f'${obj.valor:,.0f}'.replace(',', '.')
    valor_formateado.short_description = 'Valor'

    def save_model(self, request, obj, form, change):
        obj.actualizado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(SeguimientoReemplazosSena)
class SeguimientoReemplazosSenaAdmin(admin.ModelAdmin):
    list_display = ('conseguidos', 'fecha_actualizacion', 'actualizado_por')
    readonly_fields = ('fecha_actualizacion', 'actualizado_por')

    def save_model(self, request, obj, form, change):
        obj.actualizado_por = request.user
        super().save_model(request, obj, form, change)
