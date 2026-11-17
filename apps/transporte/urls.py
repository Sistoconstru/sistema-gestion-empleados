from django.urls import path

from . import views

app_name = 'transporte'

urlpatterns = [
    # Flota — jefe y director
    path('', views.flota, name='flota'),
    path('vehiculo/<uuid:vehiculo_id>/', views.detalle_vehiculo, name='detalle_vehiculo'),
    path('vehiculo/<uuid:vehiculo_id>/asignar/', views.asignar_conductor, name='asignar_conductor'),
    path('vehiculo/<uuid:vehiculo_id>/documento/', views.registrar_documento, name='registrar_documento'),

    # Servicios — los asigna Odoo, acá solo se listan
    path('servicios/', views.servicios, name='servicios'),

    # Gastos — conductor
    path('mis-gastos/', views.mis_gastos, name='mis_gastos'),
    path('mis-gastos/nuevo/', views.registrar_gasto, name='registrar_gasto'),
    path('mis-gastos/<uuid:gasto_id>/editar/', views.editar_gasto, name='editar_gasto'),

    # Gastos — jefe y director
    path('gastos/', views.gastos_flota, name='gastos_flota'),
    path('gastos/<uuid:gasto_id>/revisar/', views.revisar_gasto, name='revisar_gasto'),
]
