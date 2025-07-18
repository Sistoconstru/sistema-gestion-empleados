# =============================================================================
# apps/authentication/urls.py
# =============================================================================

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'authentication'

urlpatterns = [
    # URLs básicas de autenticación
    path('login/', auth_views.LoginView.as_view(template_name='authentication/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='authentication/password_change.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='authentication/password_change_done.html'), name='password_change_done'),
    
    # URLs personalizadas (implementar views después)
    # path('profile/', views.ProfileView.as_view(), name='profile'),
    # path('users/', views.UserListView.as_view(), name='user_list'),
]