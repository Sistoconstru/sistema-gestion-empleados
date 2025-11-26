from django import forms
from apps.employees.models import Empleado
from apps.organizational.models import AreaEmpresa
from .models import TipoEvaluacion, EvaluacionDesempeño

class FiltroAsignacionEvaluacionForm(forms.Form):
    tipo_evaluacion = forms.ModelChoiceField(
        queryset=TipoEvaluacion.objects.filter(activo=True),
        label="Tipo de Evaluación",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    area = forms.ModelChoiceField(
        queryset=AreaEmpresa.objects.filter(activa=True),
        label="Área",
        required=False,
        empty_label="-- Todas las áreas --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class EmpleadoMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.nombre_completo} - {obj.cargo_actual.cargo.nombre if obj.cargo_actual else ''} ({obj.area_actual.nombre if obj.area_actual else ''})"

class AsignacionEvaluacionManualForm(forms.Form):
    empleados = EmpleadoMultipleChoiceField(
        queryset=Empleado.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Empleados a asignar"
    )
    dias_disponibles = forms.IntegerField(min_value=1, label="Días disponibles para completar la evaluación", required=True)
    # El evaluador (jefe inmediato) se determina en backend
    # El usuario que asigna se toma de request.user
    # La fecha de inicio es la fecha de asignación

    def __init__(self, *args, **kwargs):
        empleados_queryset = kwargs.pop('empleados_queryset', None)
        super().__init__(*args, **kwargs)
        if empleados_queryset is not None:
            self.fields['empleados'].queryset = empleados_queryset
