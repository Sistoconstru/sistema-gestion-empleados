from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import (
    HistorialCargo, Empleado, Producto, Venta, Subasta,
    PujaSubasta, Regalo, Conversacion, Mensaje, Publicacion
)
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Empleado)
def crear_usuario_automatico_empleado(sender, instance, created, **kwargs):
    """Crea el usuario y asigna el rol cuando se crea un empleado nuevo sin usuario"""
    # Flag para evitar duplicidad en el ciclo de guardado
    if created and not instance.usuario and not hasattr(instance, '_usuario_creado_flag'):
        setattr(instance, '_usuario_creado_flag', True)
        from django.db import transaction
        def crear_usuario_post_commit():
            User = get_user_model()
            try:
                primer_nombre = instance.nombres.split()[0].lower()
                primer_apellido = instance.apellidos.split()[0].lower()
                username_base = f"{primer_nombre}.{primer_apellido}"

                username = username_base
                counter = 1
                # Buscar username único, incluso si hay homónimos
                while User.objects.filter(username=username).exists():
                    username = f"{username_base}{counter}"
                    counter += 1

                password = f"{primer_nombre.capitalize()}{instance.numero_documento}"

                # Verificar que no exista ya un usuario con ese username y correo
                if not User.objects.filter(username=username, email=instance.correo_electronico).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=instance.correo_electronico or '',
                        first_name=instance.nombres,
                        last_name=instance.apellidos,
                        password=password,
                        is_active=True
                    )

                    # Asignar rol automático desde el cargo si existe historial activo
                    historial = instance.historialcargo_set.filter(activo=True).first()
                    if historial and historial.cargo and hasattr(historial.cargo, 'rol_automatico') and historial.cargo.rol_automatico:
                        from apps.authentication.models import UsuarioRol
                        superuser = User.objects.filter(is_superuser=True).first()
                        # Evitar duplicidad de UsuarioRol
                        if not UsuarioRol.objects.filter(usuario=user, rol=historial.cargo.rol_automatico).exists():
                            UsuarioRol.objects.create(
                                usuario=user,
                                rol=historial.cargo.rol_automatico,
                                asignado_por=superuser
                            )

                    # Asignar el usuario al empleado solo si sigue sin usuario, evitando save() para no disparar el signal nuevamente
                    if not instance.usuario:
                        Empleado.objects.filter(pk=instance.pk).update(usuario=user)

            except Exception as e:
                print(f"[ERROR al crear usuario automático]: {e}")

        transaction.on_commit(crear_usuario_post_commit)


@receiver(pre_save, sender=Empleado)
def capturar_estado_anterior(sender, instance, **kwargs):
    """Captura el estado anterior del empleado antes de guardarlo"""
    if instance.pk:
        try:
            instance._estado_anterior = Empleado.objects.get(pk=instance.pk).estado
        except Empleado.DoesNotExist:
            instance._estado_anterior = None
    else:
        instance._estado_anterior = None


@receiver(post_save, sender=Empleado)
def registrar_cambio_estado(sender, instance, created, **kwargs):
    """Registra cambios de estado de empleados para auditoría"""
    if not created and hasattr(instance, '_estado_anterior'):
        estado_anterior = instance._estado_anterior
        estado_actual = instance.estado
        
        if estado_anterior and estado_anterior != estado_actual:
            # Detectar si fue un cambio automático de periodo de prueba a activo
            es_activacion_automatica = (
                estado_anterior.codigo == 'p-prue' and 
                estado_actual.codigo == '999'
            )
            
            # Log del cambio de estado
            if es_activacion_automatica:
                logger.info(
                    f"ACTIVACIÓN AUTOMÁTICA: Empleado {instance.numero_documento} "
                    f"({instance.nombre_completo}) cambió de estado '{estado_anterior.nombre}' "
                    f"a '{estado_actual.nombre}' automáticamente por cumplir periodo de prueba"
                )
            else:
                logger.info(
                    f"CAMBIO DE ESTADO: Empleado {instance.numero_documento} "
                    f"({instance.nombre_completo}) cambió de estado '{estado_anterior.nombre}' "
                    f"a '{estado_actual.nombre}'"
                )
        
        # Limpiar el estado anterior
        delattr(instance, '_estado_anterior')


