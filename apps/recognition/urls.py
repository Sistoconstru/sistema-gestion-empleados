
# =============================================================================
# apps/recognition/urls.py
# =============================================================================

from django.urls import path
from . import views

app_name = 'recognition'

urlpatterns = [
    # Dashboard principal
    path('', views.DashboardView.as_view(), name='index'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Gamificación
    path('puntos/', views.MisPuntosView.as_view(), name='mis_puntos'),
    path('insignias/', views.MisInsigniasView.as_view(), name='mis_insignias'),
    path('ranking/', views.RankingView.as_view(), name='ranking'),
    path('mis-logros/', views.MisLogrosView.as_view(), name='mis_logros'),
    
    # Beneficios
    path('beneficios/', views.BeneficiosView.as_view(), name='beneficios'),
    path('canjear/<int:beneficio_id>/', views.CanjearBeneficioView.as_view(), name='canjear_beneficio'),
    path('mis-canjes/', views.MisCanjesView.as_view(), name='mis_canjes'),
    
    # Gestión de canjes (administradores)
    path('admin-canjes/', views.AdminCanjesView.as_view(), name='admin_canjes'),
    path('aprobar-canje/<uuid:canje_id>/', views.AprobarCanjeView.as_view(), name='aprobar_canje'),
    path('rechazar-canje/<uuid:canje_id>/', views.RechazarCanjeView.as_view(), name='rechazar_canje'),
    path('entregar-canje/<uuid:canje_id>/', views.EntregarCanjeView.as_view(), name='entregar_canje'),
    
    # Reportes
    path('generar-reporte-ranking/', views.GenerarReporteRankingView.as_view(), name='generar_reporte_ranking'),
    path('generar-reporte/', views.GenerarReporteView.as_view(), name='generar_reporte'),
    
    # Acciones administrativas
    path('otorgar-puntos/', views.OtorgarPuntosView.as_view(), name='otorgar_puntos'),
    path('asignar-insignia/', views.AsignarInsigniaView.as_view(), name='asignar_insignia'),
    path('historial-empleado/<uuid:empleado_id>/', views.HistorialEmpleadoView.as_view(), name='historial_empleado'),
    
    # Reconocimientos (para implementar después)
    # path('reconocimientos/', views.MisReconocimientosView.as_view(), name='mis_reconocimientos'),
]

