from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import HistorialCargo, Empleado
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
