"""Formularios del módulo de transporte."""
from datetime import date, timedelta

from django import forms
from django.utils import timezone

from apps.employees.models import Empleado

from .models import (
    DocumentoVehiculo, GastoVehiculo, ServicioIniciado, Vehiculo,
)

# Hasta cuándo se puede colgar un gasto de un servicio. Un peaje se registra
# el mismo día o al siguiente; un mes después ya nadie recuerda de cuál
# viaje era, y la lista se vuelve imposible de usar en un celular.
DIAS_SERVICIOS_ELEGIBLES = 30


def _etiqueta_servicio(servicio):
    """Cómo se lee un servicio en el desplegable del conductor."""
    cuando = timezone.localtime(servicio.iniciado_en).strftime('%d/%m')
    partes = [cuando, servicio.ref or str(servicio.odoo_id)]
    if servicio.resumen:
        partes.append(servicio.resumen)
    return ' · '.join(partes)[:120]


def _etiqueta_servicio_con_conductor(servicio):
    return f'{servicio.conductor.nombre_completo} — {_etiqueta_servicio(servicio)}'[:160]


class DocumentoVehiculoForm(forms.ModelForm):
    """Registrar o renovar un documento del vehículo.

    El vencimiento se deja en blanco a propósito: lo calcula el modelo según
    el tipo. Quien lo registra solo tiene que saber cuándo se expidió, que es
    lo que dice el papel que tiene en la mano.
    """

    class Meta:
        model = DocumentoVehiculo
        fields = ['tipo', 'numero', 'entidad', 'fecha_expedicion',
                  'fecha_vencimiento', 'valor', 'aplica', 'archivo',
                  'observaciones']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de póliza o certificado'}),
            'entidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Aseguradora o centro de diagnóstico'}),
            'fecha_expedicion': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 0, 'step': '1'}),
            'aplica': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'archivo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,application/pdf'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2}),
        }
        help_texts = {
            'fecha_vencimiento': (
                'Déjalo vacío y se calcula solo: SOAT, tecnomecánica y '
                'póliza al año de la expedición, impuesto el 30 de junio y '
                'rodamiento el 31 de diciembre. Si la póliza es a otro plazo, '
                'escribe la fecha.'),
            'aplica': 'Desmarca si este tributo no aplica al vehículo.',
        }

    def __init__(self, *args, vehiculo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.vehiculo = vehiculo
        self.fields['fecha_expedicion'].widget.attrs['max'] = date.today().isoformat()
        self.fields['numero'].required = False
        self.fields['entidad'].required = False
        self.fields['fecha_expedicion'].required = False

    def save(self, commit=True, usuario=None):
        doc = super().save(commit=False)
        if self.vehiculo:
            doc.vehiculo = self.vehiculo
        if usuario and not doc.registrado_por_id:
            doc.registrado_por = usuario
        if commit:
            doc.save()
        return doc


class GastoVehiculoForm(forms.ModelForm):
    """Registro de un gasto por parte del conductor.

    El recibo es obligatorio: sin soporte el gasto no se legaliza, y pedirlo
    después nunca funciona.

    El vehículo viene propuesto —el que conduce— pero se puede cambiar o
    dejar vacío: tanquear el camión de un compañero es un gasto de ese
    camión, y un almuerzo en ruta no es de ninguno.
    """

    class Meta:
        model = GastoVehiculo
        fields = ['vehiculo', 'servicio', 'tipo', 'monto', 'fecha',
                  'descripcion', 'responsable', 'kilometraje', 'recibo']
        widgets = {
            'vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'servicio': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={
                'class': 'form-select', 'id': 'id_tipo_gasto'}),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'min': 1, 'step': '1', 'inputmode': 'numeric',
                'placeholder': '0'}),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estación, taller, peaje...'}),
            'responsable': forms.Select(attrs={
                'class': 'form-select', 'id': 'id_responsable_gasto'}),
            'kilometraje': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 0, 'step': '1',
                'inputmode': 'numeric', 'placeholder': 'Opcional'}),
            'recibo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,application/pdf'}),
        }

    def __init__(self, *args, vehiculo=None, conductor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.conductor = conductor
        self.fields['fecha'].widget.attrs['max'] = date.today().isoformat()
        # `_state.adding` y no `instance.pk`: la clave primaria es un UUID con
        # default, así que ya trae valor antes de guardar y preguntar por el
        # pk daría "ya existe" para un gasto que se está creando.
        es_nuevo = self.instance._state.adding
        if es_nuevo:
            self.fields['fecha'].initial = date.today()
            if vehiculo is not None:
                self.fields['vehiculo'].initial = vehiculo
        self.fields['responsable'].required = False
        self.fields['responsable'].choices = (
            [('', '— Solo para multas —')] + list(GastoVehiculo.RESPONSABLES))
        # Al corregir, el gasto ya tiene recibo y se puede dejar el mismo; al
        # crearlo no puede faltar, porque sin soporte no se legaliza.
        self.fields['recibo'].required = es_nuevo

        self.fields['vehiculo'].required = False
        self.fields['vehiculo'].empty_label = '— Ningún vehículo —'
        self.fields['vehiculo'].queryset = Vehiculo.objects.filter(
            activo=True).order_by('placa')

        # Solo los servicios de este conductor, y solo los recientes: una
        # lista con todo el histórico es inservible en un celular.
        self.fields['servicio'].required = False
        self.fields['servicio'].empty_label = '— No es por un servicio —'
        self.fields['servicio'].queryset = self._servicios_del_conductor(conductor)
        self.fields['servicio'].label_from_instance = _etiqueta_servicio

    @staticmethod
    def _servicios_del_conductor(conductor):
        if not conductor:
            return ServicioIniciado.objects.none()
        desde = timezone.now() - timedelta(days=DIAS_SERVICIOS_ELEGIBLES)
        return (ServicioIniciado.objects
                .filter(conductor=conductor, anulado_en__isnull=True,
                        iniciado_en__gte=desde)
                .select_related('vehiculo')
                .order_by('-iniciado_en'))

    def save(self, commit=True, usuario=None):
        gasto = super().save(commit=False)
        if self.conductor and not gasto.conductor_id:
            gasto.conductor = self.conductor
        if usuario and not gasto.registrado_por_id:
            gasto.registrado_por = usuario
        if commit:
            gasto.save()
        return gasto


class GastoAdminForm(GastoVehiculoForm):
    """Lo mismo, pero lo registra el coordinador a nombre de un conductor.

    Nace aprobado: pedirle al coordinador que después apruebe lo que él
    mismo digitó es una vuelta sin sentido. Queda la marca de quién lo
    registró, que es lo que permite distinguirlo del que sube el conductor.
    """

    class Meta(GastoVehiculoForm.Meta):
        fields = ['conductor'] + GastoVehiculoForm.Meta.fields
        widgets = dict(GastoVehiculoForm.Meta.widgets,
                       conductor=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, conductores=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['conductor'].required = True
        self.fields['conductor'].queryset = (
            conductores if conductores is not None
            else Empleado.objects.none()).order_by('apellidos', 'nombres')
        self.fields['conductor'].empty_label = '— Escoge el conductor —'
        # El servicio depende del conductor, que aquí se escoge en el mismo
        # formulario: se ofrecen los de todos los conductores a cargo y la
        # validación comprueba que el elegido sea de quien corresponde.
        self.fields['servicio'].queryset = (
            ServicioIniciado.objects
            .filter(conductor__in=self.fields['conductor'].queryset,
                    anulado_en__isnull=True,
                    iniciado_en__gte=timezone.now() - timedelta(
                        days=DIAS_SERVICIOS_ELEGIBLES))
            .select_related('vehiculo', 'conductor')
            .order_by('-iniciado_en'))
        self.fields['servicio'].label_from_instance = _etiqueta_servicio_con_conductor

    def clean(self):
        datos = super().clean()
        servicio, conductor = datos.get('servicio'), datos.get('conductor')
        if servicio and conductor and servicio.conductor_id != conductor.pk:
            raise forms.ValidationError({
                'servicio': f'Ese servicio es de '
                            f'{servicio.conductor.nombre_completo}, no de '
                            f'{conductor.nombre_completo}.'
            })
        return datos


class RevisionGastoForm(forms.Form):
    """Aprobar o rechazar un gasto."""
    decision = forms.ChoiceField(
        choices=[('aprobar', 'Aprobar'), ('rechazar', 'Rechazar')])
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))

    def clean(self):
        datos = super().clean()
        if datos.get('decision') == 'rechazar' and not (
                datos.get('observaciones') or '').strip():
            raise forms.ValidationError(
                'Para rechazar un gasto hay que decir por qué: el conductor '
                'necesita saber qué corregir.')
        return datos
