# =============================================================================
# apps/documents/utils.py - UTILIDADES PARA DOCUMENTOS
# =============================================================================

import os
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image
import magic

def validate_file_extension(file, allowed_extensions):
    """Validar extensión de archivo"""
    ext = os.path.splitext(file.name)[1].lower()
    valid_extensions = [f'.{ext.lower()}' for ext in allowed_extensions.split(',')]
    
    if ext not in valid_extensions:
        raise ValidationError(
            f'Extensión no permitida. Formatos válidos: {", ".join(valid_extensions)}'
        )

def validate_file_size(file, max_size_mb):
    """Validar tamaño de archivo"""
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            f'El archivo es muy grande. Tamaño máximo: {max_size_mb}MB'
        )

def validate_file_content(file):
    """Validar que el contenido del archivo coincida con la extensión"""
    try:
        # Validar tipo MIME
        file_mime = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)  # Resetear puntero
        
        # Tipos MIME permitidos
        allowed_mimes = {
            'application/pdf': ['.pdf'],
            'image/jpeg': ['.jpg', '.jpeg'],
            'image/png': ['.png'],
            'image/gif': ['.gif']
        }
        
        ext = os.path.splitext(file.name)[1].lower()
        
        # Verificar coincidencia
        if file_mime in allowed_mimes:
            if ext not in allowed_mimes[file_mime]:
                raise ValidationError(
                    f'El contenido del archivo no coincide con la extensión {ext}'
                )
        else:
            raise ValidationError(f'Tipo de archivo no permitido: {file_mime}')
            
    except Exception as e:
        raise ValidationError(f'Error validando archivo: {str(e)}')

def get_upload_path(instance, filename):
    """Generar ruta de subida personalizada"""
    empleado_doc = instance.empleado.numero_documento
    tipo_doc = instance.tipo_documento.codigo
    
    # Crear estructura: documentos/empleado_123456/CEDULA/archivo.pdf
    return f'documentos/{empleado_doc}/{tipo_doc}/{filename}'

def compress_image(image_path, quality=85):
    """Comprimir imagen para reducir tamaño"""
    try:
        with Image.open(image_path) as img:
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionar si es muy grande
            if img.width > 1920 or img.height > 1920:
                img.thumbnail((1920, 1920), Image.Resampling.LANCZOS)
            
            # Guardar con compresión
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            
    except Exception as e:
        raise ValidationError(f'Error comprimiendo imagen: {str(e)}')
