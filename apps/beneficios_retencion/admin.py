from django.contrib import admin

from .models import (
    DependienteBeneficio, SoporteBeneficio, SoporteDependiente, TramiteBeneficio,
)


class SoporteInline(admin.TabularInline):
    model = SoporteBeneficio
    extra = 0
    readonly_fields = ('nombre_original', 'tipo_mime', 'fecha_subida')


class DependienteInline(admin.TabularInline):
    model = DependienteBeneficio
    extra = 0
    show_change_link = True


@admin.register(TramiteBeneficio)
class TramiteBeneficioAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'tipo', 'anio_aplicacion', 'estado',
                    'validado_por', 'validado_el', 'fecha_creacion')
    list_filter = ('estado', 'tipo', 'anio_aplicacion')
    search_fields = ('empleado__nombres', 'empleado__apellidos',
                     'empleado__numero_documento')
    readonly_fields = ('id', 'odoo_id', 'aplica_desde', 'vence_el',
                       'respuesta_odoo', 'enviado_a_odoo_el',
                       'ultimo_error_odoo', 'carta_generada_el',
                       'carta_firmada_el', 'fecha_creacion', 'fecha_actualizacion')
    inlines = [SoporteInline, DependienteInline]


@admin.register(DependienteBeneficio)
class DependienteBeneficioAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'tramite', 'causal', 'numero_documento')
    list_filter = ('causal',)
    search_fields = ('nombres', 'numero_documento')


admin.site.register(SoporteBeneficio)
admin.site.register(SoporteDependiente)
