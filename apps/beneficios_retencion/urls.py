from django.urls import path

from . import views


app_name = 'beneficios_retencion'

urlpatterns = [
    # Empleado
    path('marcar-declarante/', views.marcar_declarante, name='marcar_declarante'),
    path('mis-tramites/', views.mis_tramites, name='mis_tramites'),
    path('mis-tramites/nuevo/', views.nuevo_tramite, name='nuevo_tramite'),
    path('mis-tramites/<uuid:pk>/cancelar/', views.cancelar_tramite, name='cancelar_tramite'),

    # RRHH
    path('rrhh/', views.bandeja_rrhh, name='bandeja_rrhh'),
    path('rrhh/<uuid:pk>/', views.detalle_rrhh, name='detalle_rrhh'),
    path('rrhh/<uuid:pk>/validar/', views.validar_tramite, name='validar_tramite'),
    path('rrhh/<uuid:pk>/rechazar/', views.rechazar_tramite, name='rechazar_tramite'),
    path('rrhh/<uuid:pk>/revocar/', views.revocar_tramite, name='revocar_tramite'),
    path('rrhh/<uuid:pk>/reintentar-odoo/', views.reintentar_envio_odoo, name='reintentar_envio_odoo'),
    path('rrhh/<uuid:pk>/carta/', views.descargar_carta, name='descargar_carta'),
    path('rrhh/<uuid:pk>/marcar-firmada/', views.marcar_carta_firmada, name='marcar_carta_firmada'),
]
