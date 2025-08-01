# apps/training/forms.py

from django import forms
from .models import Capacitacion, InscripcionCapacitacion, TipoCapacitacion
from apps.organizational.models import Cargo

class CapacitacionForm(forms.ModelForm):
    """Formulario para crear/editar capacitaciones"""
    cargos = forms.ModelMultipleChoiceField(
        queryset=Cargo.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Selecciona los cargos que requieren esta capacitación (solo para obligatorias)"
    )
    
    class Meta:
        model = Capacitacion
        fields = [
            'codigo', 'nombre', 'descripcion', 'tipo', 'duracion_estimada_horas',
            'puntaje_aprobacion', 'intentos_maximos', 'fecha_vigencia_inicio',
            'fecha_vigencia_fin', 'version', 'proveedor_externo', 
            'url_inscripcion_externa', 'requiere_certificado_externo',
            'nivel_dificultad', 'costo_inscripcion', 'puntos_gamificacion'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'duracion_estimada_horas': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_vigencia_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_vigencia_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proveedor_externo': forms.TextInput(attrs={'class': 'form-control'}),
            'url_inscripcion_externa': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Mostrar campos específicos según el tipo
        tipo_field = self.fields['tipo']
        tipo_field.widget.attrs['onchange'] = 'toggleExternalFields(this.value)'
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        
        # Validación para capacitaciones externas
        if tipo and tipo.codigo == 'EXTERNA_LIBRE':
            if not cleaned_data.get('proveedor_externo'):
                raise forms.ValidationError({
                    'proveedor_externo': 'Requerido para capacitaciones externas'
                })
            if not cleaned_data.get('url_inscripcion_externa'):
                raise forms.ValidationError({
                    'url_inscripcion_externa': 'Requerido para capacitaciones externas'
                })
        
        return cleaned_data
