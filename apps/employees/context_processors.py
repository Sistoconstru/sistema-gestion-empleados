"""
Context processors para empleados y marketplace
"""
from django.db.models import Q
from .models import Mensaje, Conversacion


def mensajes_sin_leer(request):
    """
    Añade información de mensajes sin leer al contexto de todas las templates
    """
    context = {
        'mensajes_sin_leer': 0
    }

    if request.user.is_authenticated:
        try:
            empleado = request.user.empleado
            # Contar mensajes sin leer donde el usuario es participante
            # y no es el remitente
            mensajes_count = Mensaje.objects.filter(
                conversacion__participantes=empleado,
                leido=False
            ).exclude(
                remitente=empleado
            ).count()
            context['mensajes_sin_leer'] = mensajes_count
        except Exception:
            # Si el usuario no tiene perfil de empleado, pasar
            pass

    return context
