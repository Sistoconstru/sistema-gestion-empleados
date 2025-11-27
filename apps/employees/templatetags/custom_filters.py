from django import template

register = template.Library()


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
