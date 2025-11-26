# Decoradores de autenticación y métodos
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.http import HttpResponse
from .forms import FiltroAsignacionEvaluacionForm, AsignacionEvaluacionManualForm
# --- Vista AJAX para asignación manual de evaluaciones ---
@login_required
@require_http_methods(["GET", "POST"])
def asignar_evaluacion_manual(request):
    """
    Vista AJAX para mostrar y procesar el formulario de asignación manual de evaluaciones.
    """
    from apps.organizational.models import AreaEmpresa
    from apps.evaluations.models import TipoEvaluacion
    from apps.employees.models import Empleado
    context = {}
    tipos = TipoEvaluacion.objects.filter(activo=True)
    areas = AreaEmpresa.objects.filter(activa=True)
    filtro_form = FiltroAsignacionEvaluacionForm(request.POST or None)
    empleados_form = None
    empleados_queryset = Empleado.objects.none()
    mostrar_empleados = False
    mensaje = None

    if request.method == "POST":
        # Distinguir entre filtrado y asignación
        if 'filtrar' in request.POST:
            # Filtrar empleados según tipo de evaluación y área
            # Solo validar el formulario de filtro, NO el de empleados
            if filtro_form.is_valid():
                tipo_evaluacion = filtro_form.cleaned_data['tipo_evaluacion']
                area = filtro_form.cleaned_data['area']
                empleados_queryset = Empleado.objects.all()
                if area:
                    # area_actual es una propiedad, filtrar por historialcargo activo
                    empleados_queryset = empleados_queryset.filter(
                        historialcargo__activo=True,
                        historialcargo__cargo__area=area
                    ).distinct()
                # Crear formulario VACÍO (sin datos POST) para nueva búsqueda
                empleados_form = AsignacionEvaluacionManualForm(empleados_queryset=empleados_queryset)
                mostrar_empleados = True
            else:
                # Si el filtro no es válido, mostrar formulario vacío
                empleados_form = None
                mostrar_empleados = False
        elif 'asignar' in request.POST:
            # Asignar evaluaciones
            empleados_queryset = Empleado.objects.all()
            empleados_form = AsignacionEvaluacionManualForm(request.POST, empleados_queryset=empleados_queryset)
            if filtro_form.is_valid() and empleados_form.is_valid():
                tipo_evaluacion = filtro_form.cleaned_data['tipo_evaluacion']
                dias_disponibles = empleados_form.cleaned_data['dias_disponibles']
                empleados = empleados_form.cleaned_data['empleados']
                try:
                    from .models import EvaluacionDesempeño, AsignacionEvaluacion
                    evaluacion = EvaluacionDesempeño.objects.filter(tipo_evaluacion=tipo_evaluacion, activa=True).first()
                    if not evaluacion:
                        mensaje = 'No existe una evaluación activa para el tipo seleccionado.'
                    else:
                        for empleado in empleados:
                            jefe = None
                            if empleado.cargo_actual and empleado.cargo_actual.cargo.cargo_jefe:
                                jefe = Empleado.objects.filter(historialcargo__cargo=empleado.cargo_actual.cargo.cargo_jefe, historialcargo__activo=True).first()
                            AsignacionEvaluacion.objects.create(
                                empleado_evaluado=empleado,
                                evaluacion=evaluacion,
                                evaluador=jefe,
                                periodo_evaluacion=str(tipo_evaluacion.nombre)[:20],
                                fecha_vencimiento=timezone.now().date() + timezone.timedelta(days=int(dias_disponibles)),
                                es_autoevaluacion=tipo_evaluacion.es_autoevaluacion,
                                asignado_por=request.user,
                            )
                        mensaje = 'Evaluaciones asignadas correctamente.'
                        filtro_form = FiltroAsignacionEvaluacionForm()
                        empleados_form = None
                        mostrar_empleados = False
                except Exception as e:
                    mensaje = f'Error: {str(e)}'
            else:
                mostrar_empleados = True
        else:
            empleados_form = AsignacionEvaluacionManualForm()
    else:
        filtro_form = FiltroAsignacionEvaluacionForm()
        empleados_form = None

    context = {
        'tipos': tipos,
        'areas': areas,
        'filtro_form': filtro_form,
        'empleados_form': empleados_form,
        'mostrar_empleados': mostrar_empleados,
        'mensaje': mensaje,
    }
    html = render_to_string('evaluations/partials/form_asignar_evaluacion.html', context, request=request)
    return HttpResponse(html)
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.db import transaction, models
from django.db.models import Count, Q
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import date

from .models import (
    AsignacionEvaluacion, 
    EvaluacionDesempeño, 
    RespuestaEvaluacion,
    ResultadoEvaluacion,
    PreguntaEvaluacion,
    OpcionEvaluacion
)
from apps.employees.models import Empleado


class EvaluacionesIndexView(LoginRequiredMixin, TemplateView):
    """Vista principal del módulo de evaluaciones"""
    template_name = 'evaluations/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        
        try:
            # Obtener el empleado del usuario actual
            empleado_usuario = Empleado.objects.get(usuario=usuario)
            
            # Evaluaciones donde soy evaluador directo (pendientes)
            evaluaciones_pendientes = AsignacionEvaluacion.objects.filter(
                evaluador=empleado_usuario,
                estado__in=['pendiente', 'en_progreso']
            ).select_related(
                'empleado_evaluado', 
                'evaluacion',
                'evaluacion__tipo_evaluacion'
            ).order_by('-fecha_asignacion')
            
        except Empleado.DoesNotExist:
            # Usuario no es empleado (ej: superusuario)
            evaluaciones_pendientes = AsignacionEvaluacion.objects.none()
            empleado_usuario = None
        
        # Evaluaciones donde soy empleado evaluado
        mis_evaluaciones = AsignacionEvaluacion.objects.filter(
            empleado_evaluado__usuario=usuario
        ).select_related(
            'evaluador',
            'evaluacion', 
            'evaluacion__tipo_evaluacion'
        ).order_by('-fecha_asignacion')
        
        # Si soy superusuario, puedo ver todas las evaluaciones
        if usuario.is_superuser:
            # Ver todas las evaluaciones pendientes del sistema
            todas_evaluaciones_pendientes = AsignacionEvaluacion.objects.filter(
                estado__in=['pendiente', 'en_progreso']
            ).select_related(
                'empleado_evaluado', 
                'evaluacion',
                'evaluacion__tipo_evaluacion',
                'evaluador'
            ).order_by('-fecha_asignacion')
            
            # Para superusuarios, mantener evaluaciones_pendientes como están
            # pero agregar contexto de que es superusuario
            evaluaciones_pendientes = todas_evaluaciones_pendientes
        
        # Estadísticas generales del sistema de evaluaciones
        from datetime import date, timedelta
        inicio_mes = date.today().replace(day=1)
        
        evaluaciones_completadas_mes = AsignacionEvaluacion.objects.filter(
            estado='completada',
            fecha_completada__gte=inicio_mes
        ).count()
        
        # Lista completa de evaluaciones para consulta (todas las evaluaciones del sistema)
        todas_evaluaciones = AsignacionEvaluacion.objects.select_related(
            'empleado_evaluado',
            'evaluador',
            'evaluacion',
            'evaluacion__tipo_evaluacion'
        ).order_by('-fecha_asignacion')
        
        # Obtener lista de empleados para filtro (empleados que tienen evaluaciones en cualquier estado)
        empleados_con_evaluaciones = Empleado.objects.filter(
            id__in=AsignacionEvaluacion.objects.values_list('empleado_evaluado_id', flat=True)
        ).distinct().order_by('apellidos', 'nombres')
        
        # Filtros opcionales
        estado_filtro = self.request.GET.get('estado')
        tipo_filtro = self.request.GET.get('tipo')
        buscar = self.request.GET.get('buscar')
        empleado_filtro = self.request.GET.get('empleado')
        
        # Limpiar valores None o vacíos
        estado_filtro = estado_filtro if estado_filtro and estado_filtro.strip() and estado_filtro != 'None' else None
        tipo_filtro = tipo_filtro if tipo_filtro and tipo_filtro.strip() and tipo_filtro != 'None' else None
        buscar = buscar if buscar and buscar.strip() and buscar != 'None' else None
        empleado_filtro = empleado_filtro if empleado_filtro and empleado_filtro.strip() and empleado_filtro != 'None' else None
        
        if estado_filtro:
            todas_evaluaciones = todas_evaluaciones.filter(estado=estado_filtro)
        
        if tipo_filtro:
            todas_evaluaciones = todas_evaluaciones.filter(evaluacion__tipo_evaluacion__codigo=tipo_filtro)
        
        if empleado_filtro:
            todas_evaluaciones = todas_evaluaciones.filter(empleado_evaluado__id=empleado_filtro)
            
        if buscar:
            todas_evaluaciones = todas_evaluaciones.filter(
                empleado_evaluado__nombres__icontains=buscar
            ) | todas_evaluaciones.filter(
                empleado_evaluado__apellidos__icontains=buscar
            )
        
        # Calcular conteos antes de convertir a listas
        total_pendientes = 0
        total_mis_evaluaciones = mis_evaluaciones.count()
        
        if hasattr(evaluaciones_pendientes, 'count'):
            total_pendientes = evaluaciones_pendientes.count()
        elif evaluaciones_pendientes:
            total_pendientes = len(evaluaciones_pendientes)
        
        context.update({
            'evaluaciones_pendientes': list(evaluaciones_pendientes[:5]) if evaluaciones_pendientes else [],
            'mis_evaluaciones': list(mis_evaluaciones[:5]),
            'todas_evaluaciones': todas_evaluaciones[:20],  # Mostrar primeras 20 para no sobrecargar
            'empleados_disponibles': empleados_con_evaluaciones,
            'total_evaluaciones': todas_evaluaciones.count(),
            'total_pendientes': total_pendientes,
            'total_mis_evaluaciones': total_mis_evaluaciones,
            'evaluaciones_completadas': evaluaciones_completadas_mes,
            'es_superusuario': usuario.is_superuser,
            'empleado_actual': empleado_usuario,
            # Filtros para el template
            'estado_filtro': estado_filtro,
            'tipo_filtro': tipo_filtro,
            'buscar': buscar,
            'empleado_filtro': empleado_filtro,
        })
        
        return context


class ListadoCompletoEvaluacionesView(LoginRequiredMixin, ListView):
    """Vista para mostrar el listado completo de evaluaciones con filtros avanzados"""
    template_name = 'evaluations/listado_completo.html'
    context_object_name = 'evaluaciones'
    paginate_by = 20
    
    def get_queryset(self):
        """Obtener todas las evaluaciones del sistema con filtros"""
        queryset = AsignacionEvaluacion.objects.select_related(
            'empleado_evaluado',
            'evaluador',
            'evaluacion',
            'evaluacion__tipo_evaluacion'
        ).order_by('-fecha_asignacion')
        
        # Aplicar filtros
        estado_filtro = self.request.GET.get('estado')
        tipo_filtro = self.request.GET.get('tipo')
        buscar = self.request.GET.get('buscar')
        empleado_filtro = self.request.GET.get('empleado')
        
        # Limpiar valores None o vacíos
        estado_filtro = estado_filtro if estado_filtro and estado_filtro.strip() and estado_filtro != 'None' else None
        tipo_filtro = tipo_filtro if tipo_filtro and tipo_filtro.strip() and tipo_filtro != 'None' else None
        buscar = buscar if buscar and buscar.strip() and buscar != 'None' else None
        empleado_filtro = empleado_filtro if empleado_filtro and empleado_filtro.strip() and empleado_filtro != 'None' else None
        
        if estado_filtro:
            queryset = queryset.filter(estado=estado_filtro)
        
        if tipo_filtro:
            queryset = queryset.filter(evaluacion__tipo_evaluacion__codigo=tipo_filtro)
        
        if empleado_filtro:
            queryset = queryset.filter(empleado_evaluado__id=empleado_filtro)
            
        if buscar:
            queryset = queryset.filter(
                empleado_evaluado__nombres__icontains=buscar
            ) | queryset.filter(
                empleado_evaluado__apellidos__icontains=buscar
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        
        try:
            empleado_usuario = Empleado.objects.get(usuario=usuario)
        except Empleado.DoesNotExist:
            empleado_usuario = None
        
        # Obtener filtros para el contexto
        estado_filtro = self.request.GET.get('estado')
        tipo_filtro = self.request.GET.get('tipo')
        buscar = self.request.GET.get('buscar')
        empleado_filtro = self.request.GET.get('empleado')
        
        # Limpiar valores None o vacíos para el contexto
        estado_filtro = estado_filtro if estado_filtro and estado_filtro.strip() and estado_filtro != 'None' else None
        tipo_filtro = tipo_filtro if tipo_filtro and tipo_filtro.strip() and tipo_filtro != 'None' else None
        buscar = buscar if buscar and buscar.strip() and buscar != 'None' else None
        empleado_filtro = empleado_filtro if empleado_filtro and empleado_filtro.strip() and empleado_filtro != 'None' else None
        
        # Obtener lista de empleados para filtro (empleados que tienen evaluaciones en cualquier estado)
        empleados_con_evaluaciones = Empleado.objects.filter(
            id__in=AsignacionEvaluacion.objects.values_list('empleado_evaluado_id', flat=True)
        ).distinct().order_by('apellidos', 'nombres')
        
        # Estadísticas generales
        total_evaluaciones = self.get_queryset().count()
        evaluaciones_completadas = AsignacionEvaluacion.objects.filter(estado='completada').count()
        evaluaciones_pendientes = AsignacionEvaluacion.objects.filter(estado__in=['pendiente', 'en_progreso']).count()
        evaluaciones_aprobadas = AsignacionEvaluacion.objects.filter(estado='aprobada').count()
        
        context.update({
            'total_evaluaciones': total_evaluaciones,
            'evaluaciones_completadas': evaluaciones_completadas,
            'evaluaciones_pendientes': evaluaciones_pendientes,
            'evaluaciones_aprobadas': evaluaciones_aprobadas,
            'empleados_disponibles': empleados_con_evaluaciones,
            'es_superusuario': usuario.is_superuser,
            'empleado_actual': empleado_usuario,
            # Filtros para el template
            'estado_filtro': estado_filtro,
            'tipo_filtro': tipo_filtro,
            'buscar': buscar,
            'empleado_filtro': empleado_filtro,
        })
        
        return context


class MisEvaluacionesPendientesView(LoginRequiredMixin, ListView):
    """Lista todas las evaluaciones donde el usuario es evaluador (jefe inmediato)"""
    template_name = 'evaluations/supervisor/pendientes.html'
    context_object_name = 'evaluaciones'
    paginate_by = 10

    def get_queryset(self):
        try:
            # Obtener el empleado del usuario actual
            empleado_usuario = Empleado.objects.get(usuario=self.request.user)
            return AsignacionEvaluacion.objects.filter(
                evaluador=empleado_usuario,
                estado__in=['pendiente', 'en_progreso']
            ).select_related(
                'empleado_evaluado',
                'evaluacion',
                'evaluacion__tipo_evaluacion'
            ).order_by('-fecha_asignacion')
        except Empleado.DoesNotExist:
            # Si el usuario no tiene empleado asociado, devolver queryset vacío
            return AsignacionEvaluacion.objects.none()


class AdminTodasPendientesView(LoginRequiredMixin, ListView):
    """
    Vista administrativa: muestra TODAS las evaluaciones pendientes del sistema.
    Solo accesible para superusuarios y usuarios con permisos de administración.
    """
    template_name = 'evaluations/admin/todas_pendientes.html'
    context_object_name = 'evaluaciones'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Verificar permisos de administrador
        if not (request.user.is_superuser or request.user.has_perm('evaluations.change_asignacionevaluacion')):
            messages.error(request, 'No tiene permisos para acceder a esta vista.')
            return redirect('evaluations:index')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Obtener TODAS las evaluaciones pendientes del sistema"""
        return AsignacionEvaluacion.objects.filter(
            estado__in=['pendiente', 'en_progreso']
        ).select_related(
            'empleado_evaluado',
            'evaluacion',
            'evaluacion__tipo_evaluacion',
            'evaluador'
        ).order_by('-fecha_asignacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas
        queryset = self.get_queryset()
        total_pendientes = queryset.count()
        sin_evaluador = queryset.filter(evaluador__isnull=True).count()
        en_progreso = queryset.filter(estado='en_progreso').count()

        # Agrupar por tipo de evaluación
        from django.db.models import Count
        por_tipo = queryset.values(
            'evaluacion__tipo_evaluacion__nombre'
        ).annotate(total=Count('id')).order_by('-total')

        # Evaluaciones con vencimiento próximo (7 días)
        from datetime import timedelta
        fecha_limite = timezone.now().date() + timedelta(days=7)
        proximas_vencer = queryset.filter(
            fecha_vencimiento__lte=fecha_limite
        ).count()

        context.update({
            'total_pendientes': total_pendientes,
            'sin_evaluador': sin_evaluador,
            'en_progreso': en_progreso,
            'por_tipo': por_tipo,
            'proximas_vencer': proximas_vencer,
            'es_vista_admin': True,
        })
        return context


class EvaluacionHistorialView(LoginRequiredMixin, ListView):
    """Historial de evaluaciones del usuario como empleado"""
    template_name = 'evaluations/empleado/historial.html'
    context_object_name = 'evaluaciones'
    paginate_by = 10
    
    def get_queryset(self):
        return AsignacionEvaluacion.objects.filter(
            empleado_evaluado__usuario=self.request.user
        ).select_related(
            'evaluador',
            'evaluacion',
            'evaluacion__tipo_evaluacion',
            'resultadoevaluacion'
        ).order_by('-fecha_asignacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evaluaciones = self.get_queryset()
        
        # Calcular estadísticas
        total_evaluaciones = evaluaciones.count()
        completadas = evaluaciones.filter(estado='completada').count()
        pendientes = evaluaciones.filter(estado__in=['pendiente', 'en_progreso']).count()
        
        # Calcular promedio general
        resultados = ResultadoEvaluacion.objects.filter(
            asignacion__empleado_evaluado__usuario=self.request.user
        )
        if resultados.exists():
            promedio = sum(r.puntaje_final for r in resultados) / resultados.count()
        else:
            promedio = 0.0
        
        context.update({
            'evaluaciones_completadas': completadas,
            'evaluaciones_pendientes': pendientes,
            'promedio_general': promedio,
        })
        
        return context


@login_required
def completar_evaluacion(request, asignacion_id):
    """Vista para completar una evaluación asignada"""
    try:
        # Obtener el empleado del usuario actual
        empleado_usuario = Empleado.objects.get(usuario=request.user)
        
        asignacion = get_object_or_404(
            AsignacionEvaluacion.objects.select_related(
                'empleado_evaluado',
                'evaluacion',
                'evaluacion__tipo_evaluacion',
                'evaluador'
            ),
            pk=asignacion_id,
            evaluador=empleado_usuario
        )
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes permisos para completar evaluaciones.')
        return redirect('evaluations:index')
    
    # Verificar que la evaluación esté en estado válido
    if asignacion.estado == 'completada':
        messages.warning(request, 'Esta evaluación ya ha sido completada.')
        return redirect('evaluations:supervisor_pendientes')
    
    # Obtener preguntas de la evaluación
    preguntas = PreguntaEvaluacion.objects.filter(
        evaluacion=asignacion.evaluacion
    ).prefetch_related('opcionevaluacion_set').order_by('orden')
    
    # Obtener respuestas existentes (si las hay)
    respuestas_existentes = {}
    if asignacion.estado == 'en_progreso':
        respuestas = RespuestaEvaluacion.objects.filter(
            asignacion=asignacion
        ).select_related('opcion_seleccionada')
        respuestas_existentes = {
            respuesta.pregunta_id: respuesta for respuesta in respuestas
        }
    
    if request.method == 'POST':
        return _procesar_respuestas_evaluacion(request, asignacion, preguntas)
    
    # Buscar plan de mejora generado para esta asignación (si existe)
    plan_mejora = None
    try:
        from .models import PlanMejoraPredefinido
        plan_mejora = PlanMejoraPredefinido.objects.get(asignacion_evaluacion=asignacion)
    except Exception:
        plan_mejora = None

    context = {
        'asignacion': asignacion,
        'preguntas': preguntas,
        'respuestas_existentes': respuestas_existentes,
        'empleado': asignacion.empleado_evaluado,
        'evaluacion': asignacion.evaluacion,
        'plan_mejora': plan_mejora,
    }
    
    return render(request, 'evaluations/supervisor/completar.html', context)


def _procesar_respuestas_evaluacion(request, asignacion, preguntas):
    """Procesa las respuestas de una evaluación"""
    try:
        with transaction.atomic():
            # Marcar como en progreso si es primera vez y asignar evaluador
            if asignacion.estado == 'pendiente':
                asignacion.estado = 'en_progreso'
                # Asignar el evaluador (usuario logueado)
                if hasattr(request.user, 'empleado'):
                    asignacion.evaluador = request.user.empleado
                asignacion.save()
            
            respuestas_validas = 0
            total_preguntas_obligatorias = preguntas.filter(obligatoria=True).count()
            
            # Procesar cada pregunta
            for pregunta in preguntas:
                campo_respuesta = f'pregunta_{pregunta.id}'
                campo_comentario = f'comentario_{pregunta.id}'
                
                if campo_respuesta in request.POST:
                    valor_respuesta = request.POST[campo_respuesta]
                    comentario = request.POST.get(campo_comentario, '').strip()
                    
                    if valor_respuesta:  # Si hay respuesta
                        # Obtener o crear la respuesta
                        respuesta, created = RespuestaEvaluacion.objects.get_or_create(
                            asignacion=asignacion,
                            pregunta=pregunta,
                            defaults={}
                        )
                        
                        # Actualizar respuesta
                        if pregunta.tipo_pregunta.codigo in ['ESCALA_5', 'ESCALA_3', 'SI_NO', 'MULTIPLE']:
                            # Respuesta con opción seleccionada
                            opcion = get_object_or_404(
                                OpcionEvaluacion, 
                                id=valor_respuesta,
                                pregunta=pregunta
                            )
                            respuesta.opcion_seleccionada = opcion
                            respuesta.puntaje_obtenido = opcion.valor_numerico
                        else:
                            # Respuesta de texto libre
                            respuesta.respuesta_texto = valor_respuesta
                        
                        respuesta.comentarios_evaluador = comentario
                        respuesta.save()
                        
                        if pregunta.obligatoria:
                            respuestas_validas += 1
            
            # Completar evaluación
            if respuestas_validas < total_preguntas_obligatorias:
                messages.error(
                    request, 
                    f'Faltan {total_preguntas_obligatorias - respuestas_validas} '
                    'respuestas obligatorias para completar la evaluación.'
                )
            else:
                # Finalizar evaluación
                asignacion.estado = 'completada'
                asignacion.fecha_completada = timezone.now()
                asignacion.estado_aprobacion = 'pendiente_aprobacion'
                asignacion.save()
                
                # Calcular resultados automáticamente
                _calcular_resultado_evaluacion(asignacion)
                
                # Generar plan de mejora automáticamente al completar la evaluación
                # NO generar plan si el puntaje es 21/21 (desempeño excelente)
                try:
                    from .models import PlanMejoraPredefinido
                    from .utils.respuestas_predefinidas import generar_plan_automatico

                    # Solo si no existe ya un plan para esta asignación
                    if not PlanMejoraPredefinido.objects.filter(asignacion_evaluacion=asignacion).exists():
                        # Verificar el puntaje total
                        if asignacion.puntaje_total and asignacion.puntaje_total >= 21:
                            # Puntaje máximo - No requiere plan de mejora
                            import logging
                            logging.info(f'Empleado {asignacion.empleado_evaluado.nombre_completo} obtuvo puntaje máximo (21/21). No se genera plan de mejora.')
                        else:
                            # Generar plan de mejora normal
                            respuestas = RespuestaEvaluacion.objects.filter(
                                asignacion=asignacion
                            ).select_related('pregunta', 'opcion_seleccionada')
                            respuestas_para_plan = respuestas.filter(opcion_seleccionada__valor_numerico__in=[1, 2, 3])
                            plan_mejora_texto = generar_plan_automatico(respuestas_para_plan)
                            PlanMejoraPredefinido.objects.create(
                                asignacion_evaluacion=asignacion,
                                plan_mejora=plan_mejora_texto,
                                generado_por=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                                estado='pendiente_aprobacion'
                            )
                except Exception as e:
                    # No interrumpir el flujo si falla la generación automática
                    import logging
                    logging.exception('Error generando plan de mejora automático: %s', e)
                
                messages.success(
                    request, 
                    f'Evaluación de {asignacion.empleado_evaluado.nombre_completo} '
                    'completada exitosamente. Los resultados preliminares han sido '
                    'enviados al empleado y están pendientes de aprobación administrativa.'
                )
                
                return redirect('evaluations:supervisor_pendientes')
            
    except Exception as e:
        messages.error(request, f'Error al guardar la evaluación: {str(e)}')
    
    # Redirigir de vuelta al formulario
    return redirect('evaluations:completar', asignacion_id=asignacion.id)


def _calcular_resultado_evaluacion(asignacion):
    """Calcula el resultado final de una evaluación"""
    try:
        respuestas = RespuestaEvaluacion.objects.filter(
            asignacion=asignacion
        ).select_related('pregunta', 'opcion_seleccionada')
        
        if not respuestas.exists():
            return
        
        puntaje_acumulado = Decimal('0.00')
        total_respuestas = respuestas.count()
        
        for respuesta in respuestas:
            if respuesta.opcion_seleccionada:
                valor_respuesta = Decimal(str(respuesta.opcion_seleccionada.valor_numerico))
            elif respuesta.puntaje_obtenido:
                valor_respuesta = Decimal(str(respuesta.puntaje_obtenido))
            else:
                continue
            
            puntaje_acumulado += valor_respuesta
        
        # Calcular puntaje final
        if total_respuestas > 0:
            # Para escalas 1-3, el puntaje máximo es 3 * número de preguntas
            puntaje_maximo = Decimal('3') * total_respuestas
            puntaje_final = (puntaje_acumulado / puntaje_maximo) * 5  # Convertir a escala 1-5
            porcentaje = (puntaje_acumulado / puntaje_maximo) * 100
        else:
            puntaje_final = Decimal('0.00')
            porcentaje = Decimal('0.00')
        
        # Determinar clasificación basada en puntaje total (umbral de aprobación: 14 puntos)
        if puntaje_acumulado >= 20:  # Puntaje excelente (cerca del máximo 21)
            clasificacion = 'excelente'
        elif puntaje_acumulado >= 18:  # Puntaje sobresaliente
            clasificacion = 'sobresaliente'
        elif puntaje_acumulado >= 14:  # Puntaje satisfactorio (aprobado)
            clasificacion = 'satisfactorio'
        elif puntaje_acumulado >= 10:  # Puntaje mejorable (reprobado)
            clasificacion = 'mejorable'
        else:  # Puntaje insatisfactorio (muy reprobado)
            clasificacion = 'insatisfactorio'
        
        # Generar aspectos positivos y áreas de mejora basados en el puntaje total
        if puntaje_acumulado >= 18:  # Excelente/Sobresaliente
            aspectos_positivos = "• Demuestra excelente desempeño en todas las áreas evaluadas\n• Supera consistentemente las expectativas\n• Muestra iniciativa y liderazgo"
            areas_mejora = "• Continuar desarrollando habilidades de liderazgo\n• Compartir conocimientos con otros miembros del equipo\n• Asumir mayores responsabilidades"
        elif puntaje_acumulado >= 14:  # Satisfactorio (aprobado)
            aspectos_positivos = "• Cumple satisfactoriamente con las responsabilidades asignadas\n• Demuestra competencia técnica adecuada\n• Muestra actitud positiva hacia el trabajo"
            areas_mejora = "• Mejorar la consistencia en el desempeño diario\n• Desarrollar mayor autonomía en la toma de decisiones\n• Fortalecer habilidades de comunicación"
        else:  # Reprobado (puntaje ≤ 13)
            aspectos_positivos = "• Muestra disposición para aprender y mejorar\n• Asiste puntualmente a sus labores\n• Demuestra interés en el desarrollo profesional"
            areas_mejora = "• Requiere capacitación específica en competencias técnicas\n• Necesita mayor supervisión y acompañamiento\n• Desarrollar habilidades básicas del puesto"
        
        # Crear o actualizar resultado
        resultado, created = ResultadoEvaluacion.objects.get_or_create(
            asignacion=asignacion,
            defaults={
                'puntaje_final': puntaje_final,
                'porcentaje_obtenido': porcentaje,
                'nivel_desempeño': clasificacion,
                'aspectos_positivos': aspectos_positivos,
                'areas_mejora': areas_mejora,
                'comentarios_generales': f'Evaluación completada con {porcentaje:.1f}% de cumplimiento.',
                'recomendaciones': 'Se recomienda que el empleado continúe en la empresa.' if puntaje_acumulado >= 14 else 'Se requiere plan de mejora inmediato.',
                'generado_por': asignacion.evaluador.usuario if asignacion.evaluador and asignacion.evaluador.usuario else None,
            }
        )
        
        if not created:
            resultado.puntaje_final = puntaje_final
            resultado.porcentaje_obtenido = porcentaje
            resultado.nivel_desempeño = clasificacion
            resultado.aspectos_positivos = aspectos_positivos
            resultado.areas_mejora = areas_mejora
            resultado.save()
        
        # Actualizar también los campos en la asignación para compatibilidad con templates existentes
        asignacion.puntaje_total = puntaje_acumulado
        asignacion.porcentaje_completado = porcentaje
        asignacion.save()
            
    except Exception as e:
        # Log del error pero no fallar la operación
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error calculando resultado de evaluación {asignacion.id}: {e}")


# =============================================================================
# VISTAS DE APROBACIÓN ADMINISTRATIVA
# =============================================================================

class EvaluacionesPendientesAprobacionView(LoginRequiredMixin, ListView):
    """
    Vista para administradores: Planes de Mejora pendientes de aprobación.
    El flujo ahora va directo: Evaluación completada → Plan de Mejora generado → Aprobación del Plan
    """
    template_name = 'evaluations/admin/pendientes_aprobacion.html'
    context_object_name = 'planes_pendientes'
    paginate_by = 20

    def get_queryset(self):
        # Solo para administradores y usuarios con permisos específicos
        if not (self.request.user.is_superuser or self.request.user.has_perm('evaluations.change_asignacionevaluacion')):
            from .models import PlanMejoraPredefinido
            return PlanMejoraPredefinido.objects.none()

        from .models import PlanMejoraPredefinido
        return PlanMejoraPredefinido.objects.filter(
            estado='pendiente_aprobacion'
        ).select_related(
            'asignacion_evaluacion__empleado_evaluado',
            'asignacion_evaluacion__evaluacion',
            'asignacion_evaluacion__evaluador'
        ).order_by('-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas de planes
        queryset = self.get_queryset()
        planes_aceptados = queryset.filter(aceptado_por_empleado=True).count()

        # Contar planes sin aceptar, diferenciando reprobados (puntaje < 14)
        planes_sin_aceptar = 0
        planes_reprobados = 0

        for plan in queryset.filter(aceptado_por_empleado=False):
            if plan.asignacion_evaluacion.puntaje_total and plan.asignacion_evaluacion.puntaje_total < 14:
                planes_reprobados += 1
            else:
                planes_sin_aceptar += 1

        context.update({
            'planes_aceptados': planes_aceptados,
            'planes_sin_aceptar': planes_sin_aceptar,
            'planes_reprobados': planes_reprobados,
        })

        return context


@login_required
def aprobar_evaluacion(request, asignacion_id):
    """Aprobar una evaluación completada"""
    if not (request.user.is_superuser or request.user.has_perm('evaluations.change_asignacionevaluacion')):
        messages.error(request, 'No tiene permisos para aprobar evaluaciones.')
        return redirect('evaluations:index')
    
    asignacion = get_object_or_404(AsignacionEvaluacion, pk=asignacion_id)
    
    if asignacion.estado != 'completada':
        messages.error(request, 'Solo se pueden aprobar evaluaciones completadas.')
        return redirect('evaluations:admin_pendientes_aprobacion')
    
    # Validar que el empleado haya aceptado el plan de mejora, excepto si fue reprobado
    evaluacion_reprobada = asignacion.puntaje_total and asignacion.puntaje_total < 14
    
    if not evaluacion_reprobada:
        # Verificar si tiene plan de mejora generado
        try:
            from .models import PlanMejoraPredefinido
            plan_mejora = PlanMejoraPredefinido.objects.get(asignacion_evaluacion=asignacion)
            
            if not plan_mejora.aceptado_por_empleado:
                messages.error(
                    request, 
                    f'No se puede aprobar la evaluación de {asignacion.empleado_evaluado.nombre_completo}. '
                    'El empleado debe revisar y aceptar su plan de mejora antes de que la evaluación '
                    'pueda ser aprobada administrativamente.'
                )
                return redirect('evaluations:admin_pendientes_aprobacion')
        except PlanMejoraPredefinido.DoesNotExist:
            # Si no tiene plan de mejora, usar la validación anterior como fallback
            if not (asignacion.observaciones and '[ACEPTADO_EMPLEADO:' in asignacion.observaciones):
                messages.error(
                    request, 
                    f'No se puede aprobar la evaluación de {asignacion.empleado_evaluado.nombre_completo}. '
                    'El empleado debe ver y aceptar primero los resultados desde su perfil en "Mi Actividad Reciente" '
                    'antes de que la evaluación pueda ser aprobada administrativamente.'
                )
                return redirect('evaluations:admin_pendientes_aprobacion')
    
    if request.method == 'POST':
        decision = request.POST.get('decision')  # 'aprobada' o 'desaprobada'
        comentarios = request.POST.get('comentarios_aprobacion', '')
        recomendacion = request.POST.get('recomendacion_continuidad', '')
        
        with transaction.atomic():
            asignacion.estado_aprobacion = decision
            asignacion.aprobada_por = request.user
            asignacion.fecha_aprobacion = date.today()
            asignacion.comentarios_aprobacion = comentarios
            asignacion.recomendacion_continuidad = recomendacion
            
            # Generar aspectos de mejora automáticamente para período de prueba
            if asignacion.evaluacion.tipo_evaluacion.codigo == 'PERIODO_PRUEBA':
                asignacion.aspectos_mejora_generados = _generar_aspectos_mejora_periodo_prueba(asignacion)
            
            asignacion.save()
            
            # Mensaje de éxito
            accion = 'aprobada' if decision == 'aprobada' else 'desaprobada'
            messages.success(
                request, 
                f'Evaluación {accion} exitosamente para {asignacion.empleado_evaluado.nombre_completo}.'
            )
            
            # TODO: Enviar notificación al empleado y supervisor
            
        return redirect('evaluations:admin_pendientes_aprobacion')
    
    # GET - Mostrar formulario de aprobación
    
    # Obtener o calcular resultado de evaluación
    try:
        resultado = ResultadoEvaluacion.objects.get(asignacion=asignacion)
    except ResultadoEvaluacion.DoesNotExist:
        # Si no existe resultado, calcularlo
        _calcular_resultado_evaluacion(asignacion)
        try:
            resultado = ResultadoEvaluacion.objects.get(asignacion=asignacion)
        except ResultadoEvaluacion.DoesNotExist:
            resultado = None
    
    context = {
        'asignacion': asignacion,
        'resultado': resultado,
        'respuestas': RespuestaEvaluacion.objects.filter(asignacion=asignacion).select_related('pregunta', 'opcion_seleccionada'),
        'es_periodo_prueba': asignacion.evaluacion.tipo_evaluacion.codigo == 'PERIODO_PRUEBA',
    }
    
    return render(request, 'evaluations/admin/aprobar_evaluacion.html', context)


def _generar_aspectos_mejora_periodo_prueba(asignacion):
    """Generar aspectos de mejora automáticamente para evaluaciones de período de prueba"""
    respuestas = RespuestaEvaluacion.objects.filter(
        asignacion=asignacion,
        puntaje_obtenido__lt=3  # Respuestas con puntaje menor a 3 (No cumple totalmente)
    ).select_related('pregunta')
    
    aspectos_mejora = []
    
    for respuesta in respuestas:
        categoria = respuesta.pregunta.categoria
        pregunta = respuesta.pregunta.pregunta
        
        # Generar recomendación basada en la pregunta
        if 'Trabajo en equipo' in pregunta:
            aspectos_mejora.append('• Fortalecer habilidades de colaboración y comunicación en equipo')
        elif 'Compromiso' in pregunta:
            aspectos_mejora.append('• Desarrollar mayor compromiso y proactividad hacia los objetivos organizacionales')
        elif 'Comunicación' in pregunta:
            aspectos_mejora.append('• Mejorar habilidades de comunicación efectiva y escucha activa')
        elif 'Atención al detalle' in pregunta:
            aspectos_mejora.append('• Incrementar la atención al detalle y precisión en las tareas asignadas')
        elif 'Cumplimiento' in pregunta:
            aspectos_mejora.append('• Reforzar el cumplimiento de normas, procedimientos y estándares de la empresa')
        elif 'Actitud' in pregunta:
            aspectos_mejora.append('• Mantener una actitud más positiva y constructiva hacia el trabajo')
        elif 'Calidad' in pregunta:
            aspectos_mejora.append('• Mejorar la calidad y precisión en la ejecución de trabajos asignados')
        else:
            aspectos_mejora.append(f'• Fortalecer competencias en: {categoria}')
    
    if not aspectos_mejora:
        return 'El empleado cumple satisfactoriamente con todos los aspectos evaluados.'
    
    return '\n'.join(aspectos_mejora)


@login_required 
def revisar_evaluacion(request, asignacion_id):
    """Marcar una evaluación para revisión (requiere cambios)"""
    if not (request.user.is_superuser or request.user.has_perm('evaluations.change_asignacionevaluacion')):
        messages.error(request, 'No tiene permisos para revisar evaluaciones.')
        return redirect('evaluations:index')
    
    asignacion = get_object_or_404(AsignacionEvaluacion, pk=asignacion_id)
    
    if request.method == 'POST':
        comentarios = request.POST.get('comentarios_revision', '')
        
        with transaction.atomic():
            asignacion.estado_aprobacion = 'requiere_revision'
            asignacion.aprobada_por = request.user
            asignacion.fecha_aprobacion = date.today()
            asignacion.comentarios_aprobacion = comentarios
            asignacion.save()
            
            messages.warning(
                request, 
                f'Evaluación marcada para revisión. Se notificará al evaluador.'
            )
            
            # TODO: Enviar notificación al evaluador
        
        return redirect('evaluations:admin_pendientes_aprobacion')
    
    return redirect('evaluations:aprobar_evaluacion', asignacion_id=asignacion_id)



@login_required
def ver_resultados_evaluacion(request, asignacion_id):
    """
    Vista de redirección: Los resultados de evaluación ahora son los planes de mejora.
    Esta vista redirige automáticamente al plan de mejora del empleado.
    """
    try:
        asignacion = AsignacionEvaluacion.objects.select_related(
            'empleado_evaluado', 'evaluacion', 'evaluador'
        ).get(pk=asignacion_id)
        
        # Verificar que el usuario puede ver estos resultados
        if not (request.user.empleado == asignacion.empleado_evaluado or 
                request.user.is_superuser or 
                request.user.has_perm('evaluations.view_asignacionevaluacion')):
            messages.error(request, 'No tiene permisos para ver estos resultados.')
            return redirect('evaluations:index')
        
        # Verificar que la evaluación esté completada
        if asignacion.estado != 'completada':
            messages.warning(request, 'La evaluación aún no está completada.')
            return redirect('evaluations:index')
        
        # Buscar el plan de mejora generado
        from .models import PlanMejoraPredefinido
        try:
            plan_mejora = PlanMejoraPredefinido.objects.get(asignacion_evaluacion=asignacion)
            # Redirigir directamente al plan de mejora
            return redirect('evaluations:ver_plan_mejora_empleado', plan_id=plan_mejora.id)
        except PlanMejoraPredefinido.DoesNotExist:
            # Si no existe plan, mostrar mensaje informativo
            messages.info(request, 'Su plan de mejora está siendo generado. Se creará automáticamente cuando la evaluación esté completamente procesada.')
            return redirect('evaluations:index')
    
    except AsignacionEvaluacion.DoesNotExist:
        messages.error(request, 'Evaluación no encontrada.')
        return redirect('evaluations:index')
    except Exception as e:
        messages.error(request, f'Error al acceder a los resultados: {str(e)}')
        return redirect('evaluations:index')


@login_required
def aceptar_resultados_evaluacion(request, asignacion_id):
    """
    Vista de redirección: La aceptación se realiza ahora en el plan de mejora.
    Esta vista redirige al plan de mejora donde el empleado puede aceptarlo.
    """
    try:
        asignacion = AsignacionEvaluacion.objects.get(pk=asignacion_id)
        
        # Verificar que es el empleado evaluado
        if request.user.empleado != asignacion.empleado_evaluado:
            messages.error(request, 'No puede acceder a los resultados de otra persona.')
            return redirect('evaluations:index')
        
        # Redirigir al plan de mejora donde puede aceptar
        from .models import PlanMejoraPredefinido
        try:
            plan_mejora = PlanMejoraPredefinido.objects.get(asignacion_evaluacion=asignacion)
            return redirect('evaluations:ver_plan_mejora_empleado', plan_id=plan_mejora.id)
        except PlanMejoraPredefinido.DoesNotExist:
            messages.info(request, 'Su plan de mejora está siendo generado.')
            return redirect('evaluations:index')
        
    except AsignacionEvaluacion.DoesNotExist:
        messages.error(request, 'Evaluación no encontrada.')
        return redirect('evaluations:index')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('evaluations:index')


# ===================== VISTAS PARA PLANES PREDEFINIDOS =====================

@login_required
def generar_plan_predefinido(request, asignacion_id):
    """
    Genera automáticamente un plan de mejora basado en respuestas predefinidas
    """
    from .models import PlanMejoraPredefinido
    from .utils.respuestas_predefinidas import generar_plan_automatico
    
    try:
        asignacion = get_object_or_404(AsignacionEvaluacion, id=asignacion_id)
        
        # Verificar permisos - solo el evaluador puede generar el plan
        try:
            empleado_usuario = Empleado.objects.get(usuario=request.user)
        except Empleado.DoesNotExist:
            # Usuario admin puede generar planes
            if not request.user.is_staff:
                messages.error(request, 'No tiene permisos para generar planes de mejora.')
                return redirect('evaluations:admin_pendientes_aprobacion')
        else:
            # Verificar que es el evaluador o jefe inmediato
            if (asignacion.evaluador != empleado_usuario and 
                asignacion.empleado_evaluado.jefe_inmediato != empleado_usuario and
                not request.user.is_staff):
                messages.error(request, 'Solo el evaluador o jefe inmediato puede generar el plan.')
                return redirect('evaluations:admin_pendientes_aprobacion')
        
        # Verificar que la evaluación esté completada y aprobada
        if asignacion.estado != 'completada' or asignacion.estado_aprobacion != 'aprobada':
            messages.error(request, 'La evaluación debe estar completada y aprobada para generar el plan.')
            return redirect('evaluations:admin_pendientes_aprobacion')
        
        # Verificar que no exista ya un plan
        if PlanMejoraPredefinido.objects.filter(asignacion_evaluacion=asignacion).exists():
            messages.error(request, 'Ya existe un plan de mejora para esta evaluación.')
            return redirect('evaluations:admin_pendientes_aprobacion')
        
        if request.method == 'POST':
            # Obtener todas las respuestas de la evaluación
            respuestas = RespuestaEvaluacion.objects.filter(
                asignacion=asignacion
            ).select_related('pregunta', 'opcion_seleccionada')
            
            # Filtrar solo las respuestas que requieren plan (valores 1, 2, 3)
            respuestas_para_plan = respuestas.filter(opcion_seleccionada__valor_numerico__in=[1, 2, 3])
            
            # Generar el plan automáticamente
            plan_mejora_texto = generar_plan_automatico(respuestas_para_plan)
            
            # Crear el plan predefinido
            plan_mejora = PlanMejoraPredefinido.objects.create(
                asignacion_evaluacion=asignacion,
                plan_mejora=plan_mejora_texto,
                generado_por=request.user,
                estado='pendiente_aprobacion'
            )
            
            messages.success(request, 'Plan de mejora generado exitosamente. Está pendiente de aprobación.')
            return redirect('evaluations:revisar_plan_predefinido', plan_id=plan_mejora.id)
        
        # GET - Mostrar formulario de confirmación
        # Obtener respuestas para preview
        respuestas = RespuestaEvaluacion.objects.filter(
            asignacion=asignacion
        ).select_related('pregunta', 'opcion_seleccionada')
        
        # Filtrar solo las respuestas que requieren plan (valores 1, 2, 3)
        respuestas_para_plan = respuestas.filter(opcion_seleccionada__valor_numerico__in=[1, 2, 3])
        
        # Generar preview del plan
        plan_preview = generar_plan_automatico(respuestas_para_plan)
        
        return render(request, 'evaluations/admin/generar_plan_predefinido.html', {
            'asignacion': asignacion,
            'plan_preview': plan_preview,
            'respuestas': respuestas
        })
        
    except Exception as e:
        messages.error(request, f'Error al generar el plan: {str(e)}')
        return redirect('evaluations:admin_pendientes_aprobacion')


@login_required
def revisar_plan_predefinido(request, plan_id):
    """
    Revisar y aprobar/rechazar un plan de mejora predefinido
    """
    from .models import PlanMejoraPredefinido, SeguimientoBimensual
    from .utils.respuestas_predefinidas import crear_seguimientos_bimensuales
    
    try:
        plan = get_object_or_404(PlanMejoraPredefinido, id=plan_id)
        
        # Verificar permisos - solo evaluador/jefe inmediato/admin
        try:
            empleado_usuario = Empleado.objects.get(usuario=request.user)
        except Empleado.DoesNotExist:
            # Usuario admin puede revisar
            if not request.user.is_staff:
                messages.error(request, 'No tiene permisos para revisar este plan.')
                return redirect('evaluations:admin_pendientes_aprobacion')
        else:
            if (plan.asignacion_evaluacion.evaluador != empleado_usuario and 
                plan.asignacion_evaluacion.empleado_evaluado.jefe_inmediato != empleado_usuario and
                not request.user.is_staff):
                messages.error(request, 'No tiene permisos para revisar este plan.')
                return redirect('evaluations:admin_pendientes_aprobacion')
        
        if request.method == 'POST':
            accion = request.POST.get('accion')
            comentarios = request.POST.get('comentarios_aprobacion', '').strip()
            
            with transaction.atomic():
                if accion == 'aprobar':
                    plan.estado = 'aprobado'
                    plan.fecha_aprobacion = timezone.now()
                    plan.aprobado_por = request.user
                    plan.comentarios_aprobacion = comentarios
                    plan.save()

                    # Solo crear seguimientos si el puntaje no es el máximo (21)
                    # Un puntaje de 21 indica desempeño excelente sin necesidad de seguimiento
                    if plan.asignacion_evaluacion.puntaje_total < 21:
                        # Crear seguimientos bimensuales automáticamente
                        crear_seguimientos_bimensuales(plan)

                        # Cambiar estado del plan a 'en_seguimiento'
                        plan.estado = 'en_seguimiento'
                        plan.save()

                        messages.success(request, 'Plan aprobado exitosamente. Se han creado los seguimientos bimensuales automáticamente.')
                    else:
                        # Puntaje máximo - No requiere seguimiento
                        plan.estado = 'completado'
                        plan.save()

                        messages.success(request, 'Plan aprobado exitosamente. El empleado obtuvo el puntaje máximo (21/21), por lo que no requiere seguimientos bimensuales.')
                    
                elif accion == 'rechazar':
                    plan.estado = 'rechazado'
                    plan.aprobado_por = request.user
                    plan.comentarios_aprobacion = comentarios or 'Plan rechazado sin comentarios específicos'
                    plan.save()
                    
                    messages.warning(request, 'Plan rechazado. Puede generar uno nuevo si es necesario.')
                
                return redirect('evaluations:admin_pendientes_aprobacion')
        
        return render(request, 'evaluations/admin/revisar_plan_predefinido.html', {
            'plan': plan
        })
        
    except Exception as e:
        messages.error(request, f'Error al revisar el plan: {str(e)}')
        return redirect('evaluations:admin_pendientes_aprobacion')


@login_required
def seguimientos_pendientes_supervisor(request):
    """
    Vista para que los supervisores vean todos sus seguimientos bimensuales pendientes
    Agrupados por jefe/evaluador
    """
    from .models import SeguimientoBimensual
    from datetime import date
    from collections import defaultdict

    try:
        # Obtener el empleado asociado al usuario
        es_admin = False
        try:
            empleado_usuario = Empleado.objects.get(usuario=request.user)
        except Empleado.DoesNotExist:
            # Si es admin, mostrar todos
            if request.user.is_staff:
                es_admin = True
                seguimientos = SeguimientoBimensual.objects.filter(
                    estado='pendiente'
                ).select_related(
                    'plan_mejora',
                    'plan_mejora__asignacion_evaluacion',
                    'plan_mejora__asignacion_evaluacion__empleado_evaluado',
                    'plan_mejora__asignacion_evaluacion__evaluador',
                    'plan_mejora__asignacion_evaluacion__evaluacion',
                    'plan_mejora__asignacion_evaluacion__evaluacion__tipo_evaluacion'
                ).prefetch_related(
                    'plan_mejora__asignacion_evaluacion__empleado_evaluado__historialcargo_set',
                    'plan_mejora__asignacion_evaluacion__empleado_evaluado__historialcargo_set__cargo',
                    'plan_mejora__asignacion_evaluacion__empleado_evaluado__historialcargo_set__cargo__area',
                    'plan_mejora__asignacion_evaluacion__evaluador__historialcargo_set',
                    'plan_mejora__asignacion_evaluacion__evaluador__historialcargo_set__cargo',
                    'plan_mejora__asignacion_evaluacion__evaluador__historialcargo_set__cargo__area'
                ).order_by('fecha_limite')
            else:
                messages.error(request, 'No tiene permisos para acceder a esta sección.')
                return redirect('evaluations:index')
        else:
            # Mostrar seguimientos donde el usuario es evaluador
            seguimientos = SeguimientoBimensual.objects.filter(
                plan_mejora__asignacion_evaluacion__evaluador=empleado_usuario,
                estado='pendiente'
            ).select_related(
                'plan_mejora',
                'plan_mejora__asignacion_evaluacion',
                'plan_mejora__asignacion_evaluacion__empleado_evaluado',
                'plan_mejora__asignacion_evaluacion__evaluador',
                'plan_mejora__asignacion_evaluacion__evaluacion',
                'plan_mejora__asignacion_evaluacion__evaluacion__tipo_evaluacion'
            ).prefetch_related(
                'plan_mejora__asignacion_evaluacion__empleado_evaluado__historialcargo_set',
                'plan_mejora__asignacion_evaluacion__empleado_evaluado__historialcargo_set__cargo',
                'plan_mejora__asignacion_evaluacion__empleado_evaluado__historialcargo_set__cargo__area',
                'plan_mejora__asignacion_evaluacion__evaluador__historialcargo_set',
                'plan_mejora__asignacion_evaluacion__evaluador__historialcargo_set__cargo',
                'plan_mejora__asignacion_evaluacion__evaluador__historialcargo_set__cargo__area'
            ).order_by('fecha_limite')

        # Marcar seguimientos vencidos
        hoy = date.today()
        for seguimiento in seguimientos:
            if seguimiento.fecha_limite < hoy:
                if seguimiento.estado == 'pendiente':
                    seguimiento.estado = 'atrasado'
                    seguimiento.save()

        # Agrupar seguimientos por jefe/evaluador
        seguimientos_por_jefe = defaultdict(list)
        for seguimiento in seguimientos:
            evaluador = seguimiento.plan_mejora.asignacion_evaluacion.evaluador
            seguimientos_por_jefe[evaluador].append(seguimiento)

        # Crear lista estructurada con estadísticas por jefe
        jefes_con_seguimientos = []
        for jefe, segs in seguimientos_por_jefe.items():
            # Agregar información de es_proximo y bloqueado a cada seguimiento
            segs_con_info = []
            for s in segs:
                # Crear un objeto wrapper con la información adicional
                s.es_proximo = (s.fecha_limite - hoy).days <= 7 and s.fecha_limite >= hoy and not s.esta_vencido

                # Verificar si este seguimiento está bloqueado (requiere completar anteriores)
                s.esta_bloqueado = False
                s.razon_bloqueo = None
                if s.estado == 'pendiente':
                    # Obtener todos los seguimientos del plan ordenados
                    segs_del_plan = SeguimientoBimensual.objects.filter(
                        plan_mejora=s.plan_mejora
                    ).order_by('numero_bimestre')

                    # Verificar si hay seguimientos anteriores sin completar
                    for seg_anterior in segs_del_plan:
                        if seg_anterior.numero_bimestre >= s.numero_bimestre:
                            break
                        if seg_anterior.estado != 'completado':
                            s.esta_bloqueado = True
                            s.razon_bloqueo = f'Debe completar primero el {seg_anterior.numero_bimestre}° bimestre'
                            break

                segs_con_info.append(s)

            # Ordenar seguimientos por fecha límite
            segs_ordenados = sorted(segs_con_info, key=lambda s: s.fecha_limite)

            # Calcular estadísticas para este jefe
            total_jefe = len(segs_ordenados)
            vencidos_jefe = sum(1 for s in segs_ordenados if s.esta_vencido)
            proximos_jefe = sum(1 for s in segs_ordenados if s.es_proximo)

            jefes_con_seguimientos.append({
                'jefe': jefe,
                'seguimientos': segs_ordenados,
                'total': total_jefe,
                'vencidos': vencidos_jefe,
                'proximos': proximos_jefe,
            })

        # Ordenar jefes por cantidad de vencidos (descendente), luego por total
        jefes_con_seguimientos.sort(key=lambda x: (-x['vencidos'], -x['total']))

        # Estadísticas globales
        total_pendientes = seguimientos.count()
        vencidos = sum(1 for s in seguimientos if s.fecha_limite < hoy)
        proximos = sum(1 for s in seguimientos if (s.fecha_limite - hoy).days <= 7 and s.fecha_limite >= hoy)

        return render(request, 'evaluations/supervisor/seguimientos_pendientes.html', {
            'jefes_con_seguimientos': jefes_con_seguimientos,
            'es_admin': es_admin,
            'total_pendientes': total_pendientes,
            'vencidos': vencidos,
            'proximos': proximos,
        })

    except Exception as e:
        messages.error(request, f'Error al cargar seguimientos: {str(e)}')
        return redirect('evaluations:index')


@login_required
def gestionar_seguimiento_bimensual(request, seguimiento_id):
    """
    Gestionar un seguimiento bimensual específico
    """
    from .models import SeguimientoBimensual, EvaluacionFinal
    from .utils.respuestas_predefinidas import puede_generar_evaluacion_final
    
    try:
        seguimiento = get_object_or_404(SeguimientoBimensual, id=seguimiento_id)
        plan = seguimiento.plan_mejora

        # Verificar permisos
        try:
            empleado_usuario = Empleado.objects.get(usuario=request.user)
        except Empleado.DoesNotExist:
            if not request.user.is_staff:
                messages.error(request, 'No tiene permisos para gestionar este seguimiento.')
                return redirect('evaluations:admin_pendientes_aprobacion')
        else:
            if (plan.asignacion_evaluacion.evaluador != empleado_usuario and
                plan.asignacion_evaluacion.empleado_evaluado.jefe_inmediato != empleado_usuario and
                not request.user.is_staff):
                messages.error(request, 'No tiene permisos para gestionar este seguimiento.')
                return redirect('evaluations:admin_pendientes_aprobacion')

        # Verificar que los seguimientos se completen en orden
        if seguimiento.estado == 'pendiente':
            # Obtener todos los seguimientos del plan ordenados por número de bimestre
            seguimientos_plan = SeguimientoBimensual.objects.filter(
                plan_mejora=plan
            ).order_by('numero_bimestre')

            # Verificar que todos los bimestres anteriores estén completados
            for seg_anterior in seguimientos_plan:
                if seg_anterior.numero_bimestre >= seguimiento.numero_bimestre:
                    break
                if seg_anterior.estado != 'completado':
                    messages.error(
                        request,
                        f'No puede completar el seguimiento del {seguimiento.numero_bimestre}° bimestre. '
                        f'Primero debe completar el seguimiento del {seg_anterior.numero_bimestre}° bimestre.'
                    )
                    return redirect('evaluations:supervisor_seguimientos_pendientes')

        if request.method == 'POST':
            avance_satisfactorio = request.POST.get('avance_satisfactorio') == 'true'
            observaciones = request.POST.get('observaciones', '').strip()
            
            seguimiento.avance_satisfactorio = avance_satisfactorio
            seguimiento.observaciones = observaciones
            seguimiento.estado = 'completado'
            seguimiento.fecha_completado = timezone.now()
            seguimiento.completado_por = request.user
            seguimiento.save()
            
            messages.success(request, f'Seguimiento del {seguimiento.numero_bimestre}° bimestre completado exitosamente.')
            
            # Verificar si se pueden generar evaluación final
            if puede_generar_evaluacion_final(plan):
                return redirect('evaluations:evaluacion_final', plan_id=plan.id)
            
            return redirect('evaluations:admin_pendientes_aprobacion')
        
        return render(request, 'evaluations/admin/seguimiento_bimensual.html', {
            'seguimiento': seguimiento,
            'plan': plan
        })
        
    except Exception as e:
        messages.error(request, f'Error al gestionar seguimiento: {str(e)}')
        return redirect('evaluations:admin_pendientes_aprobacion')


@login_required
def evaluacion_final_plan(request, plan_id):
    """
    Realizar evaluación final del plan después de 3 bimestres
    """
    from .models import PlanMejoraPredefinido, EvaluacionFinal
    from .utils.respuestas_predefinidas import puede_generar_evaluacion_final
    
    try:
        plan = get_object_or_404(PlanMejoraPredefinido, id=plan_id)
        
        # Verificar que se pueden generar evaluación final
        if not puede_generar_evaluacion_final(plan):
            messages.error(request, 'No se han completado todos los seguimientos bimensuales.')
            return redirect('evaluations:admin_pendientes_aprobacion')
        
        # Verificar que no exista ya una evaluación final
        if hasattr(plan, 'evaluacion_final'):
            messages.info(request, 'Ya existe una evaluación final para este plan.')
            return redirect('evaluations:admin_pendientes_aprobacion')
        
        # Verificar permisos
        try:
            empleado_usuario = Empleado.objects.get(usuario=request.user)
        except Empleado.DoesNotExist:
            if not request.user.is_staff:
                messages.error(request, 'No tiene permisos para realizar la evaluación final.')
                return redirect('evaluations:admin_pendientes_aprobacion')
        else:
            if (plan.asignacion_evaluacion.evaluador != empleado_usuario and 
                plan.asignacion_evaluacion.empleado_evaluado.jefe_inmediato != empleado_usuario and
                not request.user.is_staff):
                messages.error(request, 'No tiene permisos para realizar la evaluación final.')
                return redirect('evaluations:admin_pendientes_aprobacion')
        
        if request.method == 'POST':
            resultado = request.POST.get('resultado')
            conclusion = request.POST.get('conclusion', '').strip()
            
            if not conclusion:
                messages.error(request, 'La conclusión es obligatoria.')
                return render(request, 'evaluations/admin/evaluacion_final.html', {
                    'plan': plan,
                    'seguimientos': plan.seguimientos.all().order_by('numero_bimestre')
                })
            
            # Crear evaluación final
            evaluacion_final = EvaluacionFinal.objects.create(
                plan_mejora=plan,
                resultado=resultado,
                conclusion=conclusion,
                evaluado_por=request.user
            )
            
            # Marcar plan como completado
            plan.estado = 'completado'
            plan.save()
            
            messages.success(request, 'Evaluación final completada exitosamente. El plan ha sido marcado como terminado.')
            return redirect('evaluations:admin_pendientes_aprobacion')
        
        # GET - Mostrar formulario
        seguimientos = plan.seguimientos.all().order_by('numero_bimestre')

        # Contar seguimientos satisfactorios
        satisfactorios = sum(1 for s in seguimientos if s.avance_satisfactorio is True)

        return render(request, 'evaluations/admin/evaluacion_final.html', {
            'plan': plan,
            'seguimientos': seguimientos,
            'satisfactorios': satisfactorios
        })
        
    except Exception as e:
        messages.error(request, f'Error en evaluación final: {str(e)}')
        return redirect('evaluations:admin_pendientes_aprobacion')


@login_required
def ver_plan_mejora_empleado(request, plan_id):
    """
    Vista para que los empleados vean su plan de mejora y seguimientos
    """
    from .models import PlanMejoraPredefinido

    try:
        plan = get_object_or_404(PlanMejoraPredefinido, id=plan_id)

        # Permitir acceso a admins directamente
        if request.user.is_staff:
            pass  # Los admins pueden acceder
        else:
            # Verificar que el usuario sea el empleado evaluado
            try:
                empleado_usuario = Empleado.objects.get(usuario=request.user)
            except Empleado.DoesNotExist:
                messages.error(request, 'No tiene permisos para ver este plan.')
                return redirect('evaluations:index')

            # Permitir acceso al empleado evaluado o al evaluador (supervisor)
            if plan.asignacion_evaluacion.empleado_evaluado != empleado_usuario and plan.asignacion_evaluacion.evaluador != empleado_usuario:
                messages.error(request, 'No tiene permisos para ver este plan de mejora.')
                return redirect('evaluations:index')
        
        # Obtener seguimientos ordenados
        seguimientos = plan.seguimientos.all().order_by('numero_bimestre')
        
        # Verificar si tiene evaluación final
        evaluacion_final = getattr(plan, 'evaluacion_final', None)
        
        return render(request, 'evaluations/empleado/ver_plan_mejora.html', {
            'plan': plan,
            'seguimientos': seguimientos,
            'evaluacion_final': evaluacion_final,
            'asignacion': plan.asignacion_evaluacion
        })
        
    except Exception as e:
        messages.error(request, f'Error al cargar el plan: {str(e)}')
        return redirect('evaluations:index')

@login_required
def aceptar_plan_mejora(request, plan_id):
    """
    Vista para que el empleado acepte su plan de mejora
    """
    from .models import PlanMejoraPredefinido

    try:
        plan = get_object_or_404(PlanMejoraPredefinido, id=plan_id)

        # Verificar que el empleado puede aceptar este plan
        if plan.asignacion_evaluacion.empleado_evaluado.usuario != request.user:
            messages.error(request, 'No tiene permisos para aceptar este plan.')
            return redirect('evaluations:index')

        # Verificar que el plan no esté ya aceptado
        if plan.aceptado_por_empleado:
            messages.info(request, 'Este plan ya ha sido aceptado.')
            return redirect('evaluations:ver_plan_mejora_empleado', plan_id=plan_id)

        if request.method == 'POST':
            # Aceptar el plan
            plan.aceptado_por_empleado = True
            plan.fecha_aceptacion_empleado = timezone.now()
            plan.save()

            messages.success(request, 'Plan de mejora aceptado exitosamente. Ahora está disponible para aprobación del supervisor.')
            return redirect('evaluations:ver_plan_mejora_empleado', plan_id=plan_id)

        return render(request, 'evaluations/empleado/aceptar_plan.html', {
            'plan': plan,
            'asignacion': plan.asignacion_evaluacion
        })

    except Exception as e:
        messages.error(request, f'Error al procesar la aceptación del plan: {str(e)}')
        return redirect('evaluations:index')


@login_required
def imprimir_plan_mejora(request, plan_id):
    """
    Vista para imprimir el plan de mejora en formato optimizado para impresión.
    Accesible por el empleado evaluado y el supervisor/evaluador.
    """
    from .models import PlanMejoraPredefinido

    try:
        plan = get_object_or_404(PlanMejoraPredefinido, id=plan_id)

        # Verificar permisos - empleado evaluado o evaluador
        try:
            empleado_usuario = Empleado.objects.get(usuario=request.user)
            if (plan.asignacion_evaluacion.empleado_evaluado != empleado_usuario and
                plan.asignacion_evaluacion.evaluador != empleado_usuario and
                not request.user.is_staff):
                messages.error(request, 'No tiene permisos para imprimir este plan.')
                return redirect('evaluations:index')
        except Empleado.DoesNotExist:
            # Usuario admin puede imprimir
            if not request.user.is_staff:
                messages.error(request, 'No tiene permisos para imprimir este plan.')
                return redirect('evaluations:index')

        # Obtener seguimientos si existen
        seguimientos = plan.seguimientos.all().order_by('numero_bimestre')

        # Verificar si tiene evaluación final
        evaluacion_final = getattr(plan, 'evaluacion_final', None)

        return render(request, 'evaluations/empleado/imprimir_plan.html', {
            'plan': plan,
            'seguimientos': seguimientos,
            'evaluacion_final': evaluacion_final,
        })

    except Exception as e:
        messages.error(request, f'Error al cargar el plan para impresión: {str(e)}')
        return redirect('evaluations:index')


class MisEvaluacionesCompletadasView(LoginRequiredMixin, ListView):
    """Lista todas las evaluaciones completadas donde el usuario es evaluador (supervisor)"""
    template_name = 'evaluations/supervisor/completadas.html'
    context_object_name = 'evaluaciones'
    paginate_by = 10

    def get_queryset(self):
        try:
            empleado_usuario = Empleado.objects.get(usuario=self.request.user)
            return AsignacionEvaluacion.objects.filter(
                evaluador=empleado_usuario,
                estado='completada'
            ).select_related(
                'empleado_evaluado',
                'evaluacion',
                'evaluacion__tipo_evaluacion'
            ).order_by('-fecha_completada')
        except Empleado.DoesNotExist:
            return AsignacionEvaluacion.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_supervisor'] = True
        return context