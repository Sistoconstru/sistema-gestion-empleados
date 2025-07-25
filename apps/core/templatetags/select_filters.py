from django import template

register = template.Library()

def select(queryset, field, value=None):
    """
    Filtro personalizado para filtrar un queryset/lista por campo y valor.
    Uso: {{ lista|select:"campo,valor" }}
    Si solo se pasa campo, filtra por campo True/No vacío.
    """
    if not queryset:
        return []
    args = field.split(',')
    campo = args[0]
    valor = args[1] if len(args) > 1 else None
    resultado = []
    for obj in queryset:
        # Permite acceso a campos anidados tipo 'tipo_documento__codigo'
        partes = campo.split('__')
        dato = obj
        try:
            for parte in partes:
                dato = getattr(dato, parte)
        except Exception:
            dato = None
        if valor is not None:
            if str(dato).lower() == str(valor).lower():
                resultado.append(obj)
        else:
            if dato:
                resultado.append(obj)
    return resultado

register.filter('select', select)
