# =============================================================================
# apps/surveys/urls.py
# =============================================================================

from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    # Dashboard principal
    path('', views.DashboardView.as_view(), name='index'),

    # Encuestas (usuario)
    path('lista/', views.EncuestaListView.as_view(), name='encuesta_list'),
    path('responder/<uuid:pk>/', views.ResponderEncuestaView.as_view(), name='responder_encuesta'),
    path('mis-encuestas/', views.MisEncuestasView.as_view(), name='mis_encuestas'),

    # Administración de encuestas (solo staff/superuser)
    path('admin/lista/', views.EncuestaAdminListView.as_view(), name='encuesta_admin_list'),
    path('admin/crear/', views.CrearEncuestaView.as_view(), name='crear_encuesta'),
    path('admin/<uuid:pk>/preguntas/', views.EditarPreguntasView.as_view(), name='editar_preguntas'),
    path('admin/<uuid:pk>/asignar/', views.AsignarEncuestaView.as_view(), name='asignar_encuesta'),

    # Resultados
    path('admin/<uuid:pk>/resultados/', views.ResultadosEncuestaView.as_view(), name='resultados_encuesta'),
    path('admin/<uuid:pk>/exportar/', views.ExportarRespuestasEncuestaView.as_view(), name='exportar_respuestas_encuesta'),

    # Edición: encuesta, preguntas y opciones (Bloque A)
    path('admin/<uuid:pk>/editar/', views.EditarEncuestaView.as_view(), name='editar_encuesta'),
    path('admin/<uuid:pk>/toggle-activa/', views.ToggleActivaEncuestaView.as_view(), name='toggle_activa_encuesta'),
    path('admin/<uuid:pk>/pregunta/<uuid:pregunta_id>/editar/', views.EditarPreguntaView.as_view(), name='editar_pregunta'),
    path('admin/<uuid:pk>/pregunta/<uuid:pregunta_id>/eliminar/', views.EliminarPreguntaView.as_view(), name='eliminar_pregunta'),
    path('admin/<uuid:pk>/pregunta/<uuid:pregunta_id>/mover/', views.MoverPreguntaView.as_view(), name='mover_pregunta'),
    path('admin/<uuid:pk>/pregunta/<uuid:pregunta_id>/opcion/crear/', views.CrearOpcionView.as_view(), name='crear_opcion'),
    path('admin/<uuid:pk>/pregunta/<uuid:pregunta_id>/opcion/<uuid:opcion_id>/editar/', views.EditarOpcionView.as_view(), name='editar_opcion'),
    path('admin/<uuid:pk>/pregunta/<uuid:pregunta_id>/opcion/<uuid:opcion_id>/eliminar/', views.EliminarOpcionView.as_view(), name='eliminar_opcion'),

    # Preview y duplicar (Bloque B)
    path('admin/<uuid:pk>/preview/', views.PreviewEncuestaView.as_view(), name='preview_encuesta'),
    path('admin/<uuid:pk>/duplicar/', views.DuplicarEncuestaView.as_view(), name='duplicar_encuesta'),
]