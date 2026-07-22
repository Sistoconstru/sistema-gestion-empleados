# =============================================================================
# apps/employees/urls.py - URLs VERIFICADAS
# =============================================================================

from django.urls import path
from . import views, feed_views, views_polla_mundial

app_name = 'employees'

urlpatterns = [
    # Lista de empleados
    path('', views.EmpleadoListView.as_view(), name='empleado_list'),
    
    # CRUD de empleados
    path('crear/', views.EmpleadoCreateView.as_view(), name='empleado_create'),
    path('<uuid:pk>/', views.EmpleadoDetailView.as_view(), name='empleado_detail'),
    path('<uuid:pk>/editar/', views.EmpleadoUpdateView.as_view(), name='empleado_edit'),
    path('<uuid:pk>/inactivar/', views.empleado_inactivar, name='empleado_inactivar'),

    # Exportaciones individuales
    path('<uuid:pk>/export/', views.empleado_export_individual, name='empleado_export_individual'),
    path('<uuid:pk>/print/', views.empleado_print_view, name='empleado_print'),
    path('<uuid:pk>/historial/export/', views.empleado_historial_export, name='empleado_historial_export'),
    path('mi-perfil/', views.empleado_perfil_redirect, name='empleado_perfil'),
    path('perfil/<uuid:pk>/', views.EmpleadoPerfilView.as_view(), name='empleado_perfil_detail'),

    # Historial Familiar (autogestión del empleado)
    path('perfil/familia/', views.familia_panel, name='familia_panel'),
    path('perfil/familia/estado-civil/', views.familia_estado_civil_actualizar, name='familia_estado_civil'),
    path('perfil/familia/familiar/nuevo/', views.familiar_crear, name='familiar_crear'),
    path('perfil/familia/familiar/<uuid:familiar_id>/editar/', views.familiar_editar, name='familiar_editar'),
    path('perfil/familia/familiar/<uuid:familiar_id>/eliminar/', views.familiar_eliminar, name='familiar_eliminar'),
    path('perfil/familia/familiar/<uuid:familiar_id>/documento/subir/', views.documento_familiar_subir, name='documento_familiar_subir'),
    path('perfil/familia/documento/<uuid:documento_id>/eliminar/', views.documento_familiar_eliminar, name='documento_familiar_eliminar'),

    # Panel de RRHH/Admin (staff/superuser, sin requerir Empleado vinculado)
    path('admin/', views.panel_admin, name='panel_admin'),

    # Vista cruzada de familiares (staff/RRHH)
    path('admin/familiares/', views.familiares_admin_lista, name='familiares_admin_lista'),
    path('admin/familiares/export/', views.familiares_admin_export_excel, name='familiares_admin_export'),

    # Vacaciones (jefe → Odoo)
    path('jefe/vacaciones/', views.vacaciones_equipo, name='vacaciones_equipo'),
    path('jefe/vacaciones/nueva/<uuid:empleado_id>/', views.vacacion_nueva, name='vacacion_nueva'),

    # Mis vacaciones (empleado, solo lectura)
    path('mis-vacaciones/', views.mis_vacaciones, name='mis_vacaciones'),
    path('mis-vacaciones/<uuid:pk>/carta/', views.descargar_carta_vacaciones, name='descargar_carta_vacaciones'),

    # Vacaciones — Administración (staff/RRHH)
    path('admin/vacaciones/', views.vacaciones_admin_panel, name='vacaciones_admin_panel'),
    path('supervisor/<uuid:pk>/', views.EmpleadoDetailSupervisorView.as_view(), name='empleado_detail_supervisor'),
    # APIs y exportación
    path('api/search/', views.empleado_search_api, name='empleado_search_api'),
    path('api/jefes-potenciales/<int:cargo_id>/', views.obtener_jefes_potenciales, name='obtener_jefes_potenciales'),
    path('export/', views.empleado_export, name='empleado_export'),
    
    # Gestión de cargos
    path('<uuid:pk>/cambiar-cargo/', views.cambiar_cargo_empleado, name='cambiar_cargo'),
    
    # Reportes especiales
    path('periodo-prueba/', views.empleados_periodo_prueba_reporte, name='periodo_prueba_reporte'),
    path('<uuid:pk>/activar/', views.activar_empleado_individual, name='activar_empleado'),
    path('<uuid:pk>/desactivar-reprobado/', views.desactivar_empleado_reprobado, name='desactivar_empleado_reprobado'),
    
    # Historial de cargos (para futuras funcionalidades)
    # path('<uuid:pk>/historial/', views.HistorialCargoView.as_view(), name='historial_cargo'),

    # =============================================================================
    # MARKETPLACE - TÉRMINOS Y CONDICIONES
    # =============================================================================
    path('marketplace/terminos-condiciones/', views.TerminosCondicionesView.as_view(), name='terminos_condiciones'),

    # =============================================================================
    # MARKETPLACE - PRODUCTOS
    # =============================================================================
    path('marketplace/productos/', views.ProductoListView.as_view(), name='producto_list'),
    path('marketplace/productos/crear/', views.CrearProductoView.as_view(), name='crear_producto'),
    path('marketplace/productos/<uuid:pk>/', views.ProductoDetailView.as_view(), name='producto_detail'),
    path('marketplace/productos/<uuid:pk>/editar/', views.EditarProductoView.as_view(), name='editar_producto'),
    path('marketplace/productos/<uuid:pk>/eliminar/', views.EliminarProductoView.as_view(), name='eliminar_producto'),
    path('marketplace/productos/<uuid:pk>/mensaje/', views.enviar_mensaje_producto, name='enviar_mensaje_producto'),
    path('marketplace/productos/<uuid:pk>/separar/', views.separar_producto_view, name='separar_producto'),
    path('marketplace/mis-productos/', views.MisProductosView.as_view(), name='mis_productos'),
    path('marketplace/mis-compras/', views.MisComprasView.as_view(), name='mis_compras'),
    path('marketplace/productos/<uuid:producto_pk>/comprar/', views.ComprarProductoView.as_view(), name='comprar_producto'),
    path('marketplace/reservas/<uuid:reserva_id>/confirmar-entrega/', views.confirmar_entrega_reserva, name='confirmar_entrega_reserva'),
    path('marketplace/ventas/<uuid:venta_id>/calificar/', views.calificar_venta, name='calificar_venta'),

    # =============================================================================
    # MARKETPLACE - SUBASTAS
    # =============================================================================
    path('marketplace/subastas/', views.SubastaListView.as_view(), name='subasta_list'),
    path('marketplace/subastas/<uuid:pk>/', views.SubastaDetailView.as_view(), name='subasta_detail'),
    path('marketplace/subastas/<uuid:subasta_pk>/pujar/', views.PujarView.as_view(), name='pujar'),

    # =============================================================================
    # MARKETPLACE - REGALOS
    # =============================================================================
    path('marketplace/productos/<uuid:producto_pk>/regalar/', views.RegalarProductoView.as_view(), name='regalar_producto'),
    path('marketplace/productos/<uuid:producto_pk>/recibir-regalo/', views.ReceibirRegaloAjaxView.as_view(), name='recibir_regalo'),
    path('marketplace/mis-regalos/', views.MisRegalosView.as_view(), name='mis_regalos'),
    path('regalos/<uuid:regalo_id>/confirmar-entrega/', views.ConfirmarEntregaRegaloAjaxView.as_view(), name='confirmar_entrega_regalo'),
    path('regalos/<uuid:regalo_id>/revertir/', views.RevertirSolicitudRegaloAjaxView.as_view(), name='revertir_regalo'),

    # =============================================================================
    # MESSAGING - CONVERSACIONES
    # =============================================================================
    path('mensajeria/inbox/', views.InboxView.as_view(), name='inbox'),
    path('mensajeria/iniciar/', views.IniciarConversacionView.as_view(), name='iniciar_conversacion'),
    path('mensajeria/conversacion/<uuid:pk>/', views.ConversacionDetailView.as_view(), name='conversacion_detail'),
    path('mensajeria/conversacion/<uuid:conversacion_pk>/mensaje/', views.EnviarMensajeView.as_view(), name='enviar_mensaje'),
    path('mensajeria/conversacion/<uuid:conversacion_pk>/marcar-leidos/', views.marcar_mensajes_leidos, name='marcar_mensajes_leidos'),
    path('mensajeria/contactar/<uuid:empleado_id>/', views.contactar_empleado, name='contactar_empleado'),

    # =============================================================================
    # FEED/PUBLICACIONES (MINIFACEBOOK)
    # =============================================================================
    path('feed/', feed_views.FeedListView.as_view(), name='feed_list'),
    path('feed/publicacion/crear/', feed_views.CrearPublicacionView.as_view(), name='crear_publicacion'),
    path('feed/publicacion/rapida/', feed_views.crear_publicacion_rapida, name='crear_publicacion_rapida'),
    path('feed/publicacion/<uuid:pk>/eliminar/', feed_views.EliminarPublicacionView.as_view(), name='eliminar_publicacion'),
    path('feed/publicacion/<uuid:publicacion_pk>/comentario/', feed_views.agregar_comentario, name='agregar_comentario'),
    path('feed/comentario/<uuid:comentario_id>/eliminar/', feed_views.eliminar_comentario, name='eliminar_comentario'),
    path('feed/anuncio/crear/', feed_views.CrearAnuncioImportanteView.as_view(), name='crear_anuncio'),
    path('feed/preview-renderizado/', feed_views.preview_renderizado_anuncio, name='preview_renderizado_anuncio'),
    path('feed/estilos-editor/', feed_views.editor_estilos, name='editor_estilos'),

    # =============================================================================
    # POLLA MUNDIALISTA 2026
    # =============================================================================
    path('polla-mundial/', views_polla_mundial.polla_mundial_lista, name='polla_mundial'),
    path('polla-mundial/ranking/', views_polla_mundial.ranking_mundial, name='ranking_mundial'),
    path('polla-mundial/mis-predicciones/', views_polla_mundial.mis_predicciones, name='mis_predicciones'),
    path('polla-mundial/partido/<int:partido_id>/predecir/', views_polla_mundial.guardar_prediccion, name='guardar_prediccion'),
    path('polla-mundial/partido/<int:partido_id>/estadisticas/', views_polla_mundial.estadisticas_partido, name='estadisticas_partido'),
    path('polla-mundial/aceptar-terminos/', views_polla_mundial.aceptar_terminos_polla, name='aceptar_terminos_polla'),
]