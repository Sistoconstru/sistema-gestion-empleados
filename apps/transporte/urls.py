from django.urls import path

from . import views

app_name = 'transporte'

urlpatterns = [
    path('', views.flota, name='flota'),
    path('vehiculo/<uuid:vehiculo_id>/', views.detalle_vehiculo, name='detalle_vehiculo'),
    path('vehiculo/<uuid:vehiculo_id>/asignar/', views.asignar_conductor, name='asignar_conductor'),
]
