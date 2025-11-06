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