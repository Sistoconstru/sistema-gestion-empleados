
# =============================================================================
# apps/recognition/urls.py
# =============================================================================

from django.urls import path
from django.views.generic import TemplateView

app_name = 'recognition'

urlpatterns = [
    # URLs básicas
    path('', TemplateView.as_view(template_name='recognition/index.html'), name='index'),
    
    # Gamificación
    # path('puntos/', views.MisPuntosView.as_view(), name='mis_puntos'),
    # path('insignias/', views.MisInsigniasView.as_view(), name='mis_insignias'),
    # path('ranking/', views.RankingView.as_view(), name='ranking'),
    
    # Beneficios
    # path('beneficios/', views.BeneficiosView.as_view(), name='beneficios'),
    # path('canjear/<int:pk>/', views.CanjearBeneficioView.as_view(), name='canjear_beneficio'),
    
    # Reconocimientos
    # path('reconocimientos/', views.MisReconocimientosView.as_view(), name='mis_reconocimientos'),
]

