from django.contrib import admin
from .models import Sorteo, InscripcionSorteo, GanadorSorteo


@admin.register(Sorteo)
class SorteoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'cantidad_premios', 'activo',
                    'fecha_inicio_inscripcion', 'fecha_fin_inscripcion', 'fecha_sorteo')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre')


@admin.register(InscripcionSorteo)
class InscripcionSorteoAdmin(admin.ModelAdmin):
    list_display = ('sorteo', 'numero', 'empleado', 'fecha_inscripcion')
    list_filter = ('sorteo',)
    search_fields = ('empleado__nombres', 'empleado__primer_apellido', 'empleado__documento')
    autocomplete_fields = ('sorteo', 'empleado')


@admin.register(GanadorSorteo)
class GanadorSorteoAdmin(admin.ModelAdmin):
    list_display = ('sorteo', 'orden_premio', 'inscripcion', 'fecha_seleccion', 'seleccionado_por')
    list_filter = ('sorteo',)
    autocomplete_fields = ('sorteo', 'inscripcion', 'seleccionado_por')
