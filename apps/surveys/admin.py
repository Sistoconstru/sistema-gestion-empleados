from django.contrib import admin

# Register your models here.

# =============================================================================
# apps/surveys/admin.py
# =============================================================================

from django.contrib import admin
from .models import TipoEncuesta, Encuesta, PreguntaEncuesta, ParticipacionEncuesta

@admin.register(TipoEncuesta)
class TipoEncuestaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'obligatoria', 'anonima', 'activo')
    list_filter = ('obligatoria', 'anonima', 'activo')

@admin.register(Encuesta)
class EncuestaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo_encuesta', 'fecha_inicio', 'fecha_fin', 'activa')
    list_filter = ('activa', 'tipo_encuesta')

@admin.register(ParticipacionEncuesta)
class ParticipacionEncuestaAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'encuesta', 'completada', 'porcentaje_completado', 'fecha_inicio')
    list_filter = ('completada', 'encuesta')
