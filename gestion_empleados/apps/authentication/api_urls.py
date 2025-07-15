
# =============================================================================
# apps/authentication/api_urls.py
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from . import api_views

router = DefaultRouter()
# router.register(r'users', api_views.UserViewSet)
# router.register(r'roles', api_views.RolViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('login/', api_views.LoginAPIView.as_view(), name='api_login'),
    # path('logout/', api_views.LogoutAPIView.as_view(), name='api_logout'),
]