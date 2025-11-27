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
            # Contar mensajes sin leer donde:
            # 1. El usuario es participante de la conversación
            # 2. No es el remitente del mensaje
            # 3. El mensaje no ha sido leído (leido=False)
            mensajes_count = Mensaje.objects.filter(
                conversacion__participantes=empleado,
                leido=False
            ).exclude(
                remitente=empleado
            ).distinct().count()

            context['mensajes_sin_leer'] = mensajes_count

        except Exception as e:
            # Si el usuario no tiene perfil de empleado, registrar el error
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Error en context processor mensajes_sin_leer: {str(e)}")
            pass

    return context
