from multiprocessing import context

# =============================================================================
# - core/views.py
#============================================================================= 


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import Count, Sum

from apps.employees.models import Empleado, EstadoEmpleado
from apps.authentication.models import Usuario

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
    # Si llegamos aquí, es un administrador o usuario sin empleado asociado
    
    try:
        # Estadísticas de empleados
        total_empleados = Empleado.objects.count()
        
        try:
            estado_activo = EstadoEmpleado.objects.get(codigo='ACTIVO')
            empleados_activos = Empleado.objects.filter(estado=estado_activo).count()
        except EstadoEmpleado.DoesNotExist:
            empleados_activos = 0
        
        try:
            estado_prueba = EstadoEmpleado.objects.get(codigo='PRUEBA')
            empleados_prueba = Empleado.objects.filter(estado=estado_prueba).count()
        except EstadoEmpleado.DoesNotExist:
            empleados_prueba = 0
        
        # Nuevos empleados este mes
        inicio_mes = timezone.now().replace(day=1).date()
        nuevos_mes = Empleado.objects.filter(fecha_ingreso__gte=inicio_mes).count()
        
        # === ESTADÍSTICAS DE DOCUMENTOS ===
        try:
            from apps.documents.models import DocumentoEmpleado, TipoDocumentoEmpleado
            
            # Documentos pendientes de aprobación
            documentos_pendientes = DocumentoEmpleado.objects.filter(
                estado_aprobacion='pendiente'
            ).count()
            
            # Documentos próximos a vencer (30 días)
            fecha_limite = date.today() + timedelta(days=30)
            documentos_por_vencer = DocumentoEmpleado.objects.filter(
                fecha_vencimiento__isnull=False,
                fecha_vencimiento__lte=fecha_limite,
                fecha_vencimiento__gte=date.today()
            ).count()
            
            # Documentos vencidos
            documentos_vencidos = DocumentoEmpleado.objects.filter(
                fecha_vencimiento__isnull=False,
                fecha_vencimiento__lt=date.today()
            ).count()
            
            # Empleados con documentación incompleta
            empleados_docs_incompletos = 0
            for empleado in Empleado.objects.filter(estado__codigo='PRUEBA'):
                docs_obligatorios = TipoDocumentoEmpleado.objects.filter(
                    obligatorio=True, activo=True
                )
                docs_aprobados = DocumentoEmpleado.objects.filter(
                    empleado=empleado,
                    estado_aprobacion='aprobado',
                    tipo_documento__in=docs_obligatorios
                ).count()
                
                if docs_aprobados < docs_obligatorios.count():
                    empleados_docs_incompletos += 1
                    
        except ImportError:
            # Si no está implementado el módulo de documentos
            documentos_pendientes = 0
            documentos_por_vencer = 0
            documentos_vencidos = 0
            empleados_docs_incompletos = 0
        
        # === ESTADÍSTICAS DE CAPACITACIONES ===
        try:
            from apps.training.models import InscripcionCapacitacion, Capacitacion
            
            capacitaciones_activas = Capacitacion.objects.filter(activo=True).count()
            empleados_con_capacitaciones_pendientes = InscripcionCapacitacion.objects.filter(
                completada=False
            ).values('empleado').distinct().count()
            
        except ImportError:
            capacitaciones_activas = 0
            empleados_con_capacitaciones_pendientes = 0
        
        # === ESTADÍSTICAS DE EVALUACIONES ===
        try:
            from apps.evaluations.models import AsignacionEvaluacion
            
            evaluaciones_pendientes = AsignacionEvaluacion.objects.filter(
                completada=False,
                fecha_limite__gte=date.today()
            ).count()
            
            evaluaciones_vencidas = AsignacionEvaluacion.objects.filter(
                completada=False,
                fecha_limite__lt=date.today()
            ).count()
            
        except ImportError:
            evaluaciones_pendientes = 0
            evaluaciones_vencidas = 0
        
        context = {
            # Información del usuario
            'is_admin_dashboard': True,
            
            # Estadísticas de empleados
            'total_empleados': total_empleados,
            'empleados_activos': empleados_activos,
            'empleados_prueba': empleados_prueba,
            'nuevos_mes': nuevos_mes,
            
            # Estadísticas de documentos
            'documentos_pendientes': documentos_pendientes,
            'documentos_por_vencer': documentos_por_vencer,
            'documentos_vencidos': documentos_vencidos,
            'empleados_docs_incompletos': empleados_docs_incompletos,
            
            # Estadísticas de capacitaciones
            'capacitaciones_activas': capacitaciones_activas,
            'empleados_con_capacitaciones_pendientes': empleados_con_capacitaciones_pendientes,
            
            # Estadísticas de evaluaciones
            'evaluaciones_pendientes': evaluaciones_pendientes,
            'evaluaciones_vencidas': evaluaciones_vencidas,
            
            # Para alertas en el dashboard
            'alertas_documentos': {
                'pendientes': documentos_pendientes > 0,
                'vencimientos': documentos_por_vencer > 0,
                'vencidos': documentos_vencidos > 0,
                'incompletos': empleados_docs_incompletos > 0
            },
            
            'alertas_evaluaciones': {
                'pendientes': evaluaciones_pendientes > 0,
                'vencidas': evaluaciones_vencidas > 0,
            }
        }
        
        return render(request, 'core/dashboard.html', context)
        
    except Exception as e:
        # En caso de error, mostrar dashboard básico
        messages.error(request, f'Error cargando estadísticas del dashboard: {str(e)}')
        
        context = {
            'total_empleados': 0,
            'empleados_activos': 0,
            'empleados_prueba': 0,
            'nuevos_mes': 0,
            'is_admin_dashboard': True,
        }
        
        return render(request, 'core/dashboard.html', context)

# Vista basada en clase para el dashboard, reutiliza la lógica de dashboard_view
class DashboardView(LoginRequiredMixin, TemplateView):
    """Vista basada en clase del dashboard (alternativa)"""
    template_name = 'core/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar redirección antes de procesar"""
        return dashboard_view(request)

