
# =============================================================================
# apps/documents/urls.py
# =============================================================================
from django.views.generic import TemplateView

from django.urls import path
from . import views
from . import views_proxy

app_name = 'documents'

urlpatterns = [
    # Página de inicio
    path('', TemplateView.as_view(template_name='documents/index.html'), name='index'),
    
    # Gestión de documentos por empleado
    path('empleado/<uuid:empleado_pk>/', views.documento_empleado_detail, name='empleado_documentos'),
    
    # Subir documentos
    path('empleado/<uuid:empleado_pk>/subir/', views.documento_upload, name='documento_upload'),
    path('empleado/<uuid:empleado_pk>/subir-multiple/', views.documento_multiple_upload, name='documento_multiple_upload'),
    
    # Aprobar documentos
    path('documento/<uuid:documento_pk>/aprobar/', views.documento_approve, name='documento_approve'),
    # Visualizar documento (solo lectura o aprobación)
    path('documento/<uuid:documento_pk>/ver/', views.documento_approve, name='documento_view'),
    
    # Descargar documento
    path('documento/<uuid:documento_pk>/descargar/', views.documento_download, name='documento_download'),
    
    # Reemplazar documento rechazado
    path('documento/<uuid:documento_id>/reemplazar/', views.documento_replace, name='documento_replace'),
    
    # APIs
    path('api/pendientes/', views.documentos_pendientes_api, name='documentos_pendientes_api'),
    
    # Lista general (para administradores)
    path('', views.DocumentoEmpleadoListView.as_view(), name='documento_list'),
    path('proxy-pdf/', views_proxy.proxy_pdf, name='proxy_pdf'),
]