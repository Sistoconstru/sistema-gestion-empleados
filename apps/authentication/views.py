from django.contrib.auth.views import LoginView  # Vista de login de Django
from django.shortcuts import render  # Función para renderizar templates
from django.views.generic import TemplateView  # Vistas genéricas basadas en clase

# Vista personalizada de login para empleados
class EmpleadoLoginView(LoginView):
    template_name = 'authentication/login.html'  # Template que se usará para el login