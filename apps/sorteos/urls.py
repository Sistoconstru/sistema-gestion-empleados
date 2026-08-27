from django.urls import path
from . import views

app_name = 'sorteos'

urlpatterns = [
    # Empleado
    path('', views.SorteosIndexView.as_view(), name='index'),
    path('<uuid:pk>/inscribirme/', views.InscribirseSorteoView.as_view(), name='inscribirme'),

    # Admin
    path('admin/', views.SorteoAdminListView.as_view(), name='admin_lista'),
    path('admin/crear/', views.SorteoFormView.as_view(), name='crear'),
    path('admin/<uuid:pk>/editar/', views.SorteoFormView.as_view(), name='editar'),
    path('admin/<uuid:pk>/inscritos/', views.InscritosSorteoView.as_view(), name='inscritos'),
    path('admin/<uuid:pk>/inscritos/exportar/', views.ExportarInscritosView.as_view(), name='exportar_inscritos'),
    path('admin/<uuid:pk>/realizar/', views.RealizarSorteoView.as_view(), name='realizar'),
    path('admin/<uuid:pk>/realizar/buscar/', views.BuscarNumeroSorteoView.as_view(), name='buscar_numero'),
    path('admin/<uuid:pk>/realizar/registrar/', views.RegistrarGanadorView.as_view(), name='registrar_ganador'),
]
