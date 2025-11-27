"""
Context processors para notificaciones
"""
from .models import Notificacion


def notificaciones(request):
    """
    Añade información de notificaciones al contexto de todas las templates
    """
    context = {
        'notificaciones_sin_leer': 0
    }

    if request.user.is_authenticated:
        context['notificaciones_sin_leer'] = Notificacion.objects.filter(
            usuario=request.user,
            leida=False
        ).count()

    return context
