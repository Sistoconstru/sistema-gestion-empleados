# =============================================================================
# apps/employees/forms.py
# =============================================================================

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, timedelta
import re

from .models import Empleado, TipoDocumento, Escolaridad, EstadoEmpleado
from apps.organizational.models import Sede, Cargo, AreaEmpresa

User = get_user_model()


class EmpleadoForm(forms.ModelForm):
    """Formulario para crear/editar empleados"""
    
    # Campos adicionales que no están en el modelo directamente
    confirmar_email = forms.EmailField(
        label="Confirmar Email",
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar email'
        })
    )
    
    cargo = forms.ModelChoiceField(
        queryset=Cargo.objects.filter(activo=True),
        label="Cargo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Empleado
        fields = [
            'tipo_documento', 'numero_documento', 'nombres', 'apellidos',
            'telefono_contacto', 'fecha_ingreso', 'sede', 'estado',
            'fecha_nacimiento', 'ciudad_nacimiento', 'escolaridad',
            'contacto_emergencia_nombre', 'contacto_emergencia_telefono',
            'correo_electronico'
        ]
        
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12345678'
            }),
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres completos'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos completos'
            }),
            'telefono_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: +57 300 123 4567'
            }),
            'fecha_ingreso': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'sede': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'ciudad_nacimiento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Medellín, Antioquia'
            }),
            'escolaridad': forms.Select(attrs={'class': 'form-control'}),
            'contacto_emergencia_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del contacto de emergencia'
            }),
            'contacto_emergencia_telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de emergencia'
            }),
            'correo_electronico': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@empresa.com'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar querysets
        self.fields['tipo_documento'].queryset = TipoDocumento.objects.filter(activo=True)
        self.fields['sede'].queryset = Sede.objects.filter(activa=True)
        self.fields['estado'].queryset = EstadoEmpleado.objects.all()
        self.fields['escolaridad'].queryset = Escolaridad.objects.all()
        
        # Si estamos editando, cargar el cargo actual
        if self.instance and self.instance.pk:
            try:
                cargo_actual = self.instance.historialcargo_set.filter(activo=True).first()
                if cargo_actual:
                    self.fields['cargo'].initial = cargo_actual.cargo
            except:
                pass

    def clean_numero_documento(self):
        """Validar número de documento"""
        numero = self.cleaned_data.get('numero_documento')
        if not numero:
            return numero
            
        # Remover espacios y caracteres especiales
        numero = re.sub(r'[^\d]', '', numero)
        
        # Validar que solo contenga números
        if not numero.isdigit():
            raise ValidationError('El número de documento solo debe contener números.')
        
        # Validar unicidad
        queryset = Empleado.objects.filter(numero_documento=numero)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError('Ya existe un empleado con este número de documento.')
        
        return numero

    def clean_telefono_contacto(self):
        """Validar formato de teléfono colombiano"""
        telefono = self.cleaned_data.get('telefono_contacto')
        if not telefono:
            return telefono
        
        # Remover espacios y caracteres especiales excepto +
        telefono_limpio = re.sub(r'[^\d+]', '', telefono)
        
        # Patrones válidos para Colombia
        patrones = [
            r'^\+57[39]\d{9}$',  # +573001234567
            r'^[39]\d{9}$',      # 3001234567
            r'^\d{7}$',          # 1234567 (fijo)
        ]
        
        if not any(re.match(patron, telefono_limpio) for patron in patrones):
            raise ValidationError(
                'Formato de teléfono inválido. Use formato colombiano: +57 300 123 4567'
            )
        
        return telefono

    def clean_fecha_nacimiento(self):
        """Validar fecha de nacimiento"""
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if not fecha:
            return fecha
        
        # Calcular edad
        today = date.today()
        edad = today.year - fecha.year - ((today.month, today.day) < (fecha.month, fecha.day))
        
        if edad < 16:
            raise ValidationError('El empleado debe ser mayor de 16 años.')
        
        return fecha

    def clean_correo_electronico(self):
        """Validar email"""
        email = self.cleaned_data.get('correo_electronico')
        
        if email:
            # Validar que no exista en otro empleado
            queryset = Empleado.objects.filter(correo_electronico=email)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError('Ya existe un empleado con este correo electrónico.')
        
        return email


class BusquedaEmpleadoForm(forms.Form):
    """Formulario para búsqueda y filtros de empleados"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, documento o email...'
        })
    )
    
    estado = forms.ModelChoiceField(
        queryset=EstadoEmpleado.objects.all(),
        required=False,
        empty_label="Todos los Estados",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    area = forms.ModelChoiceField(
        queryset=AreaEmpresa.objects.filter(activa=True),
        required=False,
        empty_label="Todas las Áreas",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    cargo = forms.ModelChoiceField(
        queryset=Cargo.objects.filter(activo=True),
        required=False,
        empty_label="Todos los Cargos",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    sede = forms.ModelChoiceField(
        queryset=Sede.objects.filter(activa=True),
        required=False,
        empty_label="Todas las Sedes",
        widget=forms.Select(attrs={'class': 'form-control'})
    )