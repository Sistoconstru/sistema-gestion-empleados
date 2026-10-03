"""Filtros de template del módulo beneficios de retención."""
from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter(name='pesos')
def pesos(value):
    """Formatea un número como pesos colombianos: `$12.480.000`.

    Separador de miles con punto (estilo COP). Devuelve '—' si no se puede.
    """
    if value is None or value == '':
        return '—'
    try:
        n = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return '—'
    entero = int(n)
    # Formato: separador de miles con coma, luego cambio coma por punto.
    return f'${entero:,}'.replace(',', '.')
