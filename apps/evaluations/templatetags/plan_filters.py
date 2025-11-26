# =============================================================================
# apps/evaluations/templatetags/plan_filters.py
# Filtros personalizados para procesar el contenido del plan de mejora
# =============================================================================

from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def format_plan_with_checkboxes(plan_content):
    """
    Convierte el contenido del plan de mejora en HTML con checkboxes
    para cada elemento del plan (solo para puntajes 1 y 2)
    """
    if not plan_content:
        return ""
    
    # Separar por líneas y limpiar
    lines = [line.strip() for line in plan_content.split('\n') if line.strip()]
    html_content = []
    in_plan_section = False
    plan_item_counter = 1
    current_section = None
    requiere_seguimiento = False
    categoria_actual = ""
    
    for line in lines:
        # Detectar títulos de categorías (números seguidos de punto y nombre)
        if re.match(r'^\d+\.\s+[^:]+:\s*⭐', line):
            # Cerrar sección anterior si existe
            if current_section:
                if in_plan_section:
                    html_content.append('</div>')  # Cerrar plan-items
                    html_content.append('</div>')  # Cerrar plan-section
                html_content.append('</div>')  # Cerrar categoria-section
                
            # Determinar si esta categoría requiere seguimiento basado en la calificación
            requiere_seguimiento = "Calificación 1" in line or "Calificación 2" in line
            categoria_actual = line
                
            html_content.append('<div class="categoria-section mb-4">')
            html_content.append(f'<h6 class="text-primary mb-3">{line}</h6>')
            in_plan_section = False
            current_section = 'categoria'
            
        # Detectar sección "Recomendación:"
        elif line.startswith("Recomendación:"):
            html_content.append('<div class="recomendacion-section mb-3">')
            html_content.append('<h6 class="text-success mb-2"><i class="fas fa-lightbulb me-2"></i>Recomendación:</h6>')
            current_section = 'recomendacion'
            
        # Detectar sección "Plan de mejora:"
        elif line.startswith("Plan de mejora:"):
            if current_section == 'recomendacion':
                html_content.append('</div>')  # Cerrar recomendación
            html_content.append('<div class="plan-section mb-3">')
            html_content.append('<h6 class="text-warning mb-3"><i class="fas fa-tasks me-2"></i>Plan de mejora:</h6>')
            html_content.append('<div class="plan-items">')
            in_plan_section = True
            current_section = 'plan'
        
        # Detectar marcador de seguimiento
        elif line.startswith("REQUIERE_SEGUIMIENTO"):
            continue  # Saltar esta línea, no mostrarla
            
        # Detectar "Observaciones del evaluador:"
        elif line.startswith("Observaciones"):
            # Cerrar secciones anteriores
            if in_plan_section:
                html_content.append('</div>')  # Cerrar plan-items
                html_content.append('</div>')  # Cerrar plan-section
                in_plan_section = False
            if current_section == 'categoria':
                html_content.append('</div>')  # Cerrar categoria-section
                
            html_content.append('<div class="observaciones-section mt-4">')
            html_content.append('<h6 class="text-info mb-3"><i class="fas fa-comment-alt me-2"></i>Observaciones del evaluador:</h6>')
            html_content.append('<div class="alert alert-light border-info">')
            html_content.append('<p class="text-muted mb-0">[Campo opcional para comentarios adicionales del evaluador]</p>')
            html_content.append('</div>')
            html_content.append('</div>')
            current_section = 'observaciones'
            
        # Líneas de contenido
        else:
            if current_section == 'recomendacion' and line:
                html_content.append(f'<p class="mb-2">{line}</p>')
                
            elif current_section == 'plan' and line and line.endswith('.'):
                # Elementos del plan de mejora
                if requiere_seguimiento:
                    # Con checkbox para seguimiento (puntajes 1 y 2)
                    html_content.append('<div class="form-check mb-2 plan-item">')
                    html_content.append(f'<input class="form-check-input plan-checkbox" type="checkbox" id="plan_item_{plan_item_counter}">')
                    html_content.append(f'<label class="form-check-label" for="plan_item_{plan_item_counter}">{line}</label>')
                    html_content.append('</div>')
                    plan_item_counter += 1
                else:
                    # Sin checkbox (puntaje 3 - mantener nivel)
                    html_content.append(f'<div class="plan-item-info mb-2"><i class="fas fa-star text-warning me-2"></i>{line}</div>')
    
    # Cerrar divs pendientes
    if in_plan_section:
        html_content.append('</div>')  # Cerrar plan-items
        html_content.append('</div>')  # Cerrar plan-section
    if current_section in ['categoria', 'recomendacion']:
        html_content.append('</div>')  # Cerrar categoria-section o recomendacion-section
    
    return mark_safe(''.join(html_content))

@register.filter
def progress_percentage(seguimientos):
    """
    Calcula el porcentaje de progreso basado en seguimientos completados
    """
    if not seguimientos:
        return 0
    
    completados = sum(1 for s in seguimientos if s.estado == 'completado')
    total = len(seguimientos)
    return round((completados / total) * 100) if total > 0 else 0