# ===================== SIGNALS PARA MARKETPLACE Y NOTIFICACIONES =====================

@receiver(post_save, sender=Producto)
def notificar_nuevo_producto(sender, instance, created, **kwargs):
    """
    Notificar cuando se crea un nuevo producto
    """
    if created:
        try:
            from apps.notifications.models import Notificacion, TipoNotificacion

            tipo_notif = TipoNotificacion.objects.get(codigo='producto_publicado', activo=True)
            datos = {
                'titulo_producto': instance.titulo,
                'tipo': instance.get_tipo_display(),
                'vendedor': instance.vendedor.nombre_completo,
            }

            Notificacion.objects.create(
                usuario=instance.vendedor.usuario,
                tipo_notificacion=tipo_notif,
                titulo=tipo_notif.plantilla_titulo.format(**datos),
                mensaje=tipo_notif.plantilla_mensaje.format(**datos),
                datos_adicionales=datos
            )
        except Exception as e:
            logger.warning(f"Error al crear notificación de producto: {e}")


@receiver(post_save, sender=Venta)
def notificar_compra_realizada(sender, instance, created, **kwargs):
    """
    Notificar al vendedor cuando se realiza una compra
    """
    if created:
        try:
            from apps.notifications.models import Notificacion, TipoNotificacion

            tipo_notif = TipoNotificacion.objects.get(codigo='compra_recibida', activo=True)
            datos = {
                'titulo_producto': instance.producto.titulo,
                'comprador': instance.comprador.nombre_completo,
                'precio': f"${instance.precio:,.0f}",
            }

            Notificacion.objects.create(
                usuario=instance.producto.vendedor.usuario,
                tipo_notificacion=tipo_notif,
                titulo=tipo_notif.plantilla_titulo.format(**datos),
                mensaje=tipo_notif.plantilla_mensaje.format(**datos),
                datos_adicionales=datos
            )
        except Exception as e:
            logger.warning(f"Error al crear notificación de compra: {e}")


@receiver(post_save, sender=PujaSubasta)
def notificar_nueva_puja(sender, instance, created, **kwargs):
    """
    Notificar cuando se realiza una nueva puja
    """
    if created:
        try:
            from apps.notifications.models import Notificacion, TipoNotificacion

            tipo_notif = TipoNotificacion.objects.get(codigo='nueva_puja_recibida', activo=True)
            datos = {
                'titulo_producto': instance.subasta.producto.titulo,
                'monto': f"${instance.monto:,.0f}",
                'pujador': instance.pujador.nombre_completo,
            }

            Notificacion.objects.create(
                usuario=instance.subasta.vendedor.usuario,
                tipo_notificacion=tipo_notif,
                titulo=tipo_notif.plantilla_titulo.format(**datos),
                mensaje=tipo_notif.plantilla_mensaje.format(**datos),
                datos_adicionales=datos
            )
        except Exception as e:
            logger.warning(f"Error al crear notificación de puja: {e}")


@receiver(post_save, sender=Regalo)
def notificar_regalo_recibido(sender, instance, created, **kwargs):
    """
    Notificar al donante cuando alguien solicita un regalo (estado='pendiente')
    Notificar al receptor cuando el donante confirma entrega (estado='aceptado')
    """
    try:
        from apps.notifications.models import Notificacion, TipoNotificacion

        if created and instance.estado == 'pendiente':
            # Notificar al donante que alguien solicitó su regalo
            tipo_notif = TipoNotificacion.objects.get(codigo='regalo_aceptado', activo=True)
            datos = {
                'titulo_producto': instance.producto.titulo,
                'receptor': instance.receptor.nombre_completo,
            }

            Notificacion.objects.create(
                usuario=instance.donante.usuario,
                tipo_notificacion=tipo_notif,
                titulo=f'{instance.receptor.nombre_completo} solicitó tu regalo',
                mensaje=f'{instance.receptor.nombre_completo} solicitó tu regalo "{instance.producto.titulo}"',
                datos_adicionales=datos
            )
            logger.info(f"[NOTIF] Notificación enviada a {instance.donante.nombre_completo} sobre solicitud de regalo")

        elif not created and instance.estado == 'aceptado' and instance.confirmado_por_donante:
            # Notificar al receptor que el donante confirmó entrega
            tipo_notif = TipoNotificacion.objects.get(codigo='regalo_recibido', activo=True)
            datos = {
                'titulo_producto': instance.producto.titulo,
                'donante': instance.donante.nombre_completo,
            }

            Notificacion.objects.create(
                usuario=instance.receptor.usuario,
                tipo_notificacion=tipo_notif,
                titulo=f'{instance.donante.nombre_completo} confirmó tu regalo',
                mensaje=f'{instance.donante.nombre_completo} confirmó la entrega de tu regalo "{instance.producto.titulo}"',
                datos_adicionales=datos
            )
            logger.info(f"[NOTIF] Notificación enviada a {instance.receptor.nombre_completo} sobre confirmación de regalo")

    except Exception as e:
        logger.warning(f"Error al crear notificación de regalo: {e}")


@receiver(post_save, sender=Mensaje)
def notificar_nuevo_mensaje(sender, instance, created, **kwargs):
    """
    Notificar a los otros participantes cuando se recibe un mensaje
    """
    if created:
        try:
            from apps.notifications.models import Notificacion, TipoNotificacion

            tipo_notif = TipoNotificacion.objects.get(codigo='nuevo_mensaje', activo=True)
            otros_participantes = instance.conversacion.participantes.exclude(
                id=instance.remitente.id
            )

            datos = {
                'remitente': instance.remitente.nombre_completo,
                'titulo_conversacion': instance.conversacion.titulo or 'Conversación',
                'conversacion_id': str(instance.conversacion.id),  # Agregado para navegar desde notificaciones
                'url': f'/empleados/mensajeria/conversacion/{instance.conversacion.id}/',  # URL directa
            }

            for participante in otros_participantes:
                Notificacion.objects.create(
                    usuario=participante.usuario,
                    tipo_notificacion=tipo_notif,
                    titulo=tipo_notif.plantilla_titulo.format(**datos),
                    mensaje=tipo_notif.plantilla_mensaje.format(**datos),
                    datos_adicionales=datos
                )
        except Exception as e:
            logger.warning(f"Error al crear notificación de mensaje: {e}")


# ===================== SIGNALS PARA FEED/PUBLICACIONES =====================

@receiver(post_save, sender=Publicacion)
def establecer_fecha_eliminacion_automatica(sender, instance, created, **kwargs):
    """Establece la fecha de eliminación automática a los 15 días para publicaciones normales"""
    if created and not instance.es_anuncio:
        from django.utils import timezone
        from datetime import timedelta

        fecha_eliminacion = timezone.now() + timedelta(days=15)
        Publicacion.objects.filter(pk=instance.pk).update(fecha_eliminacion_automatica=fecha_eliminacion)
        logger.info(f"Publicación {instance.pk} será eliminada el {fecha_eliminacion}")


@receiver(post_save, sender=Publicacion)
def notificar_anuncio_importante(sender, instance, created, **kwargs):
    """Notifica a todos los empleados cuando se crea un anuncio importante"""
    if created and instance.es_anuncio and instance.es_importante:
        try:
            from apps.notifications.models import Notificacion, TipoNotificacion
            from django.contrib.auth import get_user_model

            User = get_user_model()

            # Obtener o crear tipo de notificación para anuncios importantes
            tipo_notif, _ = TipoNotificacion.objects.get_or_create(
                codigo='anuncio_importante',
                defaults={
                    'nombre': 'Anuncio Importante',
                    'plantilla_titulo': 'Anuncio importante: {titulo}',
                    'plantilla_mensaje': '{contenido}',
                    'activo': True
                }
            )

            datos = {
                'titulo': instance.titulo or 'Anuncio importante',
                'contenido': instance.contenido[:100],
                'autor': instance.autor.nombre_completo,
                'fecha_fin': instance.fecha_fin.strftime('%d/%m/%Y %H:%M') if instance.fecha_fin else '',
                'publicacion_id': str(instance.id),
                'url': f'/empleados/feed/#publicacion-{instance.id}',
            }

            # Notificar a todos los empleados activos (excepto admins que ya lo saben)
            empleados = Empleado.objects.filter(usuario__is_active=True).select_related('usuario')

            for empleado in empleados:
                # No notificar al autor ni a admins
                if empleado != instance.autor and not empleado.usuario.is_staff:
                    Notificacion.objects.create(
                        usuario=empleado.usuario,
                        tipo_notificacion=tipo_notif,
                        titulo=tipo_notif.plantilla_titulo.format(**datos),
                        mensaje=tipo_notif.plantilla_mensaje.format(**datos),
                        datos_adicionales=datos
                    )

            logger.info(f"Anuncio importante '{instance.titulo}' notificado a {empleados.count()} empleados")

        except Exception as e:
            logger.warning(f"Error al crear notificación de anuncio importante: {e}")


@receiver(post_delete, sender=Publicacion)
def eliminar_recursos_publicacion(sender, instance, **kwargs):
    """
    Elimina los recursos asociados a una publicación:
    - Imagen de S3/almacenamiento
    - Notificaciones relacionadas
    """
    try:
        # Eliminar imagen de S3/almacenamiento si existe
        if instance.imagen:
            try:
                from django.core.files.storage import storages
                # Obtener el nombre del archivo desde el ImageField
                imagen_path = instance.imagen.name
                if imagen_path:
                    storages["default"].delete(imagen_path)
                    logger.info(f"[PUBLICACION] Imagen eliminada de S3: {imagen_path}")
            except Exception as e:
                logger.warning(f"[PUBLICACION] Error al eliminar imagen de S3: {e}")

        # Eliminar notificaciones que hagan referencia a esta publicación
        from apps.notifications.models import Notificacion

        notificaciones = Notificacion.objects.filter(
            datos_adicionales__publicacion_id=str(instance.id)
        )

        count = notificaciones.count()
        if count > 0:
            notificaciones.delete()
            logger.info(f"[PUBLICACION] Eliminadas {count} notificaciones de la publicación {instance.id}")

    except Exception as e:
        logger.warning(f"[PUBLICACION] Error al eliminar recursos de publicación: {e}")


@receiver(post_delete, sender=Producto)
def eliminar_recursos_producto(sender, instance, **kwargs):
    """
    Elimina los recursos asociados a un producto:
    - Imagen de S3/almacenamiento
    """
    try:
        # Eliminar imagen de S3/almacenamiento si existe
        if instance.imagen:
            try:
                from django.core.files.storage import storages
                # Obtener el nombre del archivo desde el ImageField
                imagen_path = instance.imagen.name
                if imagen_path:
                    storages["default"].delete(imagen_path)
                    logger.info(f"[PRODUCTO] Imagen eliminada de S3: {imagen_path}")
            except Exception as e:
                logger.warning(f"[PRODUCTO] Error al eliminar imagen de S3: {e}")

    except Exception as e:
        logger.warning(f"[PRODUCTO] Error al eliminar recursos del producto: {e}")
