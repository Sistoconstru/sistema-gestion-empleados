from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import HistorialCargo, Empleado


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
