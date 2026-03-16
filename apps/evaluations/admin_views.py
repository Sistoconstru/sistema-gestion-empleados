"""
Vistas personalizadas para el admin de evaluations
"""
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django import forms
from datetime import datetime, timedelta
from .models import EvaluacionCargo


class ActivarEvaluacionForm(forms.Form):
    """Formulario para activar evaluaciones"""
    fecha_vencimiento = forms.DateField(
        label='Fecha de Vencimiento',
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Fecha límite para que los empleados completen la evaluación',
        initial=lambda: (datetime.now() + timedelta(days=30)).date()
    )
    periodo = forms.CharField(
        label='Período de Evaluación',
        max_length=100,
        initial=lambda: str(datetime.now().year),
        help_text='Ej: 2026 o "Evaluación Anual 2026"'
    )


@staff_member_required
def activar_evaluaciones_form(request):
    """Vista intermedia para activar evaluaciones con fecha específica"""
    # Obtener IDs de la sesión
    evaluaciones_ids = request.session.get('evaluaciones_a_activar', [])
    
    if not evaluaciones_ids:
        messages.error(request, 'No hay evaluaciones para activar')
        return redirect('admin:evaluations_evaluacioncargo_changelist')
    
    evaluaciones = EvaluacionCargo.objects.filter(
        id__in=evaluaciones_ids,
        estado='programada'
    ).select_related('evaluacion', 'cargo')
    
    if request.method == 'POST':
        form = ActivarEvaluacionForm(request.POST)
        if form.is_valid():
            fecha_vencimiento = form.cleaned_data['fecha_vencimiento']
            periodo = form.cleaned_data['periodo']
            
            count = 0
            for ec in evaluaciones:
                # Actualizar campos
                ec.estado = 'activa'
                ec.fecha_activacion = timezone.now()
                ec.fecha_vencimiento_planeada = fecha_vencimiento
                ec.activada_por = request.user
                ec.save()  # El signal se encargará de crear las asignaciones
                count += 1
            
            # Limpiar sesión
            del request.session['evaluaciones_a_activar']
            
            messages.success(
                request,
                f'{count} evaluación(es) activada(s) exitosamente. '
                f'Se crearon las asignaciones a empleados automáticamente. '
                f'Fecha de vencimiento: {fecha_vencimiento.strftime("%d/%m/%Y")}'
            )
            return redirect('admin:evaluations_evaluacioncargo_changelist')
    else:
        form = ActivarEvaluacionForm()
    
    context = {
        'form': form,
        'evaluaciones': evaluaciones,
        'title': 'Activar Evaluaciones',
        'site_title': 'Administración',
        'site_header': 'Activación de Evaluaciones',
    }
    
    return render(request, 'admin/evaluations/activar_evaluaciones.html', context)
