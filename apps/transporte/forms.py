"""Formularios del módulo de transporte."""
from datetime import date

from django import forms

from .models import DocumentoVehiculo, GastoVehiculo


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
                'Déjalo vacío y se calcula solo: SOAT y tecnomecánica al año '
                'de la expedición, impuesto el 30 de junio y rodamiento el 31 '
                'de diciembre.'),
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
    """

    class Meta:
        model = GastoVehiculo
        fields = ['tipo', 'monto', 'fecha', 'descripcion', 'responsable',
                  'kilometraje', 'recibo']
        widgets = {
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
        self.vehiculo = vehiculo
        self.conductor = conductor
        self.fields['fecha'].widget.attrs['max'] = date.today().isoformat()
        # `_state.adding` y no `instance.pk`: la clave primaria es un UUID con
        # default, así que ya trae valor antes de guardar y preguntar por el
        # pk daría "ya existe" para un gasto que se está creando.
        es_nuevo = self.instance._state.adding
        if es_nuevo:
            self.fields['fecha'].initial = date.today()
        self.fields['responsable'].required = False
        self.fields['responsable'].choices = (
            [('', '— Solo para multas —')] + list(GastoVehiculo.RESPONSABLES))
        # Al corregir, el gasto ya tiene recibo y se puede dejar el mismo; al
        # crearlo no puede faltar, porque sin soporte no se legaliza.
        self.fields['recibo'].required = es_nuevo

    def save(self, commit=True):
        gasto = super().save(commit=False)
        if self.vehiculo:
            gasto.vehiculo = self.vehiculo
        if self.conductor:
            gasto.conductor = self.conductor
        if commit:
            gasto.save()
        return gasto


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
