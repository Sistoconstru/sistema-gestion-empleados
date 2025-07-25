# =============================================================================
# apps/documents/validators.py - VALIDADORES PERSONALIZADOS
# =============================================================================

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .utils import validate_file_extension, validate_file_size, validate_file_content

class DocumentValidator:
    """Validador completo para documentos de empleados"""
    
    def __init__(self, tipo_documento):
        self.tipo_documento = tipo_documento
    
    def __call__(self, file):
        """Ejecutar todas las validaciones"""
        # Validar extensión
        validate_file_extension(file, self.tipo_documento.formatos_permitidos)
        
        # Validar tamaño
        validate_file_size(file, self.tipo_documento.tamaño_maximo_mb)
        
        # Validar contenido
        validate_file_content(file)
        
        return file

def validate_cedula_document(file):
    """Validador específico para cédula"""
    # Validaciones específicas para cédula
    allowed_extensions = ['PDF', 'JPG', 'PNG']
    max_size = 5  # MB
    
    validate_file_extension(file, ','.join(allowed_extensions))
    validate_file_size(file, max_size)
    validate_file_content(file)
    
    return file

def validate_certificate_document(file):
    """Validador específico para certificados"""
    # Solo PDF para certificados
    validate_file_extension(file, 'PDF')
    validate_file_size(file, 5)
    validate_file_content(file)
    
    return file