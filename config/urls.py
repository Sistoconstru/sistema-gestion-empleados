"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from apps.authentication.views import EmpleadoLoginView
from django.urls import reverse_lazy
from apps.core.views import dashboard_view

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('login/', EmpleadoLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='authentication/logout.html'), name='logout'),
    path('auth/', include('apps.authentication.urls')),
    path('dashboard/', include('apps.core.urls')),
    path('empleados/', include('apps.employees.urls')),
    path('organizacional/', include('apps.organizational.urls')),
    path('documentos/', include('apps.documents.urls')),
    path('capacitaciones/', include('apps.training.urls')),
    path('evaluaciones/', include('apps.evaluations.urls')),
    path('encuestas/', include('apps.surveys.urls')),
    path('reconocimientos/', include('apps.recognition.urls')),
    path('notificaciones/', include('apps.notifications.urls')),
    path('reportes/', include('apps.reports.urls')),
    
    
    
    # API URLs
    path('api/v1/', include('config.api_urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# También servir desde STATICFILES_DIRS
    from django.contrib.staticfiles.views import serve
    from django.urls import re_path
    
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve),
    ]