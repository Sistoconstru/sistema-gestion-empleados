# =============================================================================
# apps/documents/templatetags/document_filters.py - FILTROS CORREGIDOS
# =============================================================================

from django import template
from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import date, timedelta

register = template.Library()

@register.filter
def key(dictionary, key_name):
    """Acceder a un valor del diccionario por clave dinámica"""
    try:
        return dictionary[key_name]
    except (KeyError, TypeError, AttributeError):
        return None

@register.filter
def estado_color(estado):
    """Obtener color Bootstrap según estado de aprobación"""
    colors = {
        'aprobado': 'success',
        'pendiente': 'warning',
        'rechazado': 'danger'
    }
    return colors.get(estado, 'secondary')

@register.filter
def select_by_field(queryset, field_value):
    """Filtrar queryset por campo y valor - CORREGIDO"""
    try:
        if not queryset:
            return []
        
        field, value = field_value.split(',')
        field = field.strip()
        value = value.strip()
        
        # Si es un QuerySet de Django
        if hasattr(queryset, 'filter'):
            return queryset.filter(**{field: value})
        
        # Si es una lista/array
        result = []
        for item in queryset:
            if hasattr(item, field):
                if str(getattr(item, field)) == value:
                    result.append(item)
            elif hasattr(item, 'get') and callable(getattr(item, 'get')):
                if str(item.get(field)) == value:
                    result.append(item)
        
        return result
    except (ValueError, AttributeError):
        return queryset if queryset else []

@register.filter
def file_icon(filename):
    """Obtener icono FontAwesome según extensión de archivo"""
    try:
        if not filename:
            return mark_safe('<i class="fas fa-file text-secondary"></i>')
            
        extension = str(filename).lower().split('.')[-1]
        icons = {
            'pdf': 'fas fa-file-pdf text-danger',
            'jpg': 'fas fa-file-image text-primary',
            'jpeg': 'fas fa-file-image text-primary',
            'png': 'fas fa-file-image text-primary',
            'gif': 'fas fa-file-image text-primary',
            'doc': 'fas fa-file-word text-primary',
            'docx': 'fas fa-file-word text-primary',
            'xls': 'fas fa-file-excel text-success',
            'xlsx': 'fas fa-file-excel text-success',
        }
        return mark_safe(f'<i class="{icons.get(extension, "fas fa-file text-secondary")}"></i>')
    except:
        return mark_safe('<i class="fas fa-file text-secondary"></i>')

@register.filter
def file_size_human(bytes_value):
    """Convertir bytes a formato legible"""
    try:
        bytes_value = int(bytes_value)
        if bytes_value == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while bytes_value >= 1024 and i < len(size_names) - 1:
            bytes_value /= 1024.0
            i += 1
        
        return f"{bytes_value:.1f} {size_names[i]}"
    except (ValueError, TypeError):
        return "0 B"

@register.filter
def document_status_badge(documento):
    """Generar badge HTML para estado del documento"""
    try:
        if documento.estado_aprobacion == 'aprobado':
            icon = 'fas fa-check'
            color = 'success'
            text = 'Aprobado'
        elif documento.estado_aprobacion == 'pendiente':
            icon = 'fas fa-clock'
            color = 'warning'
            text = 'Pendiente'
        else:
            icon = 'fas fa-times'
            color = 'danger'
            text = 'Rechazado'
        
        return mark_safe(f'<span class="badge bg-{color}"><i class="{icon} me-1"></i>{text}</span>')
    except:
        return mark_safe('<span class="badge bg-secondary">Sin estado</span>')

@register.filter
def get_documents_by_type(documentos, tipo_codigo):
    """Obtener documentos por tipo específico"""
    try:
        if not documentos:
            return []
        
        # Si es un QuerySet
        if hasattr(documentos, 'filter'):
            return documentos.filter(tipo_documento__codigo=tipo_codigo)
        
        # Si es una lista
        result = []
        for doc in documentos:
            if hasattr(doc, 'tipo_documento') and hasattr(doc.tipo_documento, 'codigo'):
                if doc.tipo_documento.codigo == tipo_codigo:
                    result.append(doc)
        
        return result
    except:
        return []

@register.filter
def get_document_by_type(documentos, tipo_codigo):
    """Obtener primer documento por tipo específico"""
    docs = get_documents_by_type(documentos, tipo_codigo)
    return docs[0] if docs else None

@register.filter
def count_by_status(documentos, estado):
    """Contar documentos por estado"""
    try:
        if not documentos:
            return 0
        
        if hasattr(documentos, 'filter'):
            return documentos.filter(estado_aprobacion=estado).count()
        
        count = 0
        for doc in documentos:
            if hasattr(doc, 'estado_aprobacion') and doc.estado_aprobacion == estado:
                count += 1
        
        return count
    except:
        return 0

@register.filter
def is_document_expired(documento):
    """Verificar si un documento está vencido"""
    try:
        if not documento or not hasattr(documento, 'fecha_vencimiento'):
            return False
        
        if not documento.fecha_vencimiento:
            return False
        
        return documento.fecha_vencimiento < date.today()
    except:
        return False

@register.filter
def days_until_expiry(documento):
    """Días hasta el vencimiento del documento"""
    try:
        if not documento or not hasattr(documento, 'fecha_vencimiento'):
            return None
        
        if not documento.fecha_vencimiento:
            return None
        
        delta = documento.fecha_vencimiento - date.today()
        return delta.days
    except:
        return None

@register.inclusion_tag('documents/partials/document_progress_bar.html')
def document_progress_bar(empleado):
    """Mostrar barra de progreso de documentos del empleado"""
    try:
        from apps.documents.models import TipoDocumentoEmpleado, DocumentoEmpleado
        
        # Obtener documentos obligatorios
        docs_obligatorios = TipoDocumentoEmpleado.objects.filter(obligatorio=True, activo=True)
        
        # Documentos específicos del cargo
        historial_actual = empleado.historialcargo_set.filter(activo=True).first()
        docs_cargo = []
        if historial_actual:
            docs_cargo = TipoDocumentoEmpleado.objects.filter(
                tipodocumentocargo__cargo=historial_actual.cargo,
                activo=True
            )
        
        total_requeridos = docs_obligatorios.count() + docs_cargo.count()
        
        # Documentos aprobados
        tipos_requeridos = list(docs_obligatorios) + list(docs_cargo)
        docs_aprobados = DocumentoEmpleado.objects.filter(
            empleado=empleado,
            estado_aprobacion='aprobado',
            tipo_documento__in=tipos_requeridos
        ).count()
        
        if total_requeridos > 0:
            porcentaje = (docs_aprobados / total_requeridos) * 100
        else:
            porcentaje = 100
        
        return {
            'porcentaje': round(porcentaje),
            'docs_aprobados': docs_aprobados,
            'total_requeridos': total_requeridos,
            'empleado': empleado
        }
    except Exception as e:
        return {
            'porcentaje': 0,
            'docs_aprobados': 0,
            'total_requeridos': 0,
            'empleado': empleado,
            'error': str(e)
        }
