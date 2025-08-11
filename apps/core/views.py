# =============================================================================
# core/views.py
# =============================================================================

import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import Count, Sum

from apps.employees.models import Empleado, EstadoEmpleado
from apps.training.models import InscripcionCapacitacion
from apps.documents.models import DocumentoEmpleado
from apps.evaluations.models import AsignacionEvaluacion

# Configurar logging
logger = logging.getLogger(__name__)

@login_required
def dashboard_view(request):
    """Vista del dashboard principal con lógica de redirección por rol"""
    
    # === LÓGICA DE REDIRECCIÓN AUTOMÁTICA ===
    # Si el usuario es un empleado normal (no administrador), 
    # redirigir a su perfil personal
    try:
        empleado = Empleado.objects.get(usuario=request.user)
        
        # Verificar si es empleado normal (no tiene permisos de administrador)
        if not request.user.is_staff and not request.user.is_superuser:
            # Verificar si no tiene roles administrativos
            # (Aquí puedes agregar lógica adicional para verificar roles)
            
            # Mostrar mensaje de bienvenida solo la primera vez
            if not request.session.get('welcome_shown', False):
                messages.success(
                    request, 
                    f'¡Bienvenido {empleado.nombres}! Este es tu perfil personal.'
                )
                request.session['welcome_shown'] = True
            
            # Redirigir al perfil del empleado
            return redirect('employees:empleado_perfil_detail', pk=empleado.pk)
            
    except Empleado.DoesNotExist:
        # Si el usuario no tiene empleado asociado, continuar al dashboard normal
        pass
    
    # === DASHBOARD PARA ADMINISTRADORES ===
    context = {}
    
    try:
        # Total real de empleados (incluyendo todos los estados)
        context['total_empleados'] = Empleado.objects.count()
        
        # Empleados activos - verificar si existe el estado
        try:
            estado_activo = EstadoEmpleado.objects.get(codigo='999')  # Activo
            context['empleados_activos'] = Empleado.objects.filter(
                estado=estado_activo
            ).count()
        except EstadoEmpleado.DoesNotExist:
            logger.warning("Estado código '999' (Activo) no encontrado en la base de datos")
            context['empleados_activos'] = 0
        
        # Empleados en período de prueba - verificar si existe el estado
        try:
            estado_prueba = EstadoEmpleado.objects.get(codigo='p-prue')  # Periodo de prueba
            context['empleados_prueba'] = Empleado.objects.filter(
                estado=estado_prueba
            ).count()
        except EstadoEmpleado.DoesNotExist:
            logger.warning("Estado código 'p-prue' (Periodo de prueba) no encontrado en la base de datos")
            context['empleados_prueba'] = 0
        
        # Nuevos empleados este mes
        inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        context['nuevos_mes'] = Empleado.objects.filter(
            fecha_ingreso__gte=inicio_mes
        ).count()
        
        # Calcular porcentaje de empleados activos
        if context['total_empleados'] > 0:
            context['porcentaje_activos'] = round(
                (context['empleados_activos'] / context['total_empleados']) * 100
            )
        else:
            context['porcentaje_activos'] = 0
        
        # === ESTADÍSTICAS DE CAPACITACIONES ===
        context['capacitaciones_activas'] = InscripcionCapacitacion.objects.filter(
            estado='en_progreso'
        ).count()
        
        # === ESTADÍSTICAS DE DOCUMENTOS ===
        # Documentos pendientes de aprobación
        context['documentos_pendientes'] = DocumentoEmpleado.objects.filter(
            estado_aprobacion='pendiente'
        ).count()
        
        # Documentos por vencer en los próximos 30 días
        fecha_limite = timezone.now().date() + timedelta(days=30)
        context['documentos_por_vencer'] = DocumentoEmpleado.objects.filter(
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gt=timezone.now().date()
        ).count()
        
        # Documentos ya vencidos
        context['documentos_vencidos'] = DocumentoEmpleado.objects.filter(
            fecha_vencimiento__lt=timezone.now().date()
        ).count()
        
        # Empleados con documentación incompleta
        context['empleados_docs_incompletos'] = Empleado.objects.annotate(
            num_docs=Count('documentoempleado')
        ).filter(num_docs__lt=3).count()  # Asumiendo que cada empleado debe tener al menos 3 documentos
        
        # === ALERTAS ===
        context.update({
            'alertas_documentos': {
                'pendientes': context['documentos_pendientes'] > 0,
                'vencimientos': context['documentos_por_vencer'] > 0,
                'vencidos': context['documentos_vencidos'] > 0,
                'incompletos': context['empleados_docs_incompletos'] > 0
            }
        })
        
        # Marcar que es dashboard de admin
        context['is_admin_dashboard'] = True
            
    except Exception as e:
        # Si hay algún error, establecer valores por defecto
        context.update({
            'total_empleados': 0,
            'empleados_activos': 0,
            'empleados_prueba': 0,
            'nuevos_mes': 0,
            'porcentaje_activos': 0,
            'capacitaciones_activas': 0,
            'documentos_pendientes': 0,
            'documentos_por_vencer': 0,
            'documentos_vencidos': 0,
            'empleados_docs_incompletos': 0,
            'alertas_documentos': {
                'pendientes': False,
                'vencimientos': False, 
                'vencidos': False,
                'incompletos': False
            },
            'is_admin_dashboard': True
        })
        messages.error(request, f'Error al cargar estadísticas: {str(e)}')
    
    return render(request, 'core/dashboard.html', context)

# Vista basada en clase para el dashboard, reutiliza la lógica de dashboard_view
class DashboardView(LoginRequiredMixin, TemplateView):
    """Vista basada en clase del dashboard (alternativa)"""
    template_name = 'core/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar redirección antes de procesar"""
        return dashboard_view(request)

