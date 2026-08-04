# =============================================================================
# apps/training/urls.py
# =============================================================================

from django.urls import path
from django.views.generic import TemplateView
from . import views, views_sesiones
from .views import MisCertificadosView, PlayerPreviewView
from .views_pdf import PDFMediaView
 # PDF seguro con CORS


app_name = 'training'

urlpatterns = [
    # URLs básicas
    path('', TemplateView.as_view(template_name='training/index.html'), name='index'),
    #path('', views.MisCapacitacionesView.as_view(), name='mis_capacitaciones'),
    path('catalogo/', views.CatalogoCapacitacionesView.as_view(), name='catalogo'),
    path('capacitacion/<uuid:pk>/', views.CapacitacionDetailView.as_view(), name='capacitacion_detail'),
    path('capacitacion/<uuid:pk>/inscribir/', views.inscribir_capacitacion, name='inscribir_capacitacion'),  # pk en lugar de capacitacion_id
    path('admin/', views.CapacitacionListView.as_view(), name='capacitacion_list'),

    # Vista previa solo lectura para admin
    path('player-preview/<uuid:pk>/', PlayerPreviewView.as_view(), name='player_preview'),
    
    # Capacitaciones
    # path('list/', views.CapacitacionListView.as_view(), name='capacitacion_list'),
    # path('create/', views.CapacitacionCreateView.as_view(), name='capacitacion_create'),
    # path('<uuid:pk>/', views.CapacitacionDetailView.as_view(), name='capacitacion_detail'),
    
    # Inscripciones
    path('mis-capacitaciones/', views.MisCapacitacionesView.as_view(), name='mis_capacitaciones'),
    # path('<uuid:pk>/inscribir/', views.InscribirCapacitacionView.as_view(), name='inscribir_capacitacion'),
    
    # Módulos y lecciones
    # path('<uuid:pk>/modulos/', views.ModuloListView.as_view(), name='modulo_list'),
    # path('modulo/<uuid:pk>/lecciones/', views.LeccionListView.as_view(), name='leccion_list'),
    path('player/<uuid:pk>/', views.PlayerView.as_view(), name='player'),
    path('contenido/<uuid:pk>/completar/', views.completar_contenido, name='completar_contenido'),

    # Certificados
    path('mis-certificados/', MisCertificadosView.as_view(), name='mis_certificados'),
    path('certificado/<uuid:pk>/descargar/', views.descargar_certificado, name='descargar_certificado'),
    path('certificado/plantilla/<int:plantilla_id>/vista-previa/', views.vista_previa_certificado, name='vista_previa_certificado'),
    
    # Validación de inscripciones
    path('inscripcion/<uuid:pk>/aprobar-solicitud/', views.aprobar_solicitud_inscripcion, name='aprobar_solicitud_inscripcion'),
    path('inscripcion/<uuid:pk>/validar-certificado/', views.validar_certificado_externo, name='validar_certificado_externo'),
    path('inscripcion/<uuid:pk>/validar/', views.validar_inscripcion, name='validar_inscripcion'),  # Deprecated
    path('inscripcion/<uuid:pk>/rechazar/', views.rechazar_inscripcion, name='rechazar_inscripcion'),
    path('inscripcion/<uuid:pk>/cancelar/', views.cancelar_inscripcion_empleado, name='cancelar_inscripcion_empleado'),
    
    # Quizzes y valoraciones
    path('quiz/<int:pk>/', views.QuizView.as_view(), name='quiz'),
    path('quiz/<int:pk>/resultado/', views.QuizResultadoView.as_view(), name='quiz_resultado'),
    path('quiz/intento/<int:intento_id>/respuesta/', views.guardar_respuesta_quiz, name='guardar_respuesta_quiz'),
    path('quiz/intento/<int:intento_id>/finalizar/', views.finalizar_quiz, name='finalizar_quiz'),
    path('media-pdf/<path:path>/', PDFMediaView.as_view(), name='media_pdf'),

    # Capacitaciones presenciales — sesiones
    path('sesiones/', views_sesiones.SesionesAbiertasView.as_view(), name='sesiones_abiertas'),
    path('sesiones/mis-sesiones/', views_sesiones.MisSesionesView.as_view(), name='mis_sesiones'),
    path('sesiones/<uuid:pk>/', views_sesiones.SesionDetailView.as_view(), name='sesion_detail'),
    path('sesiones/<uuid:pk>/inscribirse/', views_sesiones.inscribirse_sesion, name='inscribirse_sesion'),
    path('sesiones/inscripcion/<uuid:pk>/cancelar/', views_sesiones.cancelar_inscripcion_sesion, name='cancelar_inscripcion_sesion'),
]