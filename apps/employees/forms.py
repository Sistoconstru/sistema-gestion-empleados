# =============================================================================
# apps/employees/forms.py - FORMULARIOS CORREGIDOS
# =============================================================================

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, timedelta
import re
import logging

from .models import Empleado, TipoDocumento, Escolaridad, EstadoEmpleado, HistorialCargo
from apps.organizational.models import Sede, Cargo, AreaEmpresa

User = get_user_model()
logger = logging.getLogger(__name__)


class EmpleadoForm(forms.ModelForm):
    """Formulario para crear/editar empleados"""
    
    # Campo adicional para confirmar email
    confirmar_email = forms.EmailField(
        label="Confirmar Email",
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar email'
        }),
        help_text="Debe coincidir con el email principal"
    )
    
    # Campo para cargo (no está en el modelo directamente)
    cargo = forms.ModelChoiceField(
        queryset=Cargo.objects.filter(activo=True),
        label="Cargo",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_cargo'}),
        help_text="Cargo que ocupará el empleado"
    )

    # Campo para jefe directo (se muestra dinámicamente según el cargo seleccionado)
    jefe_directo = forms.ModelChoiceField(
        queryset=Empleado.objects.none(),
        label="Jefe Directo",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_jefe_directo'}),
        help_text="Seleccione el jefe directo del empleado (si hay más de un posible jefe)"
    )
    
    departamento = forms.ModelChoiceField(
        queryset=None,
        label="Departamento",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Seleccione departamento'}),
        help_text="Filtra las ciudades por departamento"
    )
    direccion = forms.CharField(
        label="Dirección de residencia",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ejemplo: Calle 93 # 15-20, Barrio, Ciudad',
        }),
        help_text="Debe iniciar con el tipo de vía completo (Calle, Carrera, Avenida, Vereda, etc.)"
    )

    class Meta:
        model = Empleado
        fields = [
            'tipo_documento', 'numero_documento', 'nombres', 'apellidos',
            'telefono_contacto', 'fecha_ingreso', 'sede', 'cargo',
            'fecha_nacimiento', 'departamento', 'ciudad_nacimiento', 'escolaridad',
            'contacto_emergencia_nombre', 'contacto_emergencia_telefono',
            'correo_electronico',
            'direccion',
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12345678',
                'required': True,
                'pattern': '[0-9]+',
                'title': 'Solo números'
            }),
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres completos',
                'required': True
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos completos',
                'required': True
            }),
            'telefono_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: +57 300 123 4567',
                'required': True
            }),
            'fecha_ingreso': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True,
                'data-date-format': 'YYYY-MM-DD'
            }),
            'sede': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'data-date-format': 'YYYY-MM-DD'
            }),
            'ciudad_nacimiento': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Seleccione ciudad de nacimiento'
            }),
            'escolaridad': forms.Select(attrs={
                'class': 'form-control'
            }),
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
        # Obtener cargo_id de kwargs si viene de POST
        cargo_id = kwargs.pop('cargo_id', None)
        super().__init__(*args, **kwargs)
        from apps.employees.models import Departamento, Ciudad
        # Configurar queryset de departamento
        self.fields['departamento'].queryset = Departamento.objects.all().order_by('nombre')
        # Configurar querysets para campos relacionados
        try:
            self.fields['tipo_documento'].queryset = TipoDocumento.objects.filter(activo=True)
            self.fields['sede'].queryset = Sede.objects.filter(activa=True)
            self.fields['escolaridad'].queryset = Escolaridad.objects.all()
            self.fields['cargo'].queryset = Cargo.objects.filter(activo=True).select_related('area', 'cargo_jefe')
            self.fields['ciudad_nacimiento'].queryset = Ciudad.objects.all().order_by('nombre')
        except Exception as e:
            logger.error(f"Error configurando querysets en formulario: {e}")

        # Si estamos editando, cargar el cargo actual y jefe directo
        if self.instance and self.instance.pk:
            try:
                cargo_actual = self.instance.historialcargo_set.filter(activo=True).first()
                if cargo_actual:
                    self.fields['cargo'].initial = cargo_actual.cargo
                    # Cargar jefe directo si existe
                    if cargo_actual.jefe_directo:
                        self.fields['jefe_directo'].initial = cargo_actual.jefe_directo
                    # Cargar lista de posibles jefes para el cargo actual
                    if cargo_actual.cargo and cargo_actual.cargo.cargo_jefe:
                        jefes_potenciales = self._obtener_jefes_potenciales(cargo_actual.cargo)
                        self.fields['jefe_directo'].queryset = jefes_potenciales
                # Inicializar departamento según la ciudad actual
                ciudad_actual = self.instance.ciudad_nacimiento
                if ciudad_actual:
                    self.fields['departamento'].initial = ciudad_actual.departamento
            except Exception as e:
                logger.warning(f"Error cargando cargo/departamento actual: {e}")

        # Si viene un cargo_id de POST, cargar los jefes potenciales
        if cargo_id:
            try:
                cargo = Cargo.objects.get(pk=cargo_id, activo=True)
                jefes_potenciales = self._obtener_jefes_potenciales(cargo)
                self.fields['jefe_directo'].queryset = jefes_potenciales
            except Cargo.DoesNotExist:
                pass
        # Si viene en data del POST, intentar obtener cargo_id
        elif self.data and self.data.get('cargo'):
            try:
                cargo_id = int(self.data.get('cargo'))
                cargo = Cargo.objects.get(pk=cargo_id, activo=True)
                jefes_potenciales = self._obtener_jefes_potenciales(cargo)
                self.fields['jefe_directo'].queryset = jefes_potenciales
            except (ValueError, Cargo.DoesNotExist):
                pass

        # Hacer campos requeridos más explícitos
        required_fields = [
            'tipo_documento', 'numero_documento', 'nombres', 'apellidos',
            'telefono_contacto', 'fecha_ingreso', 'sede', 'cargo'
        ]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
                # Agregar asterisco visual
                if not self.fields[field_name].label.endswith('*'):
                    self.fields[field_name].label += ' *'

    def _obtener_jefes_potenciales(self, cargo):
        """Obtiene los empleados que ocupan el cargo_jefe del cargo dado"""
        if not cargo or not cargo.cargo_jefe:
            return Empleado.objects.none()

        # Buscar empleados activos que ocupen el cargo_jefe
        jefes = Empleado.objects.filter(
            historialcargo__cargo=cargo.cargo_jefe,
            historialcargo__activo=True,
            estado__codigo__in=['999', 'ACTIVO', 'p-prue']  # Estados activos o en prueba
        ).distinct().select_related('estado')

        return jefes

    def clean_direccion(self):
        value = self.cleaned_data.get('direccion', '').strip()
        # Solo permite palabras completas al inicio, case-insensitive y sin abreviaturas
        tipos_via = ["Calle", "Carrera", "Avenida", "Vereda", "Transversal", "Diagonal", "Autopista", "SIN DIRECCIÓN", "Manzana", "Lote", "Pasaje", "Circular", "Circunvalar"]
        import re
        pattern = r"^(%s)\b" % "|".join(tipos_via)
        if not re.match(pattern, value, re.IGNORECASE):
            raise forms.ValidationError(
                "La dirección debe iniciar con el tipo de vía completo (ejemplo: Calle, Carrera, Avenida, Vereda, etc.) y no se permiten abreviaturas."
            )
        # Validar que no se usen abreviaturas conocidas
        abreviaturas = [
            r"^C\b", r"^Cl\b", r"^Cll\b", r"^Ca\b", r"^Cra\b", r"^Cr\b", r"^V\b", r"^Ve\b", r"^Ver\b", r"^Vda\b"
        ]
        for abbr in abreviaturas:
            if re.match(abbr, value, re.IGNORECASE):
                raise forms.ValidationError(
                    "No se permiten abreviaturas al inicio de la dirección. Escriba la palabra completa."
                )
        return value

    def clean_numero_documento(self):
        """Validar número de documento"""
        numero = self.cleaned_data.get('numero_documento')
        if not numero:
            raise ValidationError('El número de documento es requerido.')
            
        # Remover espacios y caracteres especiales
        numero = re.sub(r'[^\d]', '', numero)
        
        # Validar que solo contenga números
        if not numero.isdigit():
            raise ValidationError('El número de documento solo debe contener números.')
        
        # Validar longitud
        if len(numero) < 6:
            raise ValidationError('El número de documento debe tener al menos 6 dígitos.')
        
        if len(numero) > 15:
            raise ValidationError('El número de documento no puede tener más de 15 dígitos.')
        
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
            raise ValidationError('El teléfono de contacto es requerido.')
        
        # Remover espacios y caracteres especiales excepto +
        telefono_limpio = re.sub(r'[^\d+]', '', telefono)
        
        # Patrones válidos para Colombia
        patrones = [
            r'^\+57[39]\d{9}$',  # +573001234567
            r'^[39]\d{9}$',      # 3001234567
            r'^\d{7}$',          # 1234567 (fijo)
            r'^\+57\d{7}$',      # +571234567 (fijo)
        ]
        
        if not any(re.match(patron, telefono_limpio) for patron in patrones):
            raise ValidationError(
                'Formato de teléfono inválido. Use formato colombiano: +57 300 123 4567 o 300 123 4567'
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
        
        if edad > 80:
            raise ValidationError('Verifique la fecha de nacimiento, parece incorrecta.')
        
        return fecha

    def clean_fecha_ingreso(self):
        """Validar fecha de ingreso"""
        fecha = self.cleaned_data.get('fecha_ingreso')
        if not fecha:
            raise ValidationError('La fecha de ingreso es requerida.')
        
        # No puede ser fecha futura (más de 1 día)
        if fecha > date.today() + timedelta(days=1):
            raise ValidationError('La fecha de ingreso no puede ser en el futuro.')
        
        # No puede ser muy antigua (más de 50 años)
        if fecha < date.today() - timedelta(days=365*50):
            raise ValidationError('La fecha de ingreso parece muy antigua.')
        
        return fecha

    def clean_correo_electronico(self):
        """Validar email"""
        email = self.cleaned_data.get('correo_electronico')
        
        if email:
            # Validar formato básico
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                raise ValidationError('Ingrese un email con formato válido.')
            
            # Validar que no exista en otro empleado
            # queryset = Empleado.objects.filter(correo_electronico=email)
            # if self.instance and self.instance.pk:
            #     queryset = queryset.exclude(pk=self.instance.pk)
            
            # if queryset.exists():
            #     raise ValidationError('Ya existe un empleado con este correo electrónico.')
        
        return email

    def clean_confirmar_email(self):
        """Validar confirmación de email"""
        email = self.cleaned_data.get('correo_electronico')
        confirmar_email = self.cleaned_data.get('confirmar_email')
        
        # Solo validar si ambos están presentes
        if email and confirmar_email:
            if email != confirmar_email:
                raise ValidationError('Los correos electrónicos no coinciden.')
        
        return confirmar_email

    def clean_contacto_emergencia_telefono(self):
        """Validar teléfono de emergencia"""
        telefono_emergencia = self.cleaned_data.get('contacto_emergencia_telefono')
        telefono_principal = self.cleaned_data.get('telefono_contacto')
        
        if telefono_emergencia:
            # Aplicar las mismas validaciones que al teléfono principal
            telefono_limpio = re.sub(r'[^\d+]', '', telefono_emergencia)
            
            patrones = [
                r'^\+57[39]\d{9}$',  # +573001234567
                r'^[39]\d{9}$',      # 3001234567
                r'^\d{7}$',          # 1234567 (fijo)
                r'^\+57\d{7}$',      # +571234567 (fijo)
            ]
            
            if not any(re.match(patron, telefono_limpio) for patron in patrones):
                raise ValidationError(
                    'Formato de teléfono de emergencia inválido.'
                )
            
            # Verificar que no sea el mismo que el teléfono principal
            if telefono_principal and telefono_limpio == re.sub(r'[^\d+]', '', telefono_principal):
                raise ValidationError(
                    'El teléfono de emergencia debe ser diferente al teléfono principal.'
                )
        
        return telefono_emergencia

    def clean_nombres(self):
        """Validar nombres"""
        nombres = self.cleaned_data.get('nombres')
        if not nombres:
            raise ValidationError('Los nombres son requeridos.')
        
        # Solo letras, espacios y algunos caracteres especiales
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nombres):
            raise ValidationError('Los nombres solo pueden contener letras y espacios.')
        
        # Al menos 2 caracteres
        if len(nombres.strip()) < 2:
            raise ValidationError('Los nombres deben tener al menos 2 caracteres.')
        
        return nombres.strip().title()

    def clean_apellidos(self):
        """Validar apellidos"""
        apellidos = self.cleaned_data.get('apellidos')
        if not apellidos:
            raise ValidationError('Los apellidos son requeridos.')
        
        # Solo letras, espacios y algunos caracteres especiales
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", apellidos):
            raise ValidationError('Los apellidos solo pueden contener letras y espacios.')
        
        # Al menos 2 caracteres
        if len(apellidos.strip()) < 2:
            raise ValidationError('Los apellidos deben tener al menos 2 caracteres.')
        
        return apellidos.strip().title()

    def clean(self):
        """Validaciones a nivel de formulario"""
        cleaned_data = super().clean()
        
        # Validar que la fecha de nacimiento sea coherente con la fecha de ingreso
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        fecha_ingreso = cleaned_data.get('fecha_ingreso')
        
        if fecha_nacimiento and fecha_ingreso:
            edad_al_ingreso = fecha_ingreso.year - fecha_nacimiento.year
            if edad_al_ingreso < 16:
                raise ValidationError(
                    'El empleado debe haber tenido al menos 16 años al momento del ingreso.'
                )
        
        # Validar que el cargo esté activo
        cargo = cleaned_data.get('cargo')
        if cargo and not cargo.activo:
            raise ValidationError('El cargo seleccionado no está activo.')
        
        # Validar que la sede esté activa
        sede = cleaned_data.get('sede')
        if sede and not sede.activa:
            raise ValidationError('La sede seleccionada no está activa.')
        
        return cleaned_data


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