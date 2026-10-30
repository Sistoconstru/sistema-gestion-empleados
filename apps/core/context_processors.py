from datetime import date
from apps.notifications.models import Notificacion


def notifications_context(request):
    """Agregar notificaciones al contexto global"""
    if request.user.is_authenticated:
        notificaciones_count = Notificacion.objects.filter(
            usuario=request.user,
            leida=False
        ).count()
        
        return {
            'notificaciones_count': notificaciones_count
        }
    
    return {}


def user_context(request):
    """Agregar información del usuario al contexto"""
    if request.user.is_authenticated:
        context = {
            'user_full_name': request.user.get_full_name() or request.user.username
        }

        # Agregar información del empleado si existe
        if hasattr(request.user, 'empleado'):
            empleado = request.user.empleado
            context.update({
                'empleado_actual': empleado,
                'cargo_actual': empleado.historialcargo_set.filter(activo=True).first()
            })

        return context

    return {}


def surveys_context(request):
    """Agregar conteo de encuestas pendientes al contexto global"""
    if request.user.is_authenticated:
        try:
            from apps.surveys.avisos import encuestas_pendientes_de

            # Verificar si el usuario tiene un empleado asociado
            if hasattr(request.user, 'empleado'):
                pendientes = encuestas_pendientes_de(request.user.empleado)
                return {
                    'encuestas_pendientes_nav': len(pendientes),
                    # Para la ventana "Tienes encuestas pendientes" de base.html.
                    'encuestas_pendientes_lista': pendientes[:3],
                }
        except ImportError:
            # Si el módulo de encuestas no está disponible, devolver 0
            pass
        except Exception:
            # En caso de cualquier otro error, devolver 0
            pass

    return {'encuestas_pendientes_nav': 0}