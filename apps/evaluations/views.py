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
                # Guardar observación de SST (si aplica para evaluaciones anuales)
                tipo_eval_codigo = asignacion.evaluacion.tipo_evaluacion.codigo
                if tipo_eval_codigo in ['ANUAL_AUX_PROCESOS', 'ANUAL_MANTENIMIENTO', 'ANUAL_OPERARIOS_PROD', 'ANUAL_COORD_PROC', 'ANUAL_AFILADORES']:
                    uso_epp = request.POST.get('uso_epp_sst', '')
                    if uso_epp:
                        asignacion.uso_epp_sst = uso_epp

                # Finalizar evaluación
                asignacion.estado = 'completada'
                asignacion.fecha_completada = timezone.now()
                asignacion.estado_aprobacion = 'pendiente_aprobacion'
                asignacion.save()
                
                # Calcular resultados automáticamente
                _calcular_resultado_evaluacion(asignacion)
                
                # Generar plan de mejora automáticamente al completar la evaluación
                try:
                    from .models import PlanMejoraPredefinido

                    # Solo si no existe ya un plan para esta asignación
                    if not PlanMejoraPredefinido.objects.filter(asignacion_evaluacion=asignacion).exists():
                        # Verificar el puntaje total según tipo de evaluación
                        tipo_eval_codigo = asignacion.evaluacion.tipo_evaluacion.codigo
                        debe_generar_plan = True

                        if tipo_eval_codigo == 'PERIODO_PRUEBA':
                            # Para período de prueba: no generar si puntaje es 21/21
                            if asignacion.puntaje_total and asignacion.puntaje_total >= 21:
                                import logging
                                logging.info(f'Empleado {asignacion.empleado_evaluado.nombre_completo} obtuvo puntaje máximo (21/21). No se genera plan de mejora.')
                                debe_generar_plan = False
                        elif tipo_eval_codigo in ['ANUAL_AUX_PROCESOS', 'ANUAL_MANTENIMIENTO', 'ANUAL_OPERARIOS_PROD', 'ANUAL_COORD_PROC', 'ANUAL_AFILADORES']:
                            # Para evaluaciones anuales: no generar si porcentaje >= 91% (Muy alto/Excelente)
                            if asignacion.porcentaje_completado and asignacion.porcentaje_completado >= 91:
                                import logging
                                logging.info(f'Empleado {asignacion.empleado_evaluado.nombre_completo} obtuvo calificación excelente ({asignacion.porcentaje_completado}%). No se genera plan de mejora.')
                                debe_generar_plan = False

                        if debe_generar_plan:
                            # Generar plan de mejora usando el método apropiado según tipo de evaluación
                            respuestas = RespuestaEvaluacion.objects.filter(
                                asignacion=asignacion
                            ).select_related('pregunta', 'opcion_seleccionada')

                            # Usar método específico según tipo de evaluación
                            tipo_eval_codigo = asignacion.evaluacion.tipo_evaluacion.codigo

                            if tipo_eval_codigo == 'PERIODO_PRUEBA':
                                plan_mejora_texto = _generar_aspectos_mejora_periodo_prueba(asignacion)
                            elif tipo_eval_codigo == 'ANUAL_AUX_PROCESOS':
                                # Generar plan específico para Auxiliares de Procesos
                                from .utils.respuestas_predefinidas_auxiliar_procesos import (
                                    generar_plan_mejora_auxiliar_procesos,
                                    calcular_puntaje_ponderado_auxiliar_procesos
                                )
                                resultado_evaluacion = calcular_puntaje_ponderado_auxiliar_procesos(respuestas)
                                plan_mejora_texto = generar_plan_mejora_auxiliar_procesos(respuestas, resultado_evaluacion)
                            elif tipo_eval_codigo == 'ANUAL_MANTENIMIENTO':
                                # Generar plan específico para Mantenimiento
                                from .utils.respuestas_predefinidas_mantenimiento import (
                                    generar_plan_mejora_mantenimiento,
                                    calcular_puntaje_ponderado_mantenimiento
                                )
                                resultado_evaluacion = calcular_puntaje_ponderado_mantenimiento(respuestas)
                                plan_mejora_texto = generar_plan_mejora_mantenimiento(respuestas, resultado_evaluacion)
                            elif tipo_eval_codigo == 'ANUAL_OPERARIOS_PROD':
                                # Generar plan específico para Operarios de Producción
                                from .utils.respuestas_predefinidas_operarios_produccion import (
                                    generar_plan_mejora_operarios_produccion,
                                    calcular_puntaje_ponderado_operarios_produccion
                                )
                                resultado_evaluacion = calcular_puntaje_ponderado_operarios_produccion(respuestas)
                                plan_mejora_texto = generar_plan_mejora_operarios_produccion(respuestas, resultado_evaluacion)
                            elif tipo_eval_codigo == 'ANUAL_COORD_PROC':
                                # Generar plan específico para Coordinadores de Procesos
                                from .utils.respuestas_predefinidas_coordinadores_procesos import (
                                    generar_plan_mejora_coordinadores_procesos,
                                    calcular_puntaje_ponderado_coordinadores_procesos
                                )
                                resultado_evaluacion = calcular_puntaje_ponderado_coordinadores_procesos(respuestas)
                                plan_mejora_texto = generar_plan_mejora_coordinadores_procesos(respuestas, resultado_evaluacion)
                            elif tipo_eval_codigo == 'ANUAL_AFILADORES':
                                # Generar plan específico para Afiladores
                                from .utils.respuestas_predefinidas_afiladores import (
                                    generar_plan_mejora_afiladores,
                                    calcular_puntaje_ponderado_afiladores
                                )
                                resultado_evaluacion = calcular_puntaje_ponderado_afiladores(respuestas)
                                plan_mejora_texto = generar_plan_mejora_afiladores(respuestas, resultado_evaluacion)
                            else:
                                # Usar método genérico para otras evaluaciones
                                from .utils.respuestas_predefinidas import generar_plan_automatico
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

        tipo_evaluacion_codigo = asignacion.evaluacion.tipo_evaluacion.codigo

        # ============ EVALUACIONES ANUALES CON PONDERACIÓN ============
        if tipo_evaluacion_codigo == 'ANUAL_AUX_PROCESOS':
            from .utils.respuestas_predefinidas_auxiliar_procesos import calcular_puntaje_ponderado_auxiliar_procesos
            resultado_calc = calcular_puntaje_ponderado_auxiliar_procesos(respuestas)
        elif tipo_evaluacion_codigo == 'ANUAL_MANTENIMIENTO':
            from .utils.respuestas_predefinidas_mantenimiento import calcular_puntaje_ponderado_mantenimiento
            resultado_calc = calcular_puntaje_ponderado_mantenimiento(respuestas)
        elif tipo_evaluacion_codigo == 'ANUAL_OPERARIOS_PROD':
            from .utils.respuestas_predefinidas_operarios_produccion import calcular_puntaje_ponderado_operarios_produccion
            resultado_calc = calcular_puntaje_ponderado_operarios_produccion(respuestas)
        elif tipo_evaluacion_codigo == 'ANUAL_COORD_PROC':
            from .utils.respuestas_predefinidas_coordinadores_procesos import calcular_puntaje_ponderado_coordinadores_procesos
            resultado_calc = calcular_puntaje_ponderado_coordinadores_procesos(respuestas)
        elif tipo_evaluacion_codigo == 'ANUAL_AFILADORES':
            from .utils.respuestas_predefinidas_afiladores import calcular_puntaje_ponderado_afiladores
            resultado_calc = calcular_puntaje_ponderado_afiladores(respuestas)
        else:
            resultado_calc = None

        if resultado_calc:

            puntaje_final = Decimal(str(resultado_calc['puntaje_escala']))  # 1-5
            porcentaje = Decimal(str(resultado_calc['puntaje_porcentaje']))  # 0-100
            nivel_desempeno = resultado_calc['nivel_desempeno']  # 'Muy bajo', 'Bajo', 'Moderado', 'Alto', 'Muy alto'

            # Mapear nivel_desempeno a clasificación estándar
            mapeo_clasificacion = {
                'Muy alto': 'excelente',
                'Alto': 'sobresaliente',
                'Moderado': 'satisfactorio',
                'Bajo': 'mejorable',
                'Muy bajo': 'insatisfactorio'
            }
            clasificacion = mapeo_clasificacion.get(nivel_desempeno, 'satisfactorio')

            # Generar aspectos según nivel
            if porcentaje >= 91:
                aspectos_positivos = "• Desempeño excepcional en todas las competencias evaluadas\n• Supera consistentemente las expectativas en todas las categorías\n• Referente de excelencia para el equipo"
                areas_mejora = "• Continuar siendo modelo de excelencia\n• Liderar programas de mejora en el área\n• Mentor de compañeros con menor desempeño"
            elif porcentaje >= 76:
                aspectos_positivos = "• Desempeño destacado en la mayoría de competencias\n• Supera las expectativas del cargo\n• Contribuye significativamente a objetivos del área"
                areas_mejora = "• Fortalecer competencias con calificación moderada\n• Incrementar participación en proyectos de mejora\n• Desarrollar habilidades de liderazgo"
            elif porcentaje >= 61:
                aspectos_positivos = "• Cumple satisfactoriamente con las responsabilidades del cargo\n• Desempeño aceptable en la mayoría de competencias\n• Mantiene estándares mínimos de calidad"
                areas_mejora = "• Mejorar competencias con calificación baja\n• Incrementar eficiencia y productividad\n• Fortalecer habilidades técnicas específicas"
            elif porcentaje >= 41:
                aspectos_positivos = "• Muestra disposición para aprender y mejorar\n• Cumple con algunas responsabilidades básicas\n• Asiste puntualmente a sus labores"
                areas_mejora = "• Requiere capacitación urgente en competencias críticas\n• Necesita supervisión y acompañamiento constante\n• Desarrollar habilidades técnicas básicas del puesto"
            else:
                aspectos_positivos = "• Asiste a sus labores\n• Muestra interés en el desarrollo profesional"
                areas_mejora = "• Requiere mejora urgente en todas las competencias evaluadas\n• Necesita capacitación intensiva y supervisión directa\n• Plan de acción correctivo inmediato"

            # Detalle por categorías
            detalle_categorias = resultado_calc.get('detalle_categorias', {})
            comentarios_detalle = "DESEMPEÑO POR CATEGORÍAS:\n"
            for cat, datos in detalle_categorias.items():
                comentarios_detalle += f"• {cat}: {datos['promedio']}/5 ({datos['porcentaje']:.1f}%)\n"

            comentarios_generales = f'Evaluación anual completada con {porcentaje:.1f}% de cumplimiento.\n\n{comentarios_detalle}'

            # Determinar recomendación
            if porcentaje >= 76:
                recomendaciones = 'Desempeño destacado. Se recomienda considerar para promociones o responsabilidades adicionales.'
            elif porcentaje >= 61:
                recomendaciones = 'Desempeño satisfactorio. El empleado continúa en el cargo con seguimiento en áreas de mejora.'
            else:
                recomendaciones = 'Desempeño por debajo de expectativas. Requiere plan de mejora con seguimientos bimensuales.'

            # Guardar puntaje total en formato compatible
            puntaje_total_acumulado = porcentaje  # Para evaluaciones ponderadas, guardamos el porcentaje

        # ============ EVALUACIONES DE PERÍODO DE PRUEBA (Escala 1-3) ============
        else:
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

            comentarios_generales = f'Evaluación completada con {porcentaje:.1f}% de cumplimiento.'
            recomendaciones = 'Se recomienda que el empleado continúe en la empresa.' if puntaje_acumulado >= 14 else 'Se requiere plan de mejora inmediato.'
            puntaje_total_acumulado = puntaje_acumulado

        # ============ GUARDAR RESULTADO (Común para todos los tipos) ============
        resultado, created = ResultadoEvaluacion.objects.get_or_create(
            asignacion=asignacion,
            defaults={
                'puntaje_final': puntaje_final,
                'porcentaje_obtenido': porcentaje,
                'nivel_desempeño': clasificacion,
                'aspectos_positivos': aspectos_positivos,
                'areas_mejora': areas_mejora,
                'comentarios_generales': comentarios_generales,
                'recomendaciones': recomendaciones,
                'generado_por': asignacion.evaluador.usuario if asignacion.evaluador and asignacion.evaluador.usuario else None,
            }
        )

        if not created:
            resultado.puntaje_final = puntaje_final
            resultado.porcentaje_obtenido = porcentaje
            resultado.nivel_desempeño = clasificacion
            resultado.aspectos_positivos = aspectos_positivos
            resultado.areas_mejora = areas_mejora
            resultado.comentarios_generales = comentarios_generales
            resultado.recomendaciones = recomendaciones
            resultado.save()

        # Actualizar también los campos en la asignación para compatibilidad con templates existentes
        asignacion.puntaje_total = puntaje_total_acumulado
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

        # Contar planes sin aceptar, diferenciando bajo desempeño según tipo de evaluación
        planes_sin_aceptar = 0
        planes_reprobados = 0

        for plan in queryset.filter(aceptado_por_empleado=False):
            if plan.asignacion_evaluacion.puntaje_total:
                tipo_evaluacion = plan.asignacion_evaluacion.evaluacion.tipo_evaluacion.codigo
                puntaje = plan.asignacion_evaluacion.puntaje_total

                # Determinar si es bajo desempeño según el tipo
                es_bajo_desempeno = False
                if tipo_evaluacion == 'PERIODO_PRUEBA':
                    es_bajo_desempeno = puntaje < 14
                elif tipo_evaluacion in ['ANUAL_AUX_PROCESOS', 'ANUAL_MANTENIMIENTO', 'ANUAL_OPERARIOS_PROD', 'ANUAL_COORD_PROC', 'ANUAL_AFILADORES']:
                    es_bajo_desempeno = puntaje < 61

                if es_bajo_desempeno:
                    planes_reprobados += 1
                else:
                    planes_sin_aceptar += 1
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
    """Generar plan de mejora basado en las respuestas del documento de período de prueba"""
    # Documento de respuestas posibles - mismo contenido que en actualizar_opciones_documento.py
    RESPUESTAS_DOCUMENTO = {
        'Trabajo en equipo': {
            1: {'observacion': 'Se presentan dificultades para integrarse plenamente con el equipo. En algunas ocasiones surgen desacuerdos debido a la falta de escucha activa o a una disposición limitada para colaborar.', 'recomendacion': 'Fortalecer la comunicación y la participación dentro del equipo, solicitando apoyo cuando sea necesario y brindándolo igualmente. Involucrarse de manera más activa en actividades grupales contribuirá a un mejor clima laboral.', 'ejemplo': 'Iniciar ofreciendo apoyo en tareas sencillas para generar confianza y mejorar la relación con los compañeros'},
            2: {'observacion': 'Muestra disposición para colaborar en algunas situaciones, aunque de manera inconstante. En ocasiones se requiere que se involucre más activamente en la consecución de objetivos comunes.', 'recomendacion': 'Incrementar la participación proactiva en las tareas grupales, promoviendo el diálogo y la búsqueda de acuerdos.', 'ejemplo': 'Proponer soluciones en reuniones de equipo y mostrar apertura a las ideas de otros'},
            3: {'observacion': 'Demuestra una actitud colaborativa constante, valora las opiniones de otros y contribuye activamente al logro de objetivos comunes.', 'recomendacion': 'Mantener esta actitud positiva y fortalecer el liderazgo informal en el equipo.', 'ejemplo': 'Continuar apoyando a sus compañeros'}
        },
        'Compromiso': {
            1: {'observacion': 'No siempre evidencia constancia o disposición para apoyar las metas del proceso. En ocasiones, evita asumir responsabilidades adicionales.', 'recomendacion': 'Fortalecer el sentido de pertenencia y compromiso hacia el área, mostrando iniciativa en la resolución de tareas diarias.', 'ejemplo': 'Buscar oportunidades diarias para contribuir de manera proactiva, sin esperar indicaciones'},
            2: {'observacion': 'Muestra compromiso en algunas ocasiones, pero este no es constante y requiere acompañamiento para asumir determinadas actividades.', 'recomendacion': 'Fortalecer la constancia y demostrar mayor autonomía en las labores diarias. Atender con diligencia aquellas tareas no contempladas explícitamente en las funciones, pero que surgen de manera cotidiana y son importantes para garantizar la calidad del trabajo.', 'ejemplo': 'Identificar tareas pendientes y gestionarlas de manera autónoma, sin esperar instrucciones directas'},
            3: {'observacion': 'Demuestra constancia, disposición al esfuerzo y capacidad para asumir actividades adicionales cuando se requiere.', 'recomendacion': 'Mantener este nivel de compromiso y aprovechar oportunidades de liderazgo.', 'ejemplo': 'Continuar siendo un ejemplo de dedicación'}
        },
        'Comunicación': {
            1: {'observacion': 'Se presentan dificultades para expresar ideas de manera comprensible o para mantener una escucha activa, lo cual afecta la coordinación.', 'recomendacion': 'Fortalecer la habilidad comunicativa practicando la expresión clara y la escucha atenta. Asegurar que la información transmitida sea completa y oportuna.', 'ejemplo': 'Resumir los puntos clave antes de finalizar una conversación'},
            2: {'observacion': 'Generalmente se comunica de forma adecuada, aunque en algunas ocasiones puede haber falta de claridad o malentendidos.', 'recomendacion': 'Continuar fortaleciendo la expresión y la escucha, asegurando que la comunicación sea asertiva y oportuna.', 'ejemplo': 'Preguntar para confirmar que la información fue comprendida correctamente'},
            3: {'observacion': 'Se comunica de forma clara, escucha activamente y facilita la resolución de acuerdos.', 'recomendacion': 'Mantener y fortalecer esta habilidad, continuando como un referente de comunicación efectiva.', 'ejemplo': 'Mantener este nivel de comunicación'}
        },
        'Atención al detalle': {
            1: {'observacion': 'Presenta omisiones o errores que afectan la calidad de las tareas realizadas, lo que requiere supervisión constante.', 'recomendacion': 'Incrementar la concentración al realizar actividades para reducir errores. Verificar cada actividad antes de considerarla terminada.', 'ejemplo': 'Utilizar listas de verificación antes de entregar cualquier tarea'},
            2: {'observacion': 'Suele mostrar una buena atención en sus tareas; sin embargo, en algunas ocasiones ciertos detalles pueden pasar desapercibidos.', 'recomendacion': 'Se sugiere fortalecer la concentración, especialmente en tareas críticas, para asegurar que todos los elementos relevantes sean considerados.', 'ejemplo': 'Subrayar o marcar los puntos importantes de cada actividad antes de ejecutarla'},
            3: {'observacion': 'Demuestra excelente atención al detalle, revisa su trabajo antes de entregarlo y rara vez comete errores.', 'recomendacion': 'Mantener este nivel de precisión y continuar siendo un ejemplo para otros.', 'ejemplo': 'Mantener este nivel de calidad'}
        },
        'Cumplimiento de las normas y procedimientos': {
            1: {'observacion': 'Actualmente tiene dificultades para seguir los procedimientos establecidos y requiere recordatorios frecuentes para completar las tareas de acuerdo con los protocolos.', 'recomendacion': 'Se sugiere revisar nuevamente los protocolos del área y practicarlos de forma constante para lograr una aplicación más segura y uniforme.', 'ejemplo': 'Revisar el manual del área antes de realizar procedimientos clave'},
            2: {'observacion': 'Cumple la mayoría de las normas, aunque en ocasiones puede olvidar ciertos aspectos o requerir recordatorios.', 'recomendacion': 'Fortalecer la consistencia en la aplicación de procedimientos y normas institucionales.', 'ejemplo': 'Aplicar recordatorios diarios o listas de chequeo para protocolos clave'},
            3: {'observacion': 'Demuestra un cumplimiento estricto de normas y procedimientos, lo que garantiza calidad y seguridad.', 'recomendacion': 'Mantener esta disciplina y servir como referente para otros compañeros.', 'ejemplo': 'Continuar siendo un ejemplo de cumplimiento'}
        },
        'Actitud respecto al trabajo': {
            1: {'observacion': 'Se observa falta de motivación o actitud poco positiva en diversas situaciones laborales.', 'recomendacion': 'Identificar factores que afectan la motivación y trabajar en fortalecer una actitud más proactiva y constructiva.', 'ejemplo': 'Establecer objetivos personales diarios para aumentar la motivación'},
            2: {'observacion': 'Generalmente muestra buena actitud, pero en situaciones de presión se ve afectada su disposición.', 'recomendacion': 'Fortalecer su manejo emocional en situaciones de alta demanda para mantener la estabilidad y el enfoque.', 'ejemplo': 'Aplicar técnicas breves de respiración o pausas conscientes cuando surja el estrés'},
            3: {'observacion': 'Mantiene una actitud positiva, proactiva y orientada al crecimiento, contribuyendo a un buen ambiente laboral.', 'recomendacion': 'Mantener esta disposición y servir como ejemplo positivo para el equipo.', 'ejemplo': 'Continuar con esta actitud positiva'}
        },
        'Calidad': {
            1: {'observacion': 'Se han identificado errores recurrentes en las tareas o falta de una revisión final antes de entregarlas.', 'recomendacion': 'Fortalecer el control de calidad para asegurar resultados más precisos y completos.', 'ejemplo': 'Antes de finalizar, revisar tres aspectos clave: formato, exactitud de la información y coherencia del contenido'},
            2: {'observacion': 'La calidad del trabajo suele ser buena, aunque ocasionalmente se presentan fallas por descuidos puntuales.', 'recomendacion': 'Incrementar la atención en actividades repetitivas o que requieran mayor detalle para evitar errores menores.', 'ejemplo': 'Solicitar retroalimentación sobre las entregas para identificar oportunidades de mejora continua'},
            3: {'observacion': 'Entregas de excelente calidad, sin errores y con evidente cuidado.', 'recomendacion': 'Mantener este nivel de dedicación y precisión en todas las tareas asignadas, ya que aporta significativamente a la calidad del trabajo del equipo.', 'ejemplo': 'Mantener este nivel de calidad'}
        }
    }

    respuestas = RespuestaEvaluacion.objects.filter(
        asignacion=asignacion
    ).select_related('pregunta', 'opcion_seleccionada').order_by('pregunta__orden')

    if not respuestas.exists():
        return 'El empleado cumple satisfactoriamente con todos los aspectos evaluados.'

    aspectos_mejora = []
    numero = 1

    # Mapeo de calificación a etiqueta
    etiqueta_map = {
        1: "No cumple",
        2: "Cumple parcialmente",
        3: "Cumple totalmente"
    }

    for respuesta in respuestas:
        pregunta_nombre = respuesta.pregunta.pregunta
        calificacion = int(respuesta.puntaje_obtenido)
        etiqueta = etiqueta_map.get(calificacion, "Sin información")

        # Buscar en el documento de respuestas
        datos = None
        if pregunta_nombre in RESPUESTAS_DOCUMENTO:
            datos = RESPUESTAS_DOCUMENTO[pregunta_nombre].get(calificacion)

        # Construir la sección
        seccion = f"{numero}. {pregunta_nombre}: ⭐ Calificación {calificacion} – {etiqueta}\n"

        if datos:
            seccion += f"Observación:\n{datos['observacion']}\n\n"
            seccion += f"Recomendación:\n{datos['recomendacion']}\n\n"
            if calificacion in [1, 2]:
                seccion += f"Ejemplo: {datos['ejemplo']}\n"
                seccion += "Requiere seguimiento\n"
            else:
                seccion += f"Ejemplo: {datos['ejemplo']}\n"
        else:
            # Fallback si no se encuentra en el documento
            seccion += f"Observación: [No disponible para {pregunta_nombre}]\n\n"

        aspectos_mejora.append(seccion)
        numero += 1

    if not aspectos_mejora:
        return 'El empleado cumple satisfactoriamente con todos los aspectos evaluados.'

    plan_texto = "\n".join(aspectos_mejora)
    return plan_texto


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
            # Generar el plan automáticamente usando el método apropiado según tipo de evaluación
            if asignacion.evaluacion.tipo_evaluacion.codigo == 'PERIODO_PRUEBA':
                plan_mejora_texto = _generar_aspectos_mejora_periodo_prueba(asignacion)
            else:
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
        # Generar preview del plan usando el método apropiado
        if asignacion.evaluacion.tipo_evaluacion.codigo == 'PERIODO_PRUEBA':
            plan_preview = _generar_aspectos_mejora_periodo_prueba(asignacion)
        else:
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

        # Verificar permisos - solo evaluador/jefe inmediato/admin/superuser
        # Primero permitir a admins y superusers
        if request.user.is_staff or request.user.is_superuser:
            # El admin puede revisar todos los planes
            pass
        else:
            # Para usuarios normales, verificar si es evaluador o jefe inmediato
            try:
                empleado_usuario = Empleado.objects.get(usuario=request.user)
                if (plan.asignacion_evaluacion.evaluador != empleado_usuario and
                    plan.asignacion_evaluacion.empleado_evaluado.jefe_inmediato != empleado_usuario):
                    messages.error(request, 'No tiene permisos para revisar este plan.')
                    return redirect('evaluations:admin_pendientes_aprobacion')
            except Empleado.DoesNotExist:
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

                    # Determinar si requiere seguimiento según tipo de evaluación
                    tipo_evaluacion = plan.asignacion_evaluacion.evaluacion.tipo_evaluacion.codigo
                    puntaje = plan.asignacion_evaluacion.puntaje_total or 0
                    requiere_seguimiento = False
                    mensaje_aprobacion = ''

                    if tipo_evaluacion == 'PERIODO_PRUEBA':
                        # Período de prueba: puntaje máximo = 21
                        requiere_seguimiento = float(puntaje) < 21
                        if requiere_seguimiento:
                            mensaje_aprobacion = 'Plan aprobado exitosamente. Se han creado los seguimientos bimensuales automáticamente.'
                        else:
                            mensaje_aprobacion = f'Plan aprobado exitosamente. El empleado obtuvo el puntaje máximo ({puntaje:.0f}/21), por lo que no requiere seguimientos bimensuales.'

                    elif tipo_evaluacion in ['ANUAL_AUX_PROCESOS', 'ANUAL_MANTENIMIENTO', 'ANUAL_OPERARIOS_PROD', 'ANUAL_COORD_PROC', 'ANUAL_AFILADORES']:
                        # Evaluación anual: requiere seguimiento si no es "Muy Alto" (< 91%)
                        requiere_seguimiento = float(puntaje) < 91.0
                        if requiere_seguimiento:
                            mensaje_aprobacion = f'Plan aprobado exitosamente. Puntaje: {puntaje:.2f}%. Se han creado los seguimientos bimensuales automáticamente.'
                        else:
                            mensaje_aprobacion = f'Plan aprobado exitosamente. El empleado obtuvo un desempeño Muy Alto ({puntaje:.2f}%), por lo que no requiere seguimientos bimensuales.'

                    else:
                        # Otros tipos de evaluación: siempre requieren seguimiento
                        requiere_seguimiento = True
                        mensaje_aprobacion = 'Plan aprobado exitosamente. Se han creado los seguimientos bimensuales automáticamente.'

                    if requiere_seguimiento:
                        # Crear seguimientos bimensuales automáticamente
                        crear_seguimientos_bimensuales(plan)

                        # Cambiar estado del plan a 'en_seguimiento'
                        plan.estado = 'en_seguimiento'
                        plan.save()
                    else:
                        # Puntaje máximo - No requiere seguimiento
                        plan.estado = 'completado'
                        plan.save()

                    messages.success(request, mensaje_aprobacion)
                    
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
    Y planes listos para evaluación final
    Agrupados por jefe/evaluador
    """
    from .models import SeguimientoBimensual, PlanMejoraPredefinido
    from .utils.respuestas_predefinidas import puede_generar_evaluacion_final
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

                # Obtener planes listos para evaluación final (todos seguimientos completados, sin evaluación final)
                planes_para_evaluar = PlanMejoraPredefinido.objects.filter(
                    estado='en_seguimiento'
                ).select_related(
                    'asignacion_evaluacion',
                    'asignacion_evaluacion__empleado_evaluado',
                    'asignacion_evaluacion__evaluador',
                    'asignacion_evaluacion__evaluacion',
                    'asignacion_evaluacion__evaluacion__tipo_evaluacion'
                ).prefetch_related(
                    'seguimientos',
                    'asignacion_evaluacion__empleado_evaluado__historialcargo_set',
                    'asignacion_evaluacion__empleado_evaluado__historialcargo_set__cargo',
                    'asignacion_evaluacion__empleado_evaluado__historialcargo_set__cargo__area'
                )
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

            # Obtener planes listos para evaluación final del evaluador
            planes_para_evaluar = PlanMejoraPredefinido.objects.filter(
                asignacion_evaluacion__evaluador=empleado_usuario,
                estado='en_seguimiento'
            ).select_related(
                'asignacion_evaluacion',
                'asignacion_evaluacion__empleado_evaluado',
                'asignacion_evaluacion__evaluador',
                'asignacion_evaluacion__evaluacion',
                'asignacion_evaluacion__evaluacion__tipo_evaluacion'
            ).prefetch_related(
                'seguimientos',
                'asignacion_evaluacion__empleado_evaluado__historialcargo_set',
                'asignacion_evaluacion__empleado_evaluado__historialcargo_set__cargo',
                'asignacion_evaluacion__empleado_evaluado__historialcargo_set__cargo__area'
            )

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

        # Filtrar planes listos para evaluación final
        # (todos los seguimientos completados y sin evaluación final)
        planes_listos_evaluacion_final = []
        for plan in planes_para_evaluar:
            # Verificar si puede generar evaluación final (todos seguimientos completados)
            if puede_generar_evaluacion_final(plan):
                # Verificar que NO tenga evaluación final ya creada
                if not hasattr(plan, 'evaluacion_final'):
                    # Contar seguimientos satisfactorios
                    seguimientos_plan = plan.seguimientos.all()
                    satisfactorios = sum(1 for s in seguimientos_plan if s.avance_satisfactorio is True)

                    planes_listos_evaluacion_final.append({
                        'plan': plan,
                        'asignacion': plan.asignacion_evaluacion,
                        'seguimientos_satisfactorios': satisfactorios,
                        'total_seguimientos': seguimientos_plan.count(),
                    })

        return render(request, 'evaluations/supervisor/seguimientos_pendientes.html', {
            'jefes_con_seguimientos': jefes_con_seguimientos,
            'es_admin': es_admin,
            'total_pendientes': total_pendientes,
            'vencidos': vencidos,
            'proximos': proximos,
            'planes_listos_evaluacion_final': planes_listos_evaluacion_final,
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

            # NO marcar plan como completado todavía
            # El plan se completará cuando:
            # 1. El empleado ACEPTE la evaluación final (automático), o
            # 2. RRHH valide la evaluación final (si el empleado la rechaza)

            messages.success(
                request,
                'Evaluación final creada exitosamente. '
                'El empleado debe revisar y aceptar la evaluación final para completar el proceso.'
            )
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
def aceptar_evaluacion_final_empleado(request, evaluacion_final_id):
    """
    Vista para que el empleado acepte o rechace la evaluación final
    """
    from .models import EvaluacionFinal
    from django.utils import timezone

    try:
        evaluacion_final = get_object_or_404(EvaluacionFinal, id=evaluacion_final_id)
        plan = evaluacion_final.plan_mejora

        # Verificar que el usuario sea el empleado evaluado
        try:
            empleado_usuario = Empleado.objects.get(usuario=request.user)
        except Empleado.DoesNotExist:
            messages.error(request, 'No tiene permisos para interactuar con esta evaluación final.')
            return redirect('evaluations:index')

        if plan.asignacion_evaluacion.empleado_evaluado != empleado_usuario:
            messages.error(request, 'No tiene permisos para interactuar con esta evaluación final.')
            return redirect('evaluations:index')

        # Verificar que aún no haya sido aceptada o rechazada
        if evaluacion_final.aceptado_por_empleado:
            messages.info(request, 'Esta evaluación final ya ha sido aceptada.')
            return redirect('evaluations:ver_plan_mejora_empleado', plan_id=plan.id)

        if evaluacion_final.rechazado_por_empleado:
            messages.info(request, 'Esta evaluación final ya ha sido rechazada y está en revisión por Gestión Humana.')
            return redirect('evaluations:ver_plan_mejora_empleado', plan_id=plan.id)

        if request.method == 'POST':
            accion = request.POST.get('accion')

            if accion == 'aceptar':
                # Aceptar la evaluación final
                evaluacion_final.aceptado_por_empleado = True
                evaluacion_final.fecha_aceptacion_empleado = timezone.now()
                evaluacion_final.save()

                # COMPLETAR EL PLAN AUTOMÁTICAMENTE
                plan.estado = 'completado'
                plan.save()

                messages.success(
                    request,
                    'Has aceptado la evaluación final exitosamente. '
                    'El plan de mejora ha sido marcado como completado. ¡Felicidades por completar el proceso!'
                )
                return redirect('evaluations:ver_plan_mejora_empleado', plan_id=plan.id)

            elif accion == 'rechazar':
                # Rechazar la evaluación final
                motivo_rechazo = request.POST.get('motivo_rechazo', '').strip()

                if not motivo_rechazo:
                    messages.error(request, 'Debe proporcionar un motivo para rechazar la evaluación final.')
                    return render(request, 'evaluations/empleado/aceptar_evaluacion_final.html', {
                        'evaluacion_final': evaluacion_final,
                        'plan': plan,
                        'asignacion': plan.asignacion_evaluacion,
                        'error_motivo': True
                    })

                evaluacion_final.rechazado_por_empleado = True
                evaluacion_final.fecha_rechazo_empleado = timezone.now()
                evaluacion_final.motivo_rechazo_empleado = motivo_rechazo
                evaluacion_final.en_revision_rrhh = True
                evaluacion_final.save()

                # NO completar el plan - queda en seguimiento hasta que RRHH valide

                messages.warning(
                    request,
                    'Has rechazado la evaluación final. '
                    'Tu caso ha sido enviado a Gestión Humana para revisión y validación.'
                )
                return redirect('evaluations:ver_plan_mejora_empleado', plan_id=plan.id)

        # GET - Mostrar formulario
        seguimientos = plan.seguimientos.all().order_by('numero_bimestre')

        return render(request, 'evaluations/empleado/aceptar_evaluacion_final.html', {
            'evaluacion_final': evaluacion_final,
            'plan': plan,
            'seguimientos': seguimientos,
            'asignacion': plan.asignacion_evaluacion,
        })

    except Exception as e:
        messages.error(request, f'Error al procesar la evaluación final: {str(e)}')
        return redirect('evaluations:index')


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

        # Verificar si la evaluación final está pendiente de aceptación del empleado
        evaluacion_final_pendiente = False
        if evaluacion_final:
            evaluacion_final_pendiente = evaluacion_final.esta_pendiente_aceptacion

        return render(request, 'evaluations/empleado/ver_plan_mejora.html', {
            'plan': plan,
            'seguimientos': seguimientos,
            'evaluacion_final': evaluacion_final,
            'evaluacion_final_pendiente': evaluacion_final_pendiente,
            'asignacion': plan.asignacion_evaluacion
        })
        
    except Exception as e:
        messages.error(request, f'Error al cargar el plan: {str(e)}')
        return redirect('evaluations:index')

@login_required
def aceptar_plan_mejora(request, plan_id):
    """
    Vista para que el empleado acepte o rechace su plan de mejora
    """
    from .models import PlanMejoraPredefinido

    try:
        plan = get_object_or_404(PlanMejoraPredefinido, id=plan_id)

        # Verificar que el empleado puede interactuar con este plan
        if plan.asignacion_evaluacion.empleado_evaluado.usuario != request.user:
            messages.error(request, 'No tiene permisos para interactuar con este plan.')
            return redirect('evaluations:index')

        # Verificar que el plan no esté ya aceptado o rechazado
        if plan.aceptado_por_empleado:
            messages.info(request, 'Este plan ya ha sido aceptado.')
            return redirect('evaluations:ver_plan_mejora_empleado', plan_id=plan_id)

        if plan.rechazado_por_empleado:
            messages.info(request, 'Este plan ya ha sido rechazado. Está en revisión por Gestión Humana.')
            return redirect('evaluations:ver_plan_mejora_empleado', plan_id=plan_id)

        if request.method == 'POST':
            accion = request.POST.get('accion')

            if accion == 'aceptar':
                # Aceptar el plan
                plan.aceptado_por_empleado = True
                plan.fecha_aceptacion_empleado = timezone.now()
                plan.save()

                messages.success(
                    request,
                    'Plan de mejora aceptado exitosamente como autoevaluación. '
                    'Ahora está disponible para aprobación del supervisor.'
                )
                return redirect('evaluations:ver_plan_mejora_empleado', plan_id=plan_id)

            elif accion == 'rechazar':
                # Rechazar el plan
                motivo_rechazo = request.POST.get('motivo_rechazo', '').strip()

                if not motivo_rechazo:
                    messages.error(request, 'Debe proporcionar un motivo para rechazar el plan.')
                    return render(request, 'evaluations/empleado/aceptar_plan.html', {
                        'plan': plan,
                        'asignacion': plan.asignacion_evaluacion,
                        'error_motivo': True
                    })

                plan.rechazado_por_empleado = True
                plan.fecha_rechazo_empleado = timezone.now()
                plan.motivo_rechazo_empleado = motivo_rechazo
                plan.en_revision_rrhh = True
                plan.save()

                messages.warning(
                    request,
                    'Has rechazado el plan de mejora. Tu desacuerdo ha sido enviado a Gestión Humana '
                    'para revisión. Ellos decidirán si aprobar el plan original o solicitar una nueva evaluación.'
                )
                return redirect('evaluations:ver_plan_mejora_empleado', plan_id=plan_id)

        return render(request, 'evaluations/empleado/aceptar_plan.html', {
            'plan': plan,
            'asignacion': plan.asignacion_evaluacion
        })

    except Exception as e:
        messages.error(request, f'Error al procesar el plan: {str(e)}')
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


@login_required
def evaluaciones_finales_rechazadas_rrhh(request):
    """
    Vista para RRHH: listado de evaluaciones finales rechazadas por empleados
    que necesitan validación
    """
    from .models import EvaluacionFinal

    # Verificar permisos de administrador/RRHH
    if not request.user.is_staff:
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('evaluations:index')

    try:
        # Obtener evaluaciones finales rechazadas pendientes de validación
        evaluaciones_rechazadas = EvaluacionFinal.objects.filter(
            rechazado_por_empleado=True,
            en_revision_rrhh=True,
            validado_por_rrhh__isnull=True
        ).select_related(
            'plan_mejora',
            'plan_mejora__asignacion_evaluacion',
            'plan_mejora__asignacion_evaluacion__empleado_evaluado',
            'plan_mejora__asignacion_evaluacion__evaluador',
            'plan_mejora__asignacion_evaluacion__evaluacion',
            'plan_mejora__asignacion_evaluacion__evaluacion__tipo_evaluacion',
            'evaluado_por'
        ).prefetch_related(
            'plan_mejora__seguimientos'
        ).order_by('-fecha_rechazo_empleado')

        # También obtener las ya validadas para referencia
        evaluaciones_validadas = EvaluacionFinal.objects.filter(
            rechazado_por_empleado=True,
            en_revision_rrhh=True,
            validado_por_rrhh__isnull=False
        ).select_related(
            'plan_mejora',
            'plan_mejora__asignacion_evaluacion',
            'plan_mejora__asignacion_evaluacion__empleado_evaluado',
            'validado_por_rrhh'
        ).order_by('-fecha_validacion_rrhh')[:10]  # Últimas 10

        # Agregar información adicional
        evaluaciones_con_info = []
        for eval_final in evaluaciones_rechazadas:
            seguimientos = eval_final.plan_mejora.seguimientos.all()
            satisfactorios = sum(1 for s in seguimientos if s.avance_satisfactorio is True)

            evaluaciones_con_info.append({
                'evaluacion_final': eval_final,
                'plan': eval_final.plan_mejora,
                'asignacion': eval_final.plan_mejora.asignacion_evaluacion,
                'seguimientos_satisfactorios': satisfactorios,
                'total_seguimientos': seguimientos.count(),
            })

        return render(request, 'evaluations/admin/evaluaciones_finales_rechazadas.html', {
            'evaluaciones_con_info': evaluaciones_con_info,
            'evaluaciones_validadas': evaluaciones_validadas,
            'total_pendientes': evaluaciones_rechazadas.count(),
        })

    except Exception as e:
        messages.error(request, f'Error al cargar evaluaciones rechazadas: {str(e)}')
        return redirect('evaluations:index')


@login_required
def validar_evaluacion_final_rrhh(request, evaluacion_final_id):
    """
    Vista para que RRHH valide una evaluación final rechazada por el empleado
    """
    from .models import EvaluacionFinal
    from django.utils import timezone

    # Verificar permisos de administrador/RRHH
    if not request.user.is_staff:
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('evaluations:index')

    try:
        evaluacion_final = get_object_or_404(EvaluacionFinal, id=evaluacion_final_id)
        plan = evaluacion_final.plan_mejora

        # Verificar que esté rechazada y pendiente de validación
        if not evaluacion_final.rechazado_por_empleado:
            messages.error(request, 'Esta evaluación final no ha sido rechazada por el empleado.')
            return redirect('evaluations:evaluaciones_finales_rechazadas_rrhh')

        if evaluacion_final.validado_por_rrhh:
            messages.info(request, 'Esta evaluación final ya ha sido validada.')
            return redirect('evaluations:evaluaciones_finales_rechazadas_rrhh')

        if request.method == 'POST':
            comentarios_rrhh = request.POST.get('comentarios_rrhh', '').strip()

            if not comentarios_rrhh:
                messages.error(request, 'Debe proporcionar comentarios sobre la resolución.')
                return render(request, 'evaluations/admin/validar_evaluacion_final.html', {
                    'evaluacion_final': evaluacion_final,
                    'plan': plan,
                    'seguimientos': plan.seguimientos.all().order_by('numero_bimestre'),
                    'error_comentarios': True
                })

            # VALIDAR por RRHH
            evaluacion_final.validado_por_rrhh = request.user
            evaluacion_final.fecha_validacion_rrhh = timezone.now()
            evaluacion_final.comentarios_rrhh = comentarios_rrhh
            evaluacion_final.save()

            # COMPLETAR EL PLAN (RRHH tiene la palabra final)
            plan.estado = 'completado'
            plan.save()

            messages.success(
                request,
                f'Evaluación final validada exitosamente. '
                f'El plan de {plan.asignacion_evaluacion.empleado_evaluado.nombre_completo} ha sido marcado como completado.'
            )
            return redirect('evaluations:evaluaciones_finales_rechazadas_rrhh')

        # GET - Mostrar formulario
        seguimientos = plan.seguimientos.all().order_by('numero_bimestre')
        satisfactorios = sum(1 for s in seguimientos if s.avance_satisfactorio is True)

        return render(request, 'evaluations/admin/validar_evaluacion_final.html', {
            'evaluacion_final': evaluacion_final,
            'plan': plan,
            'seguimientos': seguimientos,
            'satisfactorios': satisfactorios,
            'asignacion': plan.asignacion_evaluacion,
        })

    except Exception as e:
        messages.error(request, f'Error al validar evaluación final: {str(e)}')
        return redirect('evaluations:evaluaciones_finales_rechazadas_rrhh')


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


@login_required
def resultados_finales_admin(request):
    """
    Vista para administradores que muestra todas las evaluaciones finales completadas
    con filtros y estadísticas
    """
    from .models import EvaluacionFinal, PlanMejoraPredefinido
    from django.db.models import Count, Q
    from datetime import datetime, timedelta

    # Verificar permisos de administrador
    if not request.user.is_staff:
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('evaluations:index')

    try:
        # Filtros
        filtro_resultado = request.GET.get('resultado', 'todos')
        filtro_periodo = request.GET.get('periodo', 'todos')
        filtro_busqueda = request.GET.get('busqueda', '').strip()

        # Query base - todas las evaluaciones finales
        evaluaciones_finales = EvaluacionFinal.objects.select_related(
            'plan_mejora',
            'plan_mejora__asignacion_evaluacion',
            'plan_mejora__asignacion_evaluacion__empleado_evaluado',
            'plan_mejora__asignacion_evaluacion__evaluador',
            'plan_mejora__asignacion_evaluacion__evaluacion',
            'plan_mejora__asignacion_evaluacion__evaluacion__tipo_evaluacion',
            'evaluado_por'
        ).prefetch_related(
            'plan_mejora__seguimientos',
            'plan_mejora__asignacion_evaluacion__empleado_evaluado__historialcargo_set',
            'plan_mejora__asignacion_evaluacion__empleado_evaluado__historialcargo_set__cargo',
            'plan_mejora__asignacion_evaluacion__empleado_evaluado__historialcargo_set__cargo__area'
        ).order_by('-fecha_evaluacion')

        # Aplicar filtro de resultado
        if filtro_resultado != 'todos':
            evaluaciones_finales = evaluaciones_finales.filter(resultado=filtro_resultado)

        # Aplicar filtro de período
        if filtro_periodo != 'todos':
            hoy = datetime.now().date()
            if filtro_periodo == 'mes':
                fecha_inicio = hoy - timedelta(days=30)
                evaluaciones_finales = evaluaciones_finales.filter(fecha_evaluacion__gte=fecha_inicio)
            elif filtro_periodo == 'trimestre':
                fecha_inicio = hoy - timedelta(days=90)
                evaluaciones_finales = evaluaciones_finales.filter(fecha_evaluacion__gte=fecha_inicio)
            elif filtro_periodo == 'semestre':
                fecha_inicio = hoy - timedelta(days=180)
                evaluaciones_finales = evaluaciones_finales.filter(fecha_evaluacion__gte=fecha_inicio)
            elif filtro_periodo == 'año':
                fecha_inicio = hoy - timedelta(days=365)
                evaluaciones_finales = evaluaciones_finales.filter(fecha_evaluacion__gte=fecha_inicio)

        # Aplicar búsqueda por nombre de empleado
        if filtro_busqueda:
            evaluaciones_finales = evaluaciones_finales.filter(
                Q(plan_mejora__asignacion_evaluacion__empleado_evaluado__nombres__icontains=filtro_busqueda) |
                Q(plan_mejora__asignacion_evaluacion__empleado_evaluado__apellidos__icontains=filtro_busqueda)
            )

        # Calcular estadísticas
        total_evaluaciones = evaluaciones_finales.count()

        exitosas = evaluaciones_finales.filter(resultado='exitoso').count()
        parciales = evaluaciones_finales.filter(resultado='parcialmente_exitoso').count()
        no_exitosas = evaluaciones_finales.filter(resultado='no_exitoso').count()

        # Calcular porcentajes
        porcentaje_exitosas = round((exitosas / total_evaluaciones * 100), 1) if total_evaluaciones > 0 else 0
        porcentaje_parciales = round((parciales / total_evaluaciones * 100), 1) if total_evaluaciones > 0 else 0
        porcentaje_no_exitosas = round((no_exitosas / total_evaluaciones * 100), 1) if total_evaluaciones > 0 else 0

        # Agregar información de seguimientos a cada evaluación
        evaluaciones_con_info = []
        for eval_final in evaluaciones_finales:
            seguimientos = eval_final.plan_mejora.seguimientos.all().order_by('numero_bimestre')
            satisfactorios = sum(1 for s in seguimientos if s.avance_satisfactorio is True)

            evaluaciones_con_info.append({
                'evaluacion_final': eval_final,
                'plan': eval_final.plan_mejora,
                'asignacion': eval_final.plan_mejora.asignacion_evaluacion,
                'seguimientos': seguimientos,
                'total_seguimientos': seguimientos.count(),
                'seguimientos_satisfactorios': satisfactorios,
            })

        return render(request, 'evaluations/admin/resultados_finales.html', {
            'evaluaciones_con_info': evaluaciones_con_info,
            'total_evaluaciones': total_evaluaciones,
            'exitosas': exitosas,
            'parciales': parciales,
            'no_exitosas': no_exitosas,
            'porcentaje_exitosas': porcentaje_exitosas,
            'porcentaje_parciales': porcentaje_parciales,
            'porcentaje_no_exitosas': porcentaje_no_exitosas,
            'filtro_resultado': filtro_resultado,
            'filtro_periodo': filtro_periodo,
            'filtro_busqueda': filtro_busqueda,
        })

    except Exception as e:
        messages.error(request, f'Error al cargar resultados finales: {str(e)}')
        return redirect('evaluations:index')