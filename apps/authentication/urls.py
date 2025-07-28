# =============================================================================
# apps/authentication/urls.py
# =============================================================================

from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import EmpleadoLoginView

app_name = 'authentication'

urlpatterns = [
    # URLs básicas de autenticación
    path('login/', EmpleadoLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='authentication/logout.html'), name='logout'),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='authentication/password_change.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='authentication/password_change_done.html'), name='password_change_done'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='authentication/password_reset.html',
            success_url=reverse_lazy('authentication:password_reset_done')
        ),
        name='password_reset'
    ),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='authentication/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), name='password_reset_complete'),
    
    
    # URLs personalizadas (implementar views después)
    # path('profile/', views.ProfileView.as_view(), name='profile'),
    # path('users/', views.UserListView.as_view(), name='user_list'),
]