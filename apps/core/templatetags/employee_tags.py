# =============================================================================
# apps/core/templatetags/employee_tags.py
# =============================================================================

from django import template
from django.utils import timezone
from datetime import date, datetime
import locale

register = template.Library()

@register.filter
def age(birth_date):
    """Calcular edad a partir de fecha de nacimiento"""
    if not birth_date:
        return 0
    
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

@register.filter  
def initials(full_name):
    """Obtener iniciales de un nombre completo"""
    if not full_name:
        return 'NN'
    
    names = full_name.strip().split()
    if len(names) >= 2:
        return f"{names[0][0]}{names[-1][0]}".upper()
    elif len(names) == 1:
        return names[0][:2].upper()
    return 'NN'

@register.filter
def format_phone(phone_number):
    """Formatear número de teléfono"""
    if not phone_number:
        return ''
    
    # Limpiar el número
    clean_number = ''.join(filter(str.isdigit, str(phone_number)))
    
    # Formatear según longitud
    if len(clean_number) == 10:
        return f"{clean_number[:3]} {clean_number[3:6]} {clean_number[6:]}"
    elif len(clean_number) == 7:
        return f"{clean_number[:3]} {clean_number[3:]}"
    else:
        return phone_number

@register.filter
def format_document(document_type, document_number):
    """Formatear documento de identidad"""
    if not document_number:
        return ''
    
    if hasattr(document_type, 'codigo'):
        type_code = document_type.codigo
    else:
        type_code = str(document_type)
    
    return f"{type_code} {document_number}"

@register.filter
def days_until(target_date):
    """Calcular días hasta una fecha"""
    if not target_date:
        return None
    
    if isinstance(target_date, datetime):
        target_date = target_date.date()
    
    today = date.today()
    delta = target_date - today
    
    return delta.days

@register.filter
def status_class(status):
    """Obtener clase CSS para estados"""
    if not status:
        return 'secondary'
    
    status_lower = str(status).lower()
    
    if 'activo' in status_lower:
        return 'success'
    elif 'prueba' in status_lower or 'pendiente' in status_lower:
        return 'warning'
    elif 'inactivo' in status_lower or 'vencido' in status_lower:
        return 'danger'
    elif 'completado' in status_lower or 'aprobado' in status_lower:
        return 'success'
    else:
        return 'secondary'

@register.filter
def status_icon(status):
    """Obtener icono para estados"""
    if not status:
        return 'fas fa-circle'
    
    status_lower = str(status).lower()
    
    if 'activo' in status_lower:
        return 'fas fa-check-circle'
    elif 'prueba' in status_lower:
        return 'fas fa-clock'
    elif 'inactivo' in status_lower:
        return 'fas fa-times-circle'
    elif 'pendiente' in status_lower:
        return 'fas fa-hourglass-half'
    elif 'completado' in status_lower:
        return 'fas fa-check-circle'
    else:
        return 'fas fa-circle'

@register.filter
def truncate_smart(text, length=50):
    """Truncar texto inteligentemente"""
    if not text:
        return ''
    
    if len(text) <= length:
        return text
    
    # Buscar último espacio antes del límite
    truncated = text[:length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return f"{truncated}..."

@register.filter
def time_until_spanish(target_date):
    """Tiempo hasta una fecha en español"""
    if not target_date:
        return ''
    
    if isinstance(target_date, datetime):
        target_date = target_date.date()
    
    today = date.today()
    delta = target_date - today
    days = delta.days
    
    if days < 0:
        days = abs(days)
        if days == 1:
            return 'Venció ayer'
        elif days < 7:
            return f'Venció hace {days} días'
        elif days < 30:
            weeks = days // 7
            return f'Venció hace {weeks} semana{"s" if weeks > 1 else ""}'
        else:
            months = days // 30
            return f'Venció hace {months} mes{"es" if months > 1 else ""}'
    elif days == 0:
        return 'Vence hoy'
    elif days == 1:
        return 'Vence mañana'
    elif days < 7:
        return f'Vence en {days} días'
    elif days < 30:
        weeks = days // 7
        return f'Vence en {weeks} semana{"s" if weeks > 1 else ""}'
    else:
        months = days // 30
        return f'Vence en {months} mes{"es" if months > 1 else ""}'

@register.simple_tag
def get_cargo_actual(empleado):
    """Obtener cargo actual de un empleado"""
    try:
        historial = empleado.historialcargo_set.filter(activo=True).first()
        return historial.cargo if historial else None
    except:
        return None

@register.simple_tag
def get_area_actual(empleado):
    """Obtener área actual de un empleado"""
    try:
        historial = empleado.historialcargo_set.filter(activo=True).first()
        return historial.cargo.area if historial else None
    except:
        return None

@register.inclusion_tag('core/tags/employee_card.html')
def employee_card(empleado, show_details=True):
    """Renderizar tarjeta de empleado"""
    cargo_actual = None
    try:
        historial = empleado.historialcargo_set.filter(activo=True).first()
        cargo_actual = historial.cargo if historial else None
    except:
        pass
    
    return {
        'empleado': empleado,
        'cargo_actual': cargo_actual,
        'show_details': show_details,
    }

@register.inclusion_tag('core/tags/status_badge.html')
def status_badge(status, size='normal'):
    """Renderizar badge de estado"""
    return {
        'status': status,
        'css_class': status_class(status),
        'icon': status_icon(status),
        'size': size,
    }

@register.inclusion_tag('core/tags/progress_bar.html')
def progress_bar(current, total, show_percentage=True, color='primary'):
    """Renderizar barra de progreso"""
    if total == 0:
        percentage = 0
    else:
        percentage = round((current / total) * 100, 1)
    
    return {
        'current': current,
        'total': total,
        'percentage': percentage,
        'show_percentage': show_percentage,
        'color': color,
    }

@register.filter
def percentage(value, total):
    """Calcular porcentaje"""
    if not total or total == 0:
        return 0
    return round((value / total) * 100, 1)

@register.filter
def dict_get(dictionary, key):
    """Obtener valor de diccionario por clave"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.simple_tag
def url_replace(request, field, value):
    """Reemplazar parámetro en URL manteniendo otros"""
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()

@register.filter
def multiply(value, factor):
    """Multiplicar valor por factor"""
    try:
        return float(value) * float(factor)
    except (ValueError, TypeError):
        return 0


@register.filter
def format_price(value):
    """
    Formatea un número para mostrar como precio en pesos colombianos.
    Añade separadores de miles usando puntos.

    Ejemplo: 1500000 -> 1.500.000
    """
    try:
        # Convertir a entero para eliminar decimales
        value = int(float(value))
        # Formatear como string con separadores de miles
        return f"{value:,}".replace(",", ".")
    except (ValueError, TypeError):
        return value


@register.filter
def total_venta(venta):
    """
    Calcula el total pagado en una venta considerando la cantidad solicitada.

    Args:
        venta: Objeto Venta del marketplace

    Returns:
        Total pagado (precio_final * cantidad_solicitada)
    """
    try:
        cantidad = 1
        if hasattr(venta, 'reserva_origen') and venta.reserva_origen:
            cantidad = venta.reserva_origen.cantidad_solicitada
        return venta.precio_final * cantidad
    except (AttributeError, TypeError, ValueError):
        return venta.precio_final if hasattr(venta, 'precio_final') else 0


@register.filter
def cantidad_venta(venta):
    """
    Obtiene la cantidad de unidades en una venta.

    Args:
        venta: Objeto Venta del marketplace

    Returns:
        Cantidad de unidades compradas
    """
    try:
        if hasattr(venta, 'reserva_origen') and venta.reserva_origen:
            return venta.reserva_origen.cantidad_solicitada
        return 1
    except (AttributeError, TypeError):
        return 1