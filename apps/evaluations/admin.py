from django.contrib import admin

# =============================================================================
# apps/evaluations/admin.py
# =============================================================================

from django.contrib import admin
from .models import (
    TipoPregunta, Valoracion, PreguntaValoracion, OpcionRespuesta, 
    IntentoValoracion, RespuestaValoracion, CertificadoCapacitacion,
    TipoEvaluacion, EvaluacionDesempeño, AsignacionEvaluacion, ResultadoEvaluacion
)

# Registro del modelo TipoPregunta en el admin de Django
@admin.register(TipoPregunta)
class TipoPreguntaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'permite_opciones', 'permite_texto_libre')
    list_filter = ('permite_opciones', 'permite_texto_libre')

# Registro del modelo Valoracion en el admin de Django
@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacitacion', 'puntaje_maximo', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'fecha_creacion')

# Registro del modelo TipoEvaluacion en el admin de Django
@admin.register(TipoEvaluacion)
class TipoEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'dias_activacion', 'es_autoevaluacion', 'activo')
    list_filter = ('es_autoevaluacion', 'activo')

# Registro del modelo EvaluacionDesempeño en el admin de Django
@admin.register(EvaluacionDesempeño)
class EvaluacionDesempeñoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo_evaluacion', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'tipo_evaluacion')
    search_fields = ('codigo', 'nombre')

# Registro del modelo AsignacionEvaluacion en el admin de Django
@admin.register(AsignacionEvaluacion)
class AsignacionEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('empleado_evaluado', 'evaluacion', 'evaluador', 'estado', 'fecha_vencimiento')
    list_filter = ('estado', 'es_autoevaluacion')

# Registro del modelo CertificadoCapacitacion en el admin de Django
@admin.register(CertificadoCapacitacion)
class CertificadoCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('numero_certificado', 'inscripcion', 'fecha_emision', 'fecha_vencimiento')
    search_fields = ('numero_certificado',)
