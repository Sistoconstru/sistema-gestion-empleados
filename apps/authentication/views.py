from django.contrib.auth.views import LoginView, PasswordChangeView  # Vistas de auth de Django
from django.shortcuts import render  # Función para renderizar templates
from django.urls import reverse_lazy
from django.views.generic import TemplateView  # Vistas genéricas basadas en clase

# Vista personalizada de login para empleados
class EmpleadoLoginView(LoginView):
    template_name = 'authentication/login.html'  # Template que se usará para el login


class CambiarPasswordView(PasswordChangeView):
    """Cambio de contraseña que además apaga el flag `debe_cambiar_password`.

    Es el único camino de salida del ForzarCambioPasswordMiddleware: mientras el
    flag siga activo, el middleware redirige todo aquí.
    """
    template_name = 'authentication/password_change.html'
    success_url = reverse_lazy('authentication:password_change_done')

    def form_valid(self, form):
        respuesta = super().form_valid(form)  # guarda la contraseña y renueva la sesión
        usuario = self.request.user
        if getattr(usuario, 'debe_cambiar_password', False):
            usuario.debe_cambiar_password = False
            usuario.save(update_fields=['debe_cambiar_password'])
        return respuesta
