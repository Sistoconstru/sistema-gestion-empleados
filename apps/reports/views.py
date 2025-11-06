from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Importar modelos que ya funcionan
from apps.employees.models import Empleado
from apps.training.models import Capacitacion
from apps.evaluations.models import AsignacionEvaluacion


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    """Dashboard de reportes con datos reales"""
    template_name = 'reports/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Datos reales de módulos que funcionan
        context.update({
            'total_empleados': Empleado.objects.count(),
            'capacitaciones_activas': Capacitacion.objects.filter(activa=True).count(),
            'evaluaciones_pendientes': AsignacionEvaluacion.objects.filter(estado='pendiente').count(),
            
            # Placeholders para módulos no implementados
            'satisfaccion_general': 0.0,  # Pendiente: módulo surveys
            'reconocimientos_mes': 0,     # Pendiente: módulo recognition
        })
        
        return context