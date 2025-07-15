
# =============================================================================
# apps/documents/urls.py
# =============================================================================

from django.urls import path
from django.views.generic import TemplateView

app_name = 'documents'

urlpatterns = [
    # URLs básicas
    path('', TemplateView.as_view(template_name='documents/index.html'), name='index'),
    
    # Documentos
    # path('upload/', views.DocumentUploadView.as_view(), name='document_upload'),
    # path('list/', views.DocumentListView.as_view(), name='document_list'),
    # path('<uuid:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    # path('<uuid:pk>/approve/', views.DocumentApproveView.as_view(), name='document_approve'),
    
    # Tipos de documento
    # path('tipos/', views.TipoDocumentoListView.as_view(), name='tipo_documento_list'),
]