
from django import template
register = template.Library()

# Filtro para verificar si un módulo está completado para una inscripción
@register.filter(name='modulo_completado')
def modulo_completado(modulo, inscripcion):
    return modulo.esta_completado(inscripcion)

# Filtro para verificar si una lección está completada para una inscripción
@register.filter(name='leccion_completada')
def leccion_completada(leccion, inscripcion):
    return leccion.esta_completada(inscripcion)

@register.filter
def get_item(dictionary, key):
    """Obtiene un elemento de un diccionario usando una clave"""
    if dictionary is None:
        return None
    # Verificar que sea un diccionario antes de usar .get()
    if not isinstance(dictionary, dict):
        return None
    return dictionary.get(key)


# Filtro para dividir por 60 y mostrar minutos
@register.filter(name='minutos')
def minutos(valor):
    try:
        return int(round(float(valor) / 60))
    except (ValueError, TypeError):
        return 0

# Filtro para verificar si un string contiene otro string
@register.filter(name='contains')
def contains(value, arg):
    """Devuelve True si 'arg' está en 'value' (ambos string)."""
    if not value:
        return False
    return arg in value
