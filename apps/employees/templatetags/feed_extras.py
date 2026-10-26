"""Filtros de plantilla de la cartelera."""
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import urlize
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(needs_autoescape=True)
@stringfilter
def enlazar(texto, autoescape=True):
    """Convierte las URL del texto en enlaces que abren en otra pestaña.

    urlize escapa el resto del texto, así que no abre la puerta a HTML del
    autor. Solo se le añade target="_blank": salir de la cartelera al abrir un
    enlace obligaba a volver atrás y perder el punto del feed. noopener evita
    que la página enlazada controle esta pestaña.
    """
    html = urlize(texto, trim_url_limit=60, nofollow=True, autoescape=autoescape)
    return mark_safe(html.replace(
        ' rel="nofollow"', ' target="_blank" rel="nofollow noopener noreferrer"'
    ))
