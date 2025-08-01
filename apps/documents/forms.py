# =============================================================================
# apps/documents/forms.py - FORMULARIOS PARA DOCUMENTOS
# =============================================================================

from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from .models import DocumentoEmpleado, TipoDocumentoEmpleado
from .validators import DocumentValidator
from .utils import validate_file_extension, validate_file_size

# Formulario para subir documentos individuales
class DocumentoEmpleadoForm(forms.ModelForm):
    """Formulario para subir documentos individuales"""
    
    class Meta:
        model = DocumentoEmpleado
        fields = ['tipo_documento', 'archivo', 'fecha_documento', 'fecha_vencimiento', 'observaciones']
        widgets = {
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
                'required': True
            }),
            'fecha_documento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales (opcional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        # Recibe empleado y usuario para filtrar tipos de documento y registrar quién sube el archivo
        self.empleado = kwargs.pop('empleado', None)
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar tipos de documento disponibles para el empleado
        if self.empleado:
            tipos_disponibles = self.get_available_document_types()
            # Si es lista, convertir a queryset
            if isinstance(tipos_disponibles, list):
                ids = [td.id for td in tipos_disponibles]
                self.fields['tipo_documento'].queryset = TipoDocumentoEmpleado.objects.filter(id__in=ids)
            else:
                self.fields['tipo_documento'].queryset = tipos_disponibles
        
        # Configurar campos obligatorios dinámicamente
        # Ocultar campo fecha_vencimiento si el tipo de documento no requiere vencimiento
        if self.instance and hasattr(self.instance, 'tipo_documento') and self.instance.tipo_documento:
            if hasattr(self.instance.tipo_documento, 'tiene_vencimiento') and self.instance.tipo_documento.tiene_vencimiento:
                self.fields['fecha_vencimiento'].required = True
            else:
                self.fields['fecha_vencimiento'].widget = forms.HiddenInput()
    
    def get_available_document_types(self):
        """Obtener tipos de documentos disponibles para el empleado"""
        # Documentos obligatorios para todos
        obligatorios = TipoDocumentoEmpleado.objects.filter(obligatorio=True, activo=True)
        # Documentos opcionales
        opcionales = TipoDocumentoEmpleado.objects.filter(obligatorio=False, activo=True)
        # Documentos específicos del cargo actual
        cargo_actual = None
        historial_actual = self.empleado.historialcargo_set.filter(activo=True).first()
        if historial_actual:
            cargo_actual = historial_actual.cargo
        tipos_disponibles = list(obligatorios) + list(opcionales)
        if cargo_actual:
            especificos = list(TipoDocumentoEmpleado.objects.filter(
                tipodocumentocargo__cargo=cargo_actual,
                activo=True
            ))
            tipos_disponibles += especificos
        # Excluir documentos ya subidos
        docs_existentes = set(DocumentoEmpleado.objects.filter(empleado=self.empleado).values_list('tipo_documento', flat=True))
        tipos_disponibles = [td for td in tipos_disponibles if td.id not in docs_existentes]
        return tipos_disponibles
    
    def get_available_document_types(self):
        """Obtener tipos de documentos disponibles según el usuario (admin/empleado)"""
        # Si el usuario es admin (is_staff), mostrar todos los tipos activos excluyendo los ya subidos
        if self.usuario and getattr(self.usuario, 'is_staff', False):
            tipos = TipoDocumentoEmpleado.objects.filter(activo=True)
            docs_existentes = set(DocumentoEmpleado.objects.filter(empleado=self.empleado).values_list('tipo_documento', flat=True))
            tipos = tipos.exclude(pk__in=docs_existentes)
            return tipos
        # Si es empleado, mostrar solo los no obligatorios y los de su cargo
        tipos_no_obligatorios = TipoDocumentoEmpleado.objects.filter(obligatorio=False, activo=True)
        tipos_cargo = TipoDocumentoEmpleado.objects.none()
        cargo_actual = None
        historial_actual = self.empleado.historialcargo_set.filter(activo=True).first()
        if historial_actual:
            cargo_actual = historial_actual.cargo
            tipos_cargo_ids = cargo_actual and cargo_actual.tipodocumentocargo_set.values_list('tipo_documento', flat=True)
            if tipos_cargo_ids:
                tipos_cargo = TipoDocumentoEmpleado.objects.filter(pk__in=tipos_cargo_ids, activo=True)
        tipos_final = tipos_no_obligatorios | tipos_cargo
        docs_existentes = set(DocumentoEmpleado.objects.filter(empleado=self.empleado).values_list('tipo_documento', flat=True))
        tipos_final = tipos_final.exclude(pk__in=docs_existentes)
        return tipos_final.distinct()
    
    def clean_archivo(self):
        """Validar archivo subido"""
        archivo = self.cleaned_data.get('archivo')
        tipo_documento = self.cleaned_data.get('tipo_documento')
        
        if archivo and tipo_documento:
            # Aplicar validador específico del tipo de documento
            validator = DocumentValidator(tipo_documento)
            try:
                validator(archivo)
            except ValidationError as e:
                raise forms.ValidationError(str(e))
        
        return archivo
    
    def clean(self):
        """Validaciones cruzadas"""
        cleaned_data = super().clean()
        tipo_documento = cleaned_data.get('tipo_documento')
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')
        fecha_documento = cleaned_data.get('fecha_documento')
        
        # Validar fecha de vencimiento para documentos que la requieren
        if tipo_documento and tipo_documento.tiene_vencimiento and not fecha_vencimiento:
            raise forms.ValidationError({
                'fecha_vencimiento': 'Este tipo de documento requiere fecha de vencimiento'
            })
        
        # Validar que fecha de vencimiento sea posterior a fecha del documento
        if fecha_documento and fecha_vencimiento and fecha_vencimiento <= fecha_documento:
            raise forms.ValidationError({
                'fecha_vencimiento': 'La fecha de vencimiento debe ser posterior a la fecha del documento'
            })
        
        return cleaned_data
    
    def save(self, commit=True):
        """Guardar documento con información adicional y validación de tipo_documento"""
        documento = super().save(commit=False)
        if self.empleado:
            documento.empleado = self.empleado
        if self.usuario:
            documento.cargado_por = self.usuario
        # Generar nombre de archivo automático solo si tipo_documento existe y no lanza excepción
        try:
            if documento.archivo and documento.tipo_documento:
                ext = documento.archivo.name.split('.')[-1]
                documento.nombre_archivo = f"{documento.tipo_documento.codigo}_{documento.empleado.numero_documento}.{ext}"
            else:
                documento.nombre_archivo = documento.archivo.name if documento.archivo else ''
        except Exception:
            documento.nombre_archivo = documento.archivo.name if documento.archivo else ''
        if commit:
            documento.save()
        return documento

# Formulario para subir múltiples documentos a la vez
class MultipleDocumentUploadForm(forms.Form):
    """Formulario para subir múltiples documentos a la vez"""
    
    def __init__(self, *args, **kwargs):
        self.empleado = kwargs.pop('empleado', None)
        super().__init__(*args, **kwargs)
        
        if self.empleado:
            # Crear campos dinámicos para cada tipo de documento disponible
            available_types = self.get_available_document_types()
            
            for tipo_doc in available_types:
                field_name = f'documento_{tipo_doc.codigo}'
                
                self.fields[field_name] = forms.FileField(
                    label=tipo_doc.nombre,
                    required=tipo_doc.obligatorio,
                    help_text=f"{tipo_doc.descripcion}. Formatos: {tipo_doc.formatos_permitidos}. Máx: {tipo_doc.tamaño_maximo_mb}MB",
                    widget=forms.FileInput(attrs={
                        'class': 'form-control',
                        'accept': self.get_accept_string(tipo_doc.formatos_permitidos),
                        'data-tipo-doc': tipo_doc.codigo
                    })
                )
                
                # Campo de fecha de vencimiento si es necesario
                if tipo_doc.tiene_vencimiento:
                    venc_field_name = f'vencimiento_{tipo_doc.codigo}'
                    self.fields[venc_field_name] = forms.DateField(
                        label=f'Vencimiento {tipo_doc.nombre}',
                        required=True,
                        widget=forms.DateInput(attrs={
                            'type': 'date',
                            'class': 'form-control'
                        })
                    )
    
    def get_available_document_types(self):
        """Obtener tipos de documentos disponibles"""
        if not self.empleado:
            return TipoDocumentoEmpleado.objects.none()
        
        # Lógica similar al form individual
        obligatorios = TipoDocumentoEmpleado.objects.filter(obligatorio=True, activo=True)
        opcionales = TipoDocumentoEmpleado.objects.filter(obligatorio=False, activo=True)
        
        tipos_disponibles = list(obligatorios) + list(opcionales)
        # Excluir ya existentes
        docs_existentes = set(DocumentoEmpleado.objects.filter(empleado=self.empleado).values_list('tipo_documento', flat=True))
        tipos_disponibles = [td for td in tipos_disponibles if td.id not in docs_existentes]
        return tipos_disponibles
    
    def get_accept_string(self, formatos):
        """Convertir formatos a string accept de HTML"""
        format_map = {
            'PDF': '.pdf',
            'JPG': '.jpg,.jpeg', 
            'PNG': '.png',
            'GIF': '.gif'
        }
        
        accepts = []
        for formato in formatos.split(','):
            formato = formato.strip().upper()
            if formato in format_map:
                accepts.append(format_map[formato])
        
        return ','.join(accepts)

# Formulario para aprobar/rechazar documentos
class DocumentApprovalForm(forms.ModelForm):
    """Formulario para aprobar/rechazar documentos"""
    
    class Meta:
        model = DocumentoEmpleado
        fields = ['estado_aprobacion', 'observaciones']
        widgets = {
            'estado_aprobacion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escriba las observaciones o motivo de rechazo...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar solo estados relevantes para aprobación
        self.fields['estado_aprobacion'].choices = [
            ('aprobado', 'Aprobado'),
            ('rechazado', 'Rechazado')
        ]
