
from django import forms
from .models import Empleado
from apps.organizational.models import Cargo

class EmpleadoForm(forms.ModelForm):
    cargo_inicial = forms.ModelChoiceField(
        queryset=Cargo.objects.filter(activo=True).select_related('area', 'rol_automatico'),
        required=True,
        label="Cargo Inicial",
        help_text="El rol se asignará automáticamente según el cargo seleccionado",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Empleado
        exclude = ('usuario', 'creado_por')
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar el label de cargo para mostrar el rol
        cargo_field = self.fields['cargo_inicial']
        cargo_choices = [('', '---------')]
        
        for cargo in cargo_field.queryset:
            if cargo.rol_automatico:
                label = f"{cargo.nombre} ({cargo.area.nombre}) → Rol: {cargo.rol_automatico.nombre}"
            else:
                label = f"{cargo.nombre} ({cargo.area.nombre}) → Sin rol asignado"
            cargo_choices.append((cargo.id, label))
        
        cargo_field.choices = cargo_choices
        
        # Personalizar otros campos
        self.fields['numero_documento'].help_text = 'Se usará como contraseña temporal del usuario'
        self.fields['nombres'].help_text = 'Se usará para generar el username del sistema'
        self.fields['correo_electronico'].help_text = 'Email del usuario en el sistema (opcional)'