from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.views.generic import TemplateView


class EmpleadoLoginView(LoginView):
    template_name = 'authentication/login.html'