from django.contrib import admin

# Register your models here.
# =============================================================================
# apps/evaluations/admin.py
# =============================================================================

from django.contrib import admin
from .models import (TipoPregunta, Valoracion, PreguntaValoracion, OpcionRespuesta, 
                     IntentoValoracion, RespuestaValoracion, CertificadoCapacitacion,
                     TipoEvaluacion, EvaluacionDesempeño, AsignacionEvaluacion, ResultadoEvaluacion)

@admin.register(TipoPregunta)
class TipoPreguntaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'permite_opciones', 'permite_texto_libre')
    list_filter = ('permite_opciones', 'permite_texto_libre')

@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacitacion', 'puntaje_maximo', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'fecha_creacion')

@admin.register(TipoEvaluacion)
class TipoEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'dias_activacion', 'es_autoevaluacion', 'activo')
    list_filter = ('es_autoevaluacion', 'activo')

@admin.register(EvaluacionDesempeño)
class EvaluacionDesempeñoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo_evaluacion', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'tipo_evaluacion')

@admin.register(AsignacionEvaluacion)
class AsignacionEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('empleado_evaluado', 'evaluacion', 'evaluador', 'estado', 'fecha_vencimiento')
    list_filter = ('estado', 'es_autoevaluacion')

@admin.register(CertificadoCapacitacion)
class CertificadoCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('numero_certificado', 'inscripcion', 'fecha_emision', 'fecha_vencimiento')
    search_fields = ('numero_certificado',)
