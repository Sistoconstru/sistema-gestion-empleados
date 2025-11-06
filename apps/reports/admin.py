from django.contrib import admin

# Register your models here.

# =============================================================================
# apps/reports/admin.py
# =============================================================================

from django.contrib import admin
from .models import TipoReporte, ReporteGenerado

@admin.register(TipoReporte)
class TipoReporteAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'formato_salida', 'programable', 'activo')
    list_filter = ('categoria', 'formato_salida', 'activo')

@admin.register(ReporteGenerado)
class ReporteGeneradoAdmin(admin.ModelAdmin):
    list_display = ('tipo_reporte', 'usuario', 'fecha_generacion', 'estado', 'numero_registros')
    list_filter = ('estado', 'fecha_generacion')
    readonly_fields = ('fecha_generacion',)