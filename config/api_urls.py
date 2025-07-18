from django.urls import path, include

urlpatterns = [
    path('auth/', include('apps.authentication.api_urls')),
    path('empleados/', include('apps.employees.api_urls')),
    path('organizacional/', include('apps.organizational.api_urls')),
    path('documentos/', include('apps.documents.api_urls')),
    path('capacitaciones/', include('apps.training.api_urls')),
    path('evaluaciones/', include('apps.evaluations.api_urls')),
    path('encuestas/', include('apps.surveys.api_urls')),
    path('reconocimientos/', include('apps.recognition.api_urls')),
    path('notificaciones/', include('apps.notifications.api_urls')),
    path('reportes/', include('apps.reports.api_urls')),
]