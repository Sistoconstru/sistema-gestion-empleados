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

    # Resultados (para implementar después)
    # path('resultados/<uuid:pk>/', views.ResultadosEncuestaView.as_view(), name='resultados_encuesta'),
]