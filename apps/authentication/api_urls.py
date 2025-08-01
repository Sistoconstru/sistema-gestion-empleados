# =============================================================================
# apps/authentication/api_urls.py
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Importa las vistas de la API (comentado por ahora)
# from . import api_views

# Crea un router para las vistas basadas en ViewSet
router = DefaultRouter()
# Registra el ViewSet de usuarios en el router (comentado por ahora)
# router.register(r'users', api_views.UserViewSet)
# Registra el ViewSet de roles en el router (comentado por ahora)
# router.register(r'roles', api_views.RolViewSet)

# Define las rutas de la API
urlpatterns = [
    # Incluye las rutas generadas por el router
    path('', include(router.urls)),
    # Ruta para login de la API (comentada por ahora)
    # path('login/', api_views.LoginAPIView.as_view(), name='api_login'),
    # Ruta para logout de la API (comentada por ahora)
    # path('logout/', api_views.LogoutAPIView.as_view(), name='api_logout'),
]