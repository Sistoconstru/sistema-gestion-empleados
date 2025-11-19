from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.db import transaction
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
    """Lista todas las evaluaciones donde el usuario es evaluador"""
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
    
    context = {
        'asignacion': asignacion,
        'preguntas': preguntas,
        'respuestas_existentes': respuestas_existentes,
        'empleado': asignacion.empleado_evaluado,
        'evaluacion': asignacion.evaluacion,
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


@login_required
def ver_resultado_evaluacion(request, asignacion_id):
    """Ver los resultados de una evaluación completada"""
    asignacion = get_object_or_404(
        AsignacionEvaluacion.objects.select_related(
            'empleado_evaluado',
            'evaluacion',
            'evaluador'
        ),
        pk=asignacion_id
    )
    
    try:
        # Obtener el empleado del usuario actual
        empleado_usuario = Empleado.objects.get(usuario=request.user)
        
        # Verificar permisos: evaluador, empleado evaluado, o administrador
        if (asignacion.evaluador != empleado_usuario and 
            asignacion.empleado_evaluado.usuario != request.user and
            not (request.user.is_superuser or request.user.has_perm('evaluations.view_asignacionevaluacion'))):
            raise Http404("No tiene permisos para ver esta evaluación")
            
    except Empleado.DoesNotExist:
        # Si no es empleado, verificar si es el empleado evaluado o administrador
        if (asignacion.empleado_evaluado.usuario != request.user and
            not (request.user.is_superuser or request.user.has_perm('evaluations.view_asignacionevaluacion'))):
            raise Http404("No tiene permisos para ver esta evaluación")
        empleado_usuario = None
    
    if asignacion.estado != 'completada':
        messages.warning(request, 'Esta evaluación aún no ha sido completada.')
        return redirect('evaluations:index')
    
    # Obtener resultado
    try:
        resultado = ResultadoEvaluacion.objects.get(asignacion=asignacion)
    except ResultadoEvaluacion.DoesNotExist:
        resultado = None
    
    # Obtener respuestas agrupadas por categoría
    respuestas = RespuestaEvaluacion.objects.filter(
        asignacion=asignacion
    ).select_related('pregunta', 'opcion_seleccionada').order_by('pregunta__orden')
    
    context = {
        'asignacion': asignacion,
        'resultado': resultado,
        'respuestas': respuestas,
        'empleado': asignacion.empleado_evaluado,
        'es_supervisor': empleado_usuario and asignacion.evaluador == empleado_usuario,
    }
    
    return render(request, 'evaluations/resultado.html', context)


# =============================================================================
# VISTAS DE APROBACIÓN ADMINISTRATIVA
# =============================================================================

class EvaluacionesPendientesAprobacionView(LoginRequiredMixin, ListView):
    """Vista para administradores: evaluaciones pendientes de aprobación"""
    template_name = 'evaluations/admin/pendientes_aprobacion.html'
    context_object_name = 'evaluaciones_pendientes'
    paginate_by = 20
    
    def get_queryset(self):
        # Solo para administradores y usuarios con permisos específicos
        if not (self.request.user.is_superuser or self.request.user.has_perm('evaluations.change_asignacionevaluacion')):
            return AsignacionEvaluacion.objects.none()
        
        return AsignacionEvaluacion.objects.filter(
            estado='completada',
            estado_aprobacion='pendiente_aprobacion'  # Evaluaciones pendientes de aprobación
        ).select_related(
            'empleado_evaluado',
            'evaluacion',
            'evaluador',
            'evaluacion__tipo_evaluacion'
        ).order_by('-fecha_completada')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas rápidas
        total_pendientes = self.get_queryset().count()
        total_periodo_prueba = self.get_queryset().filter(
            evaluacion__tipo_evaluacion__codigo='PERIODO_PRUEBA'
        ).count()
        
        # Evaluaciones que requieren atención urgente (más de 3 días sin aprobar)
        from datetime import date, timedelta
        hace_tres_dias = date.today() - timedelta(days=3)
        requieren_atencion = self.get_queryset().filter(
            fecha_completada__date__lt=hace_tres_dias
        ).count()
        
        context.update({
            'total_pendientes': total_pendientes,
            'total_periodo_prueba': total_periodo_prueba,
            'requieren_atencion': requieren_atencion,
            'es_administrador': self.request.user.is_superuser,
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
        return redirect('evaluations:pendientes_aprobacion')
    
    # Validar que el empleado haya aceptado el plan de mejora, excepto si fue reprobado
    evaluacion_reprobada = asignacion.puntaje_total and asignacion.puntaje_total < 14
    
    if not evaluacion_reprobada and not (asignacion.observaciones and '[ACEPTADO_EMPLEADO:' in asignacion.observaciones):
        messages.error(
            request, 
            f'No se puede aprobar la evaluación de {asignacion.empleado_evaluado.nombre_completo}. '
            'El empleado debe ver y aceptar primero los resultados desde su perfil en "Mi Actividad Reciente" '
            'antes de que la evaluación pueda ser aprobada administrativamente.'
        )
        return redirect('evaluations:pendientes_aprobacion')
    
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
            
        return redirect('evaluations:pendientes_aprobacion')
    
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
        
        return redirect('evaluations:pendientes_aprobacion')
    
    return redirect('evaluations:aprobar_evaluacion', asignacion_id=asignacion_id)



@login_required
def ver_resultados_evaluacion(request, asignacion_id):
    """Vista para que el empleado vea sus resultados preliminares"""
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
        
        # Obtener resultado
        try:
            resultado = ResultadoEvaluacion.objects.get(asignacion=asignacion)
        except ResultadoEvaluacion.DoesNotExist:
            messages.error(request, 'Los resultados aún no están disponibles.')
            return redirect('evaluations:index')
        
        context = {
            'asignacion': asignacion,
            'resultado': resultado,
            'empleado': asignacion.empleado_evaluado,
            'evaluacion': asignacion.evaluacion,
            'puede_aceptar': asignacion.estado_aprobacion in ['pendiente_aprobacion', 'aprobada']
        }
        
        return render(request, 'evaluations/empleado/ver_resultados.html', context)
        
    except AsignacionEvaluacion.DoesNotExist:
        messages.error(request, 'Evaluación no encontrada.')
        return redirect('evaluations:index')


@login_required
def aceptar_resultados_evaluacion(request, asignacion_id):
    """Vista para que el empleado acepte los resultados de su evaluación"""
    try:
        asignacion = AsignacionEvaluacion.objects.get(pk=asignacion_id)
        
        # Verificar que es el empleado evaluado
        if request.user.empleado != asignacion.empleado_evaluado:
            messages.error(request, 'No puede aceptar resultados de otra persona.')
            return redirect('evaluations:index')
        
        if request.method == 'POST':
            comentarios_empleado = request.POST.get('comentarios_empleado', '').strip()
            
            # Marcar como aceptada por el empleado con marcador específico
            fecha_aceptacion = timezone.now().strftime("%d/%m/%Y %H:%M")
            observaciones_aceptacion = f"[ACEPTADO_EMPLEADO:{fecha_aceptacion}]"
            if comentarios_empleado:
                observaciones_aceptacion += f" - Comentarios: {comentarios_empleado}"
            
            asignacion.observaciones = observaciones_aceptacion
            asignacion.save()
            
            messages.success(
                request, 
                'Ha aceptado los resultados de su evaluación. Los resultados han sido '
                'registrados y serán considerados en su proceso de continuidad.'
            )
            
            return redirect('evaluations:index')
        
        return render(request, 'evaluations/empleado/aceptar_resultados.html', {
            'asignacion': asignacion
        })
        
    except AsignacionEvaluacion.DoesNotExist:
        messages.error(request, 'Evaluación no encontrada.')
        return redirect('evaluations:index')


    return '\n'.join(areas_mejora)