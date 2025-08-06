from django import template
from django.utils import timezone
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def dias_hasta_limite(fecha):
    """
    Retorna el número de días hasta la fecha límite.
    Retorna None si la fecha es None.
    """
    if not fecha:
        return None
    
    now = timezone.now()
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
            
    diferencia = fecha - now
    return diferencia.days

@register.filter
def dias_desde_ahora(fecha):
    """
    Retorna el número de días desde/hasta una fecha relativa a ahora.
    Si es futuro retorna número positivo, si es pasado retorna número negativo.
    """
    if not fecha:
        return None
        
    now = timezone.now()
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    
    diferencia = fecha - now
    return diferencia.days

@register.filter
def is_fecha_vencida(fecha):
    """
    Comprueba si una fecha está vencida (es anterior a la fecha actual).
    Retorna True si la fecha es anterior a hoy, False en caso contrario.
    """
    if not fecha:
        return False
        
    now = timezone.now().date()
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return False
    elif isinstance(fecha, datetime):
        fecha = fecha.date()
        
    return fecha < now
