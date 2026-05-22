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
        
        # Empleados activos - buscar entre los códigos posibles
        empleados_activos = 0
        try:
            # Intentar con diferentes códigos de estado activo
            codigos_activo = ['999']
            for codigo in codigos_activo:
                try:
                    estado_activo = EstadoEmpleado.objects.get(codigo=codigo)
                    count = Empleado.objects.filter(estado=estado_activo).count()
                    if count > 0:
                        empleados_activos += count
                        logger.info(f"Encontrados {count} empleados activos con código '{codigo}'")
                        break  # Solo salir si realmente encontramos empleados
                    else:
                        logger.info(f"Estado '{codigo}' existe pero no tiene empleados asignados")
                        continue  # Continuar buscando con otros códigos
                except EstadoEmpleado.DoesNotExist:
                    logger.info(f"Estado con código '{codigo}' no existe")
                    continue
            
            context['empleados_activos'] = empleados_activos
            
        except Exception as e:
            logger.warning(f"Error calculando empleados activos: {e}")
            context['empleados_activos'] = 0

        # Empleados en período de prueba - buscar entre los códigos posibles
        empleados_prueba = 0
        try:
            # Intentar con diferentes códigos de estado de prueba
            codigos_prueba = ['p-prue']
            for codigo in codigos_prueba:
                try:
                    estado_prueba = EstadoEmpleado.objects.get(codigo=codigo)
                    count = Empleado.objects.filter(estado=estado_prueba).count()
                    if count > 0:
                        empleados_prueba += count
                        logger.info(f"Encontrados {count} empleados en prueba con código '{codigo}'")
                        break  # Solo salir si realmente encontramos empleados
                    else:
                        logger.info(f"Estado '{codigo}' existe pero no tiene empleados en prueba")
                        continue  # Continuar buscando con otros códigos
                except EstadoEmpleado.DoesNotExist:
                    logger.info(f"Estado de prueba con código '{codigo}' no existe")
                    continue
            
            context['empleados_prueba'] = empleados_prueba
            
        except Exception as e:
            logger.warning(f"Error calculando empleados en prueba: {e}")
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
        
        # === ESTADÍSTICAS DE EVALUACIONES ===
        try:
            # Evaluaciones pendientes como evaluador
            evaluaciones_pendientes = 0
            try:
                # Obtener el empleado del usuario actual
                empleado_usuario = Empleado.objects.get(usuario=request.user)
                evaluaciones_pendientes = AsignacionEvaluacion.objects.filter(
                    evaluador=empleado_usuario,
                    estado__in=['pendiente', 'en_progreso']
                ).count()
            except Empleado.DoesNotExist:
                # Si el usuario no es empleado, no tiene evaluaciones pendientes
                evaluaciones_pendientes = 0
            
            # Empleados próximos a cumplir 60 días sin evaluación completada
            fecha_limite_evaluacion = timezone.now().date() - timedelta(days=25)  # 25 días o más
            fecha_limite_activacion = timezone.now().date() - timedelta(days=55)   # Próximos a 60 días
            
            # Buscar empleados en período de prueba entre 25-59 días sin evaluación
            codigos_prueba = ['p-prue']
            estado_prueba = None
            
            for codigo in codigos_prueba:
                try:
                    estado_prueba = EstadoEmpleado.objects.get(codigo=codigo)
                    break
                except EstadoEmpleado.DoesNotExist:
                    continue
            
            empleados_sin_evaluacion = 0
            if estado_prueba:
                from django.db.models import Q, Count
                # Contar empleados en período de prueba sin evaluaciones completadas
                empleados_sin_evaluacion = Empleado.objects.filter(
                    estado=estado_prueba,
                    fecha_ingreso__lte=fecha_limite_evaluacion,
                    fecha_ingreso__gte=fecha_limite_activacion
                ).annotate(
                    evaluaciones_completadas=Count(
                        'evaluaciones_recibidas',
                        filter=Q(evaluaciones_recibidas__estado='completada')
                    )
                ).filter(
                    evaluaciones_completadas=0
                ).count()
            
            # Evaluaciones pendientes de aprobación (solo para administradores)
            evaluaciones_pendientes_aprobacion = 0
            empleados_requieren_desactivacion = 0
            if request.user.is_superuser:
                evaluaciones_pendientes_aprobacion = AsignacionEvaluacion.objects.filter(
                    estado='completada',
                    estado_aprobacion='pendiente_aprobacion'
                ).count()
                print(f"DEBUG: Evaluaciones pendientes de aprobación: {evaluaciones_pendientes_aprobacion}")
                
                # Empleados que reprobaron evaluaciones aprobadas (puntaje total ≤ 13) y requieren desactivación
                empleados_requieren_desactivacion = AsignacionEvaluacion.objects.filter(
                    estado='completada',
                    estado_aprobacion='aprobada',
                    puntaje_total__lte=13,  # Puntaje total menor o igual a 13 = reprobado
                    empleado_evaluado__estado__codigo='p-prue'  # Solo empleados en período de prueba
                ).values('empleado_evaluado').distinct().count()
                print(f"DEBUG: Empleados que requieren desactivación: {empleados_requieren_desactivacion}")

            context.update({
                'evaluaciones_pendientes_evaluador': evaluaciones_pendientes,
                'empleados_sin_evaluacion': empleados_sin_evaluacion,
                'evaluaciones_pendientes_aprobacion': evaluaciones_pendientes_aprobacion,
                'empleados_requieren_desactivacion': empleados_requieren_desactivacion,
            })
            
        except Exception as e:
            logger.warning(f"Error calculando estadísticas de evaluaciones: {e}")
            context.update({
                'evaluaciones_pendientes_evaluador': 0,
                'empleados_sin_evaluacion': 0,
                'evaluaciones_pendientes_aprobacion': 0,
                'empleados_requieren_desactivacion': 0,
            })
        
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
        
        # === EMPLEADOS LISTOS PARA ACTIVAR ===
        # Empleados en período de prueba que han cumplido 60 días
        empleados_listos_activar = 0
        empleados_listos_nombres = []
        try:
            # Buscar estado de período de prueba
            codigos_prueba = ['p-prue']
            estado_prueba = None
            
            for codigo in codigos_prueba:
                try:
                    estado_prueba = EstadoEmpleado.objects.get(codigo=codigo)
                    break
                except EstadoEmpleado.DoesNotExist:
                    continue
            
            if estado_prueba:
                # Calcular fecha límite (hace 60 días o más)
                fecha_limite = timezone.now().date() - timedelta(days=60)
                
                # Buscar empleados que cumplan el período
                empleados_listos_queryset = Empleado.objects.filter(
                    estado=estado_prueba,
                    fecha_ingreso__lte=fecha_limite
                ).select_related('estado')[:10]  # Límite para evitar listas muy largas
                
                empleados_listos_activar = empleados_listos_queryset.count()
                empleados_listos_nombres = [emp.nombre_completo for emp in empleados_listos_queryset]
                
                logger.info(f"Encontrados {empleados_listos_activar} empleados listos para activar")
                
        except Exception as e:
            logger.warning(f"Error calculando empleados listos para activar: {e}")
            empleados_listos_activar = 0
            empleados_listos_nombres = []
        
        context['empleados_listos_activar'] = empleados_listos_activar
        context['empleados_listos_nombres'] = empleados_listos_nombres
        
        # === ALERTAS ===
        context.update({
            'alertas_documentos': {
                'pendientes': context['documentos_pendientes'] > 0,
                'vencimientos': context['documentos_por_vencer'] > 0,
                'vencidos': context['documentos_vencidos'] > 0,
                'incompletos': context['empleados_docs_incompletos'] > 0
            },
            'alertas_empleados': {
                'listos_activar': context['empleados_listos_activar'] > 0
            },
            'alertas_evaluaciones': {
                'pendientes_supervisor': context.get('evaluaciones_pendientes_evaluador', 0) > 0,
                'empleados_sin_evaluacion': context.get('empleados_sin_evaluacion', 0) > 0,
                'pendientes_aprobacion': context.get('evaluaciones_pendientes_aprobacion', 0) > 0,
                'requieren_desactivacion': context.get('empleados_requieren_desactivacion', 0) > 0
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
            'empleados_listos_activar': 0,
            'empleados_listos_nombres': [],
            'evaluaciones_pendientes_evaluador': 0,
            'empleados_sin_evaluacion': 0,
            'evaluaciones_pendientes_aprobacion': 0,
            'empleados_requieren_desactivacion': 0,
            'alertas_documentos': {
                'pendientes': False,
                'vencimientos': False, 
                'vencidos': False,
                'incompletos': False
            },
            'alertas_empleados': {
                'listos_activar': False
            },
            'alertas_evaluaciones': {
                'pendientes_supervisor': False,
                'empleados_sin_evaluacion': False,
                'pendientes_aprobacion': False,
                'requieren_desactivacion': False
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

