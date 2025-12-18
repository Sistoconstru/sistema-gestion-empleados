# ...imports...

# apps/training/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from django.utils.safestring import mark_safe
from django.db.models import Q, Count, Avg, Sum
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
import logging
import json

from .models import (Capacitacion, InscripcionCapacitacion, TipoCapacitacion, 
                     CapacitacionCargo, ModuloCapacitacion, ProgresoCapacitacion,
                     Leccion, ContenidoLeccion, QuizLeccion, PreguntaQuiz, 
                     OpcionPreguntaQuiz, IntentoQuiz, RespuestaQuiz)
from .forms import CapacitacionForm #InscripcionCapacitacionForm
from apps.employees.models import Empleado

logger = logging.getLogger(__name__)

class PlayerPreviewView(LoginRequiredMixin, TemplateView):
    template_name = 'training/player.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Solo admins/staff pueden acceder
        if not self.request.user.is_staff:
            context['object'] = None
            context['mensaje_error'] = 'No autorizado'
            return context

        # Obtener la capacitación y simular inscripción
        from .models import Capacitacion, ContenidoLeccion
        capacitacion = get_object_or_404(Capacitacion, id=self.kwargs['pk'])
        # Simular un objeto de inscripción solo para mostrar la estructura
        class FakeInscripcion:
            def __init__(self, capacitacion):
                self.capacitacion = capacitacion
                self.pk = capacitacion.pk
        inscripcion = FakeInscripcion(capacitacion)
        context['object'] = inscripcion

        # Buscar el primer contenido disponible
        contenido_actual = ContenidoLeccion.objects.filter(
            leccion__modulo__capacitacion=capacitacion,
            leccion__modulo__activo=True
        ).select_related(
            'leccion', 'leccion__modulo', 'tipo_contenido'
        ).first()
        context['contenido_actual'] = contenido_actual

        # Simular progreso y navegación
        context['progreso_actual'] = type('FakeProgreso', (), {'puede_ver': True, 'completado': False})()
        context['contenido_anterior'] = None
        context['contenido_siguiente'] = None
        context['contenidos_completados'] = []
        context['evaluacion_pendiente'] = False
        context['modulos_evaluacion'] = {}
        context['solo_lectura'] = True
        return context

class CapacitacionListView(LoginRequiredMixin, ListView):
    """Vista para administradores - gestión de capacitaciones"""
    model = Capacitacion
    template_name = 'training/capacitacion_list.html'
    context_object_name = 'capacitaciones'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Capacitacion.objects.select_related('tipo').order_by('-fecha_creacion')
        
        # Aplicar filtros
        estado = self.request.GET.get('estado')
        tipo = self.request.GET.get('tipo')
        
        if estado:
            if estado == 'activa':
                queryset = queryset.filter(activa=True)
            elif estado == 'inactiva':
                queryset = queryset.filter(activa=False)
        
        if tipo:
            queryset = queryset.filter(tipo_id=tipo)
            
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar tipos de capacitación para filtros
        context['tipos'] = TipoCapacitacion.objects.all()

        # Estadísticas rápidas
        context['total_capacitaciones'] = Capacitacion.objects.count()
        context['total_obligatorias'] = Capacitacion.objects.filter(tipo__codigo='OBLIGATORIA').count()
        from apps.employees.models import Empleado
        context['total_empleados'] = Empleado.objects.count()
        context['total_horas'] = Capacitacion.objects.aggregate(total_horas=Sum('duracion_estimada_horas'))['total_horas'] or 0

        return context

class CatalogoCapacitacionesView(LoginRequiredMixin, ListView):
    """Vista del catálogo de capacitaciones para empleados"""
    model = Capacitacion
    template_name = 'training/catalogo.html'
    context_object_name = 'capacitaciones'
    paginate_by = 12

    def get_queryset(self):
        # Obtener solo capacitaciones activas
        queryset = Capacitacion.objects.filter(activa=True)
        
        # Excluir capacitaciones en las que ya está inscrito
        empleado = get_object_or_404(Empleado, usuario=self.request.user)
        inscripciones = InscripcionCapacitacion.objects.filter(empleado=empleado)
        queryset = queryset.exclude(inscripciones__in=inscripciones)
        
        # Aplicar filtros
        tipo = self.request.GET.get('tipo')
        nivel = self.request.GET.get('nivel')
        duracion = self.request.GET.get('duracion')
        
        if tipo:
            if tipo == 'interno':
                queryset = queryset.filter(proveedor_externo__isnull=True)
            elif tipo == 'externo':
                queryset = queryset.filter(proveedor_externo__isnull=False)
                
        if nivel:
            queryset = queryset.filter(nivel_dificultad=nivel)
            
        if duracion:
            queryset = queryset.filter(duracion=duracion)
            
        return queryset.select_related('tipo').order_by('nombre')

@login_required
@require_http_methods(["GET", "POST"])
def inscribir_capacitacion(request, pk):
    """Vista para procesar la inscripción a una capacitación"""
    try:
        logger.info(f'Iniciando proceso de inscripción para capacitación {pk}')
        capacitacion = get_object_or_404(Capacitacion, id=pk)
        
        if not capacitacion.activa:
            messages.error(request, 'Esta capacitación no está disponible para inscripción.')
            return redirect('training:catalogo')
            
        empleado = get_object_or_404(Empleado, usuario=request.user)
        logger.info(f'Empleado encontrado: {empleado.id} - {empleado.nombre_completo}')
        
        # Verificar si ya está inscrito
        inscripcion_existente = InscripcionCapacitacion.objects.filter(
            empleado=empleado, 
            capacitacion=capacitacion
        ).first()
        
        if inscripcion_existente:
            messages.warning(request, 'Ya estás inscrito en esta capacitación.')
            return redirect('training:catalogo')
            
        if request.method == 'POST':
            try:
                with transaction.atomic():
                    # Verificar si ya existe una inscripción (doble verificación dentro de la transacción)
                    if InscripcionCapacitacion.objects.filter(empleado=empleado, capacitacion=capacitacion).exists():
                        messages.warning(request, 'Ya estás inscrito en esta capacitación.')
                        return redirect('training:catalogo')
                    
                    # Verificar el tipo de capacitación
                    es_externa = capacitacion.es_externa()
                    now = timezone.now()

                    # Configuración inicial por defecto
                    estado_inicial = 'no_iniciado'
                    fecha_inicio = None
                    fecha_fin = None
                    porcentaje = 0

                    # Manejar capacitaciones externas
                    if es_externa:
                        if capacitacion.permite_autocompletado:
                            estado_inicial = 'no_iniciado'
                        else:
                            estado_inicial = 'pendiente_validacion'
                    
                    # Crear la inscripción
                    inscripcion = InscripcionCapacitacion.objects.create(
                        empleado=empleado,
                        capacitacion=capacitacion,
                        fecha_inscripcion=now,
                        fecha_inicio=fecha_inicio,
                        fecha_finalizacion=fecha_fin,
                        estado=estado_inicial,
                        obligatoria=False,
                        inscrito_por=request.user,
                        porcentaje_completado=porcentaje
                    )
                    
                    messages.success(request, 'Inscripción procesada correctamente.')
                    return redirect('training:mis_capacitaciones')
                    
            except Exception as e:
                logger.error(f'Error durante la transacción de inscripción: {str(e)}')
                messages.error(request, 'Ocurrió un error al procesar tu inscripción.')
                return redirect('training:catalogo')
                
        return render(request, 'training/inscripcion_form.html', {'capacitacion': capacitacion})
        
    except Exception as e:
        logger.error(f'Error en inscripción: {str(e)}')
        messages.error(request, 'Ocurrió un error al procesar la inscripción.')
        return redirect('training:catalogo')


class QuizView(LoginRequiredMixin, DetailView):
    """Vista para mostrar y tomar un quiz"""
    model = QuizLeccion
    template_name = 'training/quiz.html'
    context_object_name = 'quiz'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.get_object()
        usuario = self.request.user

        # Lógica de prerequisito: solo permitir tomar el quiz si todos los contenidos de la lección asociada al quiz están completados
        leccion = quiz.leccion
        contenidos_leccion = ContenidoLeccion.objects.filter(
            leccion=leccion,
            leccion__activa=True
        )
        total_contenidos = contenidos_leccion.count()
        empleado = getattr(usuario, 'empleado', None)
        puede_tomar_quiz = False
        mensaje_prerrequisito = ''
        if not empleado:
            mensaje_prerrequisito = 'No se encontró el empleado asociado a este usuario.'
        else:
            inscripcion = InscripcionCapacitacion.objects.filter(empleado=empleado, capacitacion=leccion.modulo.capacitacion).first()
            if not inscripcion:
                mensaje_prerrequisito = 'No tienes inscripción activa en esta capacitación.'
            else:
                completados = ProgresoCapacitacion.objects.filter(
                    inscripcion=inscripcion,
                    contenido__leccion=leccion,
                    completado=True
                ).count()
                puede_tomar_quiz = (completados == total_contenidos and total_contenidos > 0)
                if not puede_tomar_quiz:
                    mensaje_prerrequisito = 'Debes completar todos los contenidos de la lección antes de realizar la evaluación.'
        context['puede_tomar_quiz'] = puede_tomar_quiz
        context['mensaje_prerrequisito'] = mensaje_prerrequisito

        # Obtener intentos previos
        context['intentos_previos'] = IntentoQuiz.objects.filter(
            quiz=quiz,
            usuario=usuario
        ).order_by('-fecha_inicio')

        # Verificar si quedan intentos disponibles
        intentos_realizados = context['intentos_previos'].count()
        context['intentos_restantes'] = quiz.intentos_maximos - intentos_realizados if quiz.intentos_maximos > 0 else None

        # Verificar si ya aprobó
        context['ya_aprobo'] = context['intentos_previos'].filter(aprobado=True).exists()

        # Obtener todas las preguntas con sus opciones
        context['preguntas'] = quiz.preguntas.prefetch_related('opciones').all()

        return context

    def post(self, request, *args, **kwargs):
        """Procesar inicio de intento de quiz"""
        quiz = self.get_object()
        usuario = request.user
        leccion = quiz.leccion
        empleado = getattr(usuario, 'empleado', None)
        puede_tomar = False
        if empleado:
            inscripcion = InscripcionCapacitacion.objects.filter(empleado=empleado, capacitacion=leccion.modulo.capacitacion).first()
            if inscripcion:
                # Solo verificar que los contenidos estén completados, no la evaluación
                contenidos_leccion = ContenidoLeccion.objects.filter(leccion=leccion, leccion__activa=True)
                total_contenidos = contenidos_leccion.count()
                completados = ProgresoCapacitacion.objects.filter(
                    inscripcion=inscripcion,
                    contenido__leccion=leccion,
                    completado=True
                ).count()
                puede_tomar = (completados == total_contenidos and total_contenidos > 0)
        if not puede_tomar:
            return JsonResponse({
                'status': 'error',
                'message': 'Debes completar todos los contenidos de la lección antes de realizar la evaluación.'
            }, status=403)
        # Verificar si puede iniciar un nuevo intento
        intentos_previos = IntentoQuiz.objects.filter(
            quiz=quiz,
            usuario=usuario
        ).count()
        if quiz.intentos_maximos > 0 and intentos_previos >= quiz.intentos_maximos:
            messages.error(request, 'Has alcanzado el número máximo de intentos permitidos.')
            return redirect('training:quiz_resultado', pk=quiz.pk)
        # Crear nuevo intento
        intento = IntentoQuiz.objects.create(
            quiz=quiz,
            usuario=usuario
        )
        return JsonResponse({
            'status': 'success',
            'intento_id': intento.id
        })

@login_required
@require_http_methods(["POST"])
def guardar_respuesta_quiz(request, intento_id):
    """API endpoint para guardar respuestas del quiz"""
    intento = get_object_or_404(IntentoQuiz, id=intento_id, usuario=request.user)
    
    if intento.fecha_fin:
        return JsonResponse({
            'status': 'error',
            'message': 'Este intento ya ha finalizado'
        }, status=400)
    
    try:
        data = json.loads(request.body)
        pregunta_id = data.get('pregunta_id')
        opcion_id = data.get('opcion_id')
        
        pregunta = get_object_or_404(PreguntaQuiz, id=pregunta_id, quiz=intento.quiz)
        opcion = get_object_or_404(OpcionPreguntaQuiz, id=opcion_id, pregunta=pregunta)
        
        # Guardar o actualizar respuesta
        respuesta, created = RespuestaQuiz.objects.update_or_create(
            intento=intento,
            pregunta=pregunta,
            defaults={
                'opcion_seleccionada': opcion,
                'es_correcta': opcion.es_correcta
            }
        )
        
        return JsonResponse({
            'status': 'success',
            'es_correcta': opcion.es_correcta
        })
        
    except Exception as e:
        logger.error(f'Error al guardar respuesta: {str(e)}')
        return JsonResponse({
            'status': 'error',
            'message': 'Error al procesar la respuesta'
        }, status=400)

@login_required
@require_http_methods(["POST"])
def finalizar_quiz(request, intento_id):
    """Finalizar intento de quiz y calcular resultado"""
    intento = get_object_or_404(IntentoQuiz, id=intento_id, usuario=request.user)
    
    if intento.fecha_fin:
        return JsonResponse({
            'status': 'error',
            'message': 'Este intento ya ha finalizado'
        }, status=400)
    
    try:
        with transaction.atomic():
            # Calcular puntaje
            total_preguntas = intento.quiz.preguntas.count()
            respuestas_correctas = intento.respuestas.filter(es_correcta=True).count()
            
            if total_preguntas > 0:
                puntaje = (respuestas_correctas / total_preguntas) * 100
            else:
                puntaje = 0
            
            # Actualizar intento
            intento.fecha_fin = timezone.now()
            intento.puntaje_obtenido = puntaje
            intento.tiempo_utilizado = (intento.fecha_fin - intento.fecha_inicio).seconds
            intento.aprobado = puntaje >= intento.quiz.porcentaje_aprobacion
            intento.save()

            # Si el quiz fue aprobado, marcar la lección como completada en ProgresoCapacitacion
            if intento.aprobado:
                leccion = intento.quiz.leccion
                empleado = getattr(request.user, 'empleado', None)
                if empleado:
                    inscripcion = InscripcionCapacitacion.objects.filter(empleado=empleado, capacitacion=leccion.modulo.capacitacion).first()
                    if inscripcion:
                        # Marcar todos los contenidos de la lección como completados
                        contenidos = ContenidoLeccion.objects.filter(leccion=leccion)
                        for contenido in contenidos:
                            progreso, _ = ProgresoCapacitacion.objects.get_or_create(inscripcion=inscripcion, contenido=contenido)
                            if not progreso.completado:
                                progreso.completado = True
                                progreso.fecha_completado = timezone.now()
                                progreso.save()
                        # Si la lección es la única del módulo y está aprobada, marcar el módulo como completado
                        modulo = leccion.modulo
                        lecciones_modulo = modulo.leccion_set.filter(activa=True)
                        todas_completadas = all(l.esta_completada(inscripcion) for l in lecciones_modulo)
                        if todas_completadas:
                            # Aquí podrías actualizar un campo de progreso de módulo si existe, o simplemente permitir el acceso inmediato al siguiente módulo
                            pass  # Si tienes un modelo de progreso de módulo, actualízalo aquí

            return JsonResponse({
                'status': 'success',
                'redirect_url': reverse_lazy('training:quiz_resultado', kwargs={'pk': intento.quiz.pk})
            })
            
    except Exception as e:
        logger.error(f'Error al finalizar quiz: {str(e)}')
        return JsonResponse({
            'status': 'error',
            'message': 'Error al procesar el resultado'
        }, status=400)

class QuizResultadoView(LoginRequiredMixin, DetailView):
    """Vista para mostrar resultados de quiz"""
    model = QuizLeccion
    template_name = 'training/quiz_resultado.html'
    context_object_name = 'quiz'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.get_object()
        usuario = self.request.user

        # Obtener todos los intentos del usuario
        intentos = IntentoQuiz.objects.filter(
            quiz=quiz,
            usuario=usuario
        ).order_by('-fecha_inicio')

        context['intentos'] = intentos

        mejor_intento = None
        if intentos.exists():
            # Buscar el intento con mayor puntaje
            mejor_intento = max(intentos, key=lambda i: i.puntaje_obtenido or 0)
            context['mejor_intento'] = mejor_intento
            # Obtener detalles de respuestas del mejor intento
            context['respuestas'] = RespuestaQuiz.objects.filter(
                intento=mejor_intento
            ).select_related('pregunta', 'opcion_seleccionada')

        # Agregar la inscripción del usuario para la capacitación de la lección
        from apps.employees.models import Empleado
        from .models import InscripcionCapacitacion
        try:
            empleado = Empleado.objects.get(usuario=usuario)
            inscripcion = InscripcionCapacitacion.objects.get(
                empleado=empleado,
                capacitacion=quiz.leccion.modulo.capacitacion
            )
            context['inscripcion'] = inscripcion
        except Exception:
            context['inscripcion'] = None

        return context
        
        if not capacitacion.activa:
            messages.error(request, 'Esta capacitación no está disponible para inscripción.')
            return redirect('training:catalogo')
            
        empleado = get_object_or_404(Empleado, usuario=request.user)
        logger.info(f'Empleado encontrado: {empleado.id} - {empleado.nombre_completo}')
        
        # Verificar si ya está inscrito
        inscripcion_existente = InscripcionCapacitacion.objects.filter(
            empleado=empleado, 
            capacitacion=capacitacion
        ).first()
        
        if inscripcion_existente:
            messages.warning(request, 'Ya estás inscrito en esta capacitación.')
            return redirect('training:catalogo')
            
        if request.method == 'POST':
            try:
                with transaction.atomic():
                    # Verificar si ya existe una inscripción (doble verificación dentro de la transacción)
                    if InscripcionCapacitacion.objects.filter(empleado=empleado, capacitacion=capacitacion).exists():
                        messages.warning(request, 'Ya estás inscrito en esta capacitación.')
                        return redirect('training:catalogo')
                    
                    # Verificar el tipo de capacitación
                    es_externa = capacitacion.es_externa()
                    now = timezone.now()

                    # Configuración inicial por defecto
                    estado_inicial = 'no_iniciado'
                    fecha_inicio = None
                    fecha_fin = None
                    porcentaje = 0

                    # Manejar capacitaciones externas
                    if es_externa:
                        if capacitacion.permite_autocompletado:
                            estado_inicial = 'no_iniciado'
                        else:
                            estado_inicial = 'pendiente_validacion'
                    
                    # Manejar capacitaciones internas
                    else:
                        try:
                            with transaction.atomic():
                                # Verificar si tiene módulos y contenido
                                modulos = ModuloCapacitacion.objects.filter(
                                    capacitacion=capacitacion,
                                    activo=True
                                ).prefetch_related(
                                    'leccion_set__contenidoleccion_set'
                                )
                                
                                tiene_contenido = False
                                for modulo in modulos:
                                    # Verificar si hay lecciones activas
                                    lecciones_activas = modulo.leccion_set.filter(activa=True)
                                    for leccion in lecciones_activas:
                                        # Verificar si hay contenido en las lecciones
                                        if leccion.contenidoleccion_set.exists():
                                            tiene_contenido = True
                                            break
                                    if tiene_contenido:
                                        break
                                
                                if not modulos.exists() or not tiene_contenido:
                                    # Si no tiene módulos o contenido, se marca como completada
                                    estado_inicial = 'completado'
                                    fecha_inicio = now
                                    fecha_fin = now
                                    porcentaje = 100
                                else:
                                    estado_inicial = 'no_iniciado'
                                
                        except Exception as e:
                            logger.error(f'Error al verificar módulos/contenido: {str(e)}')

                    # Crear la inscripción
                    inscripcion = InscripcionCapacitacion.objects.create(
                        empleado=empleado,
                        capacitacion=capacitacion,
                        fecha_inscripcion=now,
                        fecha_inicio=fecha_inicio,
                        fecha_finalizacion=fecha_fin,
                        estado=estado_inicial,
                        obligatoria=False,
                        inscrito_por=request.user,
                        porcentaje_completado=porcentaje
                    )
                    
                    logger.info(f'Inscripción creada con ID: {inscripcion.id} - Estado: {estado_inicial}')
                    
                    # Crear registros de progreso solo para capacitaciones internas
                    if not es_externa:
                        try:
                            # Obtener todos los contenidos de una vez de manera eficiente
                            contenidos = ContenidoLeccion.objects.filter(
                                leccion__modulo__capacitacion=capacitacion,
                                leccion__modulo__activo=True,
                                leccion__activa=True
                            ).select_related(
                                'leccion',
                                'leccion__modulo'
                            )
                            
                            if contenidos.exists():
                                # Crear registros de progreso en batch
                                progresos = [
                                    ProgresoCapacitacion(
                                        inscripcion=inscripcion,
                                        contenido=contenido,
                                        completado=False,
                                        tiempo_dedicado_segundos=0,
                                        porcentaje_visto=0
                                    )
                                    for contenido in contenidos
                                ]
                                
                                # Crear todos los registros de progreso de una vez
                                ProgresoCapacitacion.objects.bulk_create(progresos)
                                logger.info(f'Creados {len(progresos)} registros de progreso para capacitación ID: {capacitacion.id}')
                                
                                # Actualizar estado de inscripción
                                inscripcion.estado = 'no_iniciado'
                                inscripcion.save()
                                logger.info('Inscripción creada con contenidos, estado: no_iniciado')
                            else:
                                # Si no hay contenidos, marcar como completada
                                inscripcion.estado = 'completado'
                                inscripcion.fecha_inicio = now
                                inscripcion.fecha_finalizacion = now
                                inscripcion.porcentaje_completado = 100
                                inscripcion.save()
                                logger.info('No se encontraron contenidos activos. Capacitación marcada como completada.')
                                
                        except Exception as e:
                            logger.error(f'Error al crear registros de progreso: {str(e)}')
                            # No revertimos la inscripción, solo registramos el error
                    
                    if request.user.is_staff:
                        messages.success(request, f'Se ha inscrito al empleado {empleado.nombre_completo} en la capacitación: {capacitacion.nombre}')
                        if capacitacion.es_externa():
                            messages.info(request, 'La inscripción quedará pendiente hasta que se valide el certificado del proveedor externo')
                        return redirect('training:capacitacion_detail', pk=capacitacion.id)
                    else:
                        messages.success(request, f'Te has inscrito exitosamente en la capacitación: {capacitacion.nombre}')
                        if capacitacion.es_externa():
                            messages.info(request, 'Por favor realiza la inscripción en el sitio del proveedor y presenta el certificado para validar tu inscripción')
                            if capacitacion.url_inscripcion_externa:
                                return redirect(capacitacion.url_inscripcion_externa)
                        return redirect('training:mis_capacitaciones')
                        
            except Exception as e:
                logger.error(f'Error durante la transacción de inscripción: {str(e)}\nDetalles: {repr(e)}')
                if 'IntegrityError' in str(type(e)):
                    messages.error(request, 'Ya existe una inscripción para esta capacitación.')
                else:
                    messages.error(request, 'Ocurrió un error al procesar tu inscripción. Por favor intenta nuevamente.')
                return redirect('training:catalogo')

class MisCapacitacionesView(LoginRequiredMixin, ListView):
    """Vista para empleados - sus capacitaciones"""
    model = InscripcionCapacitacion
    template_name = 'training/mis_capacitaciones.html'
    context_object_name = 'inscripciones'
    paginate_by = 12
    
    def get_queryset(self):
        # Obtiene las inscripciones del empleado actual
        try:
            empleado = Empleado.objects.get(usuario=self.request.user)
            return InscripcionCapacitacion.objects.filter(
                empleado=empleado
            ).select_related('capacitacion', 'capacitacion__tipo').order_by('-fecha_inscripcion')
        except Empleado.DoesNotExist:
            return InscripcionCapacitacion.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inscripciones = self.get_queryset()
        
        # Estadísticas del empleado
        context.update({
            'completadas': inscripciones.filter(estado='aprobado').count(),
            'en_progreso': inscripciones.filter(estado='en_progreso').count(),
                'horas_acumuladas': sum([
                    getattr(i.capacitacion, 'duracion_estimada_horas', 0) or 0
                    for i in inscripciones.filter(estado='aprobado')
                ])
        })
        
        # Capacitaciones recientes
        try:
            empleado = Empleado.objects.get(usuario=self.request.user)
            context['capacitaciones'] = InscripcionCapacitacion.objects.filter(
                empleado=empleado
            ).select_related(
                'capacitacion',
                'inscrito_por',
                'aprobado_por'
            ).prefetch_related(
                'capacitacion__modulocapacitacion_set'
            ).order_by(
                '-fecha_inscripcion'
            )
            # Inicializar porcentaje_completado en 0 si es None y calcular total de lecciones
            for insc in context['capacitaciones']:
                if insc.porcentaje_completado is None:
                    insc.porcentaje_completado = 0

                # Calcular total de lecciones para capacitaciones internas
                if not insc.capacitacion.es_externa():
                    total_lecciones = 0
                    for modulo in insc.capacitacion.modulocapacitacion_set.all():
                        total_lecciones += modulo.leccion_set.count()
                    insc.total_lecciones = total_lecciones
                else:
                    insc.total_lecciones = 0
        except Exception as e:
            logger.error(f"Error obteniendo capacitaciones: {e}")
            context['capacitaciones'] = []
        
        return context

class CatalogoCapacitacionesView(LoginRequiredMixin, ListView):
    """Catálogo de capacitaciones disponibles para inscripción"""
    model = Capacitacion
    template_name = 'training/catalogo.html'
    context_object_name = 'capacitaciones'
    paginate_by = 15
    
    def get_queryset(self):
        try:
            empleado = Empleado.objects.get(usuario=self.request.user)
            # Obtener IDs de capacitaciones ya asignadas o inscritas
            capacitaciones_asignadas = InscripcionCapacitacion.objects.filter(
                empleado=empleado
            ).values_list('capacitacion_id', flat=True)
        except Empleado.DoesNotExist:
            capacitaciones_asignadas = []

        # Solo capacitaciones libres y externas activas, excluyendo las ya asignadas
        queryset = Capacitacion.objects.select_related(
            'tipo', 'proveedor_externo'
        ).filter(
            activa=True,
            tipo__permite_inscripcion_libre=True
        ).exclude(
            id__in=capacitaciones_asignadas
        )
        
        # Filtrar por tipo (interna/externa)
        tipo = self.request.GET.get('tipo')
        if tipo == 'interno':
            queryset = queryset.filter(proveedor_externo__isnull=True)
        elif tipo == 'externo':
            queryset = queryset.filter(proveedor_externo__isnull=False)
            
        # Filtrar por nivel
        nivel = self.request.GET.get('nivel')
        if nivel:
            queryset = queryset.filter(nivel_dificultad=nivel)
            
        # Filtrar por duración
        duracion = self.request.GET.get('duracion')
        if duracion == 'corta':
            queryset = queryset.filter(duracion_estimada_horas__lt=4)
        elif duracion == 'media':
            queryset = queryset.filter(duracion_estimada_horas__range=(4, 8))
        elif duracion == 'larga':
            queryset = queryset.filter(duracion_estimada_horas__gt=8)
        
        return queryset.order_by('-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CapacitacionDetailView(LoginRequiredMixin, DetailView):
    """Detalle de una capacitación"""
    model = Capacitacion
    context_object_name = 'capacitacion'
    
    def get_template_names(self):
        # Si el usuario viene de mis capacitaciones o del catálogo, usar vista de empleado
        referer = self.request.META.get('HTTP_REFERER', '')
        if 'mis-capacitaciones' in referer or 'catalogo' in referer or not (self.request.user.is_staff or self.request.user.is_superuser):
            return ['training/capacitacion_detail_employee.html']
        # Para administradores y superusuarios, mostrar vista administrativa
        return ['training/capacitacion_detail.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        capacitacion = self.get_object()
        
        # Obtener inscripciones
        inscripciones = InscripcionCapacitacion.objects.filter(capacitacion=capacitacion)
        
        if self.request.user.is_staff:
            # Obtener empleados que no están inscritos en esta capacitación
            empleados_inscritos = inscripciones.values_list('empleado_id', flat=True)
            empleados_inscritos = list(empleados_inscritos)  # Convertir a lista para asegurar que sean IDs válidos
            
            # Primero filtrar por estado y luego excluir los ya inscritos
            context['empleados_disponibles'] = Empleado.objects.filter(
                estado__codigo='999'  # Filtrar por el código real del estado activo
            ).exclude(
                id__in=empleados_inscritos if empleados_inscritos else []
            ).select_related('estado').order_by('apellidos', 'nombres')
            
            # Estadísticas para admin
            context['total_inscritos'] = inscripciones.count()
            context['inscritos_pendientes'] = inscripciones.filter(estado='pendiente_validacion').count()
            context['inscritos_activos'] = inscripciones.exclude(
                estado__in=['pendiente_validacion', 'cancelado', 'completado', 'aprobado']
            ).count()
            context['completados'] = inscripciones.filter(estado__in=['completado', 'aprobado']).count()
            
            # Lista de inscripciones pendientes para cursos externos
            if capacitacion.es_externa():
                # Solicitudes pendientes de aprobación inicial
                context['inscripciones_pendientes_aprobacion'] = inscripciones.filter(
                    estado='pendiente_validacion'
                ).select_related('empleado').order_by('-fecha_inscripcion')

                # Inscripciones en progreso esperando certificado
                context['inscripciones_esperando_certificado'] = inscripciones.filter(
                    estado='en_progreso'
                ).select_related('empleado').order_by('fecha_inicio')

            # Listado completo de empleados inscritos para la tabla
            context['empleados_inscritos_list'] = InscripcionCapacitacion.objects.filter(
                capacitacion=capacitacion
            ).select_related(
                'empleado',
                'empleado__estado'
            ).prefetch_related(
                'empleado__historialcargo_set__cargo',
                'empleado__historialcargo_set__cargo__area'
            ).order_by('-fecha_inscripcion')

            context['total_inscritos'] = inscripciones.count()
            context['inscritos_pendientes'] = inscripciones.filter(estado='pendiente_validacion').count()
            context['inscritos_activos'] = inscripciones.exclude(
                estado__in=['pendiente_validacion', 'cancelado', 'completado', 'aprobado']
            ).count()
            context['completados'] = inscripciones.filter(estado__in=['completado', 'aprobado']).count()
        else:
            # Obtener la inscripción del empleado si existe
            try:
                empleado = Empleado.objects.get(usuario=self.request.user)
                context['inscripcion'] = InscripcionCapacitacion.objects.get(
                    empleado=empleado,
                    capacitacion=capacitacion
                )
            except (Empleado.DoesNotExist, InscripcionCapacitacion.DoesNotExist):
                context['inscripcion'] = None

        # Estadísticas generales (disponibles para todos los usuarios)
        context['total_inscritos'] = inscripciones.count()
        context['en_progreso'] = inscripciones.filter(estado='en_progreso').count()
        context['completados'] = inscripciones.filter(estado__in=['completado', 'aprobado']).count()
        
        # Calcular porcentajes para las barras de progreso
        total = context['total_inscritos']
        if total > 0:
            context['porcentaje_progreso'] = (context['en_progreso'] / total) * 100
            context['porcentaje_completados'] = (context['completados'] / total) * 100
        else:
            context['porcentaje_progreso'] = 0
            context['porcentaje_completados'] = 0
        
        # Cargos asignados
        context['cargos_asignados'] = CapacitacionCargo.objects.filter(
            capacitacion=capacitacion,
            activa=True
        ).select_related('cargo', 'cargo__area').order_by('cargo__nombre')
        
        # Verificar si el usuario está inscrito
        try:
            empleado = Empleado.objects.get(usuario=self.request.user)
            inscripcion = InscripcionCapacitacion.objects.filter(
                empleado=empleado,
                capacitacion=capacitacion
            ).first()
            context['inscripcion'] = inscripcion
        except Empleado.DoesNotExist:
            context['inscripcion'] = None
        
        # Módulos y lecciones si es interna
        if capacitacion.requiere_modulos():
            context['modulos'] = capacitacion.modulocapacitacion_set.filter(
                activo=True
            ).prefetch_related('leccion_set').order_by('orden')
        
        return context

@login_required
@require_http_methods(["POST"])
def aprobar_solicitud_inscripcion(request, pk):
    """Aprobar solicitud inicial de inscripción en capacitación externa"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para realizar esta acción')
        return redirect('training:catalogo')

    inscripcion = get_object_or_404(InscripcionCapacitacion, pk=pk)

    if inscripcion.estado != 'pendiente_validacion':
        messages.warning(request, 'Esta inscripción no está pendiente de aprobación')
        return redirect('training:capacitacion_detail', pk=inscripcion.capacitacion.id)

    try:
        with transaction.atomic():
            # Cambiar estado a en_progreso para que el empleado pueda acceder al curso
            inscripcion.estado = 'en_progreso'
            inscripcion.fecha_inicio = timezone.now()
            inscripcion.aprobada_supervisor = True
            inscripcion.aprobado_por = request.user
            inscripcion.observaciones_admin = request.POST.get('observaciones', '')
            inscripcion.save()

            messages.success(
                request,
                f'✅ Solicitud aprobada. {inscripcion.empleado.nombre_completo} ya puede acceder al curso externo.'
            )

    except Exception as e:
        logger.error(f'Error al aprobar solicitud {pk}: {str(e)}')
        messages.error(request, 'Ocurrió un error al aprobar la solicitud')

    return redirect('training:capacitacion_detail', pk=inscripcion.capacitacion.id)

@login_required
@require_http_methods(["POST"])
def validar_certificado_externo(request, pk):
    """Validar certificado de finalización de capacitación externa"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para realizar esta acción')
        return redirect('training:catalogo')

    inscripcion = get_object_or_404(InscripcionCapacitacion, pk=pk)

    if inscripcion.estado not in ['en_progreso', 'no_iniciado']:
        messages.warning(request, 'Esta inscripción no está en estado válido para certificar')
        return redirect('training:capacitacion_detail', pk=inscripcion.capacitacion.id)

    try:
        with transaction.atomic():
            # Guardar el certificado si se proporcionó
            if request.FILES.get('certificado'):
                inscripcion.certificado_externo = request.FILES['certificado']

            # Actualizar estado a completado/aprobado
            inscripcion.estado = 'aprobado'
            inscripcion.fecha_finalizacion = timezone.now()
            inscripcion.porcentaje_completado = 100
            inscripcion.puntaje_final = request.POST.get('puntaje_final', 100)
            inscripcion.validado_por_admin = True
            inscripcion.observaciones_admin = request.POST.get('observaciones', '')
            inscripcion.save()

            messages.success(
                request,
                f'✅ Certificado validado. {inscripcion.empleado.nombre_completo} ha completado la capacitación.'
            )

    except Exception as e:
        logger.error(f'Error al validar certificado {pk}: {str(e)}')
        messages.error(request, 'Ocurrió un error al validar el certificado')

    return redirect('training:capacitacion_detail', pk=inscripcion.capacitacion.id)

@login_required
@require_http_methods(["POST"])
def validar_inscripcion(request, pk):
    """DEPRECATED: Usar aprobar_solicitud_inscripcion o validar_certificado_externo"""
    # Mantener por compatibilidad, redirigir a aprobar_solicitud_inscripcion
    return aprobar_solicitud_inscripcion(request, pk)

@login_required
@require_http_methods(["POST"])
def rechazar_inscripcion(request, inscripcion_id):
    """Rechazar inscripción en capacitación externa"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para realizar esta acción')
        return redirect('training:catalogo')
        
    inscripcion = get_object_or_404(InscripcionCapacitacion, pk=inscripcion_id)
    
    try:
        with transaction.atomic():
            inscripcion.estado = 'cancelado'
            inscripcion.observaciones_admin = request.POST.get('motivo', '')
            inscripcion.save()
            
            messages.success(
                request, 
                f'Se ha rechazado la inscripción de {inscripcion.empleado.nombre_completo}'
            )
            
    except Exception as e:
        logger.error(f'Error al rechazar inscripción {inscripcion_id}: {str(e)}')
        messages.error(request, 'Ocurrió un error al rechazar la inscripción')
        
    return redirect('training:capacitacion_detail', pk=inscripcion.capacitacion.id)

@login_required
@require_http_methods(["POST"])
def inscribir_capacitacion(request, pk):
    """Inscribir empleado a capacitación"""
    capacitacion = get_object_or_404(Capacitacion.objects.select_related('tipo', 'proveedor_externo'), pk=pk)
    
    # Verificar si ya existe una inscripción
    if request.user.is_staff:
        empleado_id = request.POST.get('empleado_id')
        if not empleado_id:
            messages.error(request, 'Debe seleccionar un empleado')
            return redirect('training:capacitacion_detail', pk=pk)
        try:
            empleado = Empleado.objects.get(id=empleado_id)
        except Empleado.DoesNotExist:
            messages.error(request, 'Empleado no encontrado')
            return redirect('training:capacitacion_detail', pk=pk)
    else:
        # Verificar que sea capacitación libre para empleados normales
        if not capacitacion.tipo.permite_inscripcion_libre:
            messages.error(request, 'Esta capacitación no permite inscripción libre')
            return redirect('training:catalogo')
        try:
            empleado = Empleado.objects.get(usuario=request.user)
        except Empleado.DoesNotExist:
            messages.error(request, 'No se encontró tu perfil de empleado')
            return redirect('training:catalogo')
    
    # Verificar si ya existe una inscripción
    if InscripcionCapacitacion.objects.filter(empleado=empleado, capacitacion=capacitacion).exists():
        messages.warning(request, 'Ya estás inscrito en esta capacitación')
        return redirect('training:catalogo' if not request.user.is_staff else 'training:capacitacion_detail', pk=pk)
    
    try:
        with transaction.atomic():
            # Determinar el estado inicial según el tipo de capacitación
            estado_inicial = 'pendiente_validacion' if capacitacion.es_externa() else 'no_iniciado'
            
            # Crear inscripción
            inscripcion = InscripcionCapacitacion.objects.create(
                empleado=empleado,
                capacitacion=capacitacion,
                estado=estado_inicial,
                obligatoria=False,
                aprobada_supervisor=True,  # Las libres se aprueban automáticamente
                inscrito_por=request.user
            )
            
            # Si es interna, crear registros de progreso
            if not capacitacion.es_externa():
                for modulo in capacitacion.modulocapacitacion_set.filter(activo=True):
                    for leccion in modulo.leccion_set.filter(activa=True):
                        for contenido in leccion.contenidoleccion_set.all():
                            ProgresoCapacitacion.objects.create(
                                inscripcion=inscripcion,
                                contenido=contenido
                            )
            
            # Preparar mensaje y redirección según el tipo de capacitación
            if capacitacion.es_externa():
                if request.user.is_staff:
                    messages.success(
                        request,
                        f'Se ha registrado la inscripción de {empleado.nombre_completo}. '
                        f'El estado quedará pendiente de validación hasta que apruebes la solicitud.'
                    )
                    return redirect('training:capacitacion_detail', pk=pk)
                else:
                    messages.success(
                        request,
                        mark_safe(
                            '✅ Tu solicitud de inscripción ha sido enviada y está pendiente de aprobación por el administrador. '
                            'Una vez aprobada, podrás acceder al curso desde "Mis Capacitaciones".'
                        )
                    )
                    return redirect('training:mis_capacitaciones')
            else:
                if request.user.is_staff:
                    messages.success(
                        request, 
                        f'Se ha inscrito exitosamente a {empleado.nombre_completo} en la capacitación.'
                    )
                    return redirect('training:capacitacion_detail', pk=pk)
                else:
                    messages.success(request, 'Te has inscrito exitosamente. ¡Puedes comenzar cuando gustes!')
                    return redirect('training:mis_capacitaciones')
                    
    except Exception as e:
        logger.error(f'Error al inscribir empleado {empleado.id} en capacitación {pk}: {str(e)}')
        messages.error(request, 'Ocurrió un error al procesar la inscripción. Por favor intenta nuevamente.')
        if request.user.is_staff:
            return redirect('training:capacitacion_detail', pk=pk)
        return redirect('training:catalogo')

class PlayerView(LoginRequiredMixin, TemplateView):
    """Vista para reproducir el contenido de una capacitación"""
    template_name = 'training/player.html'

    @method_decorator(xframe_options_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info(f'PlayerView: Iniciando get_context_data para usuario {self.request.user.username}')
        try:
            # Obtener el empleado asociado al usuario
            empleado = get_object_or_404(Empleado, usuario=self.request.user)
            logger.info(f'PlayerView: Empleado encontrado: {empleado.nombre_completo}')
            
            # Obtener la inscripción del empleado
            inscripcion = get_object_or_404(
                InscripcionCapacitacion, 
                pk=self.kwargs['pk'],
                empleado=empleado
            )
            logger.info(f'PlayerView: Inscripción encontrada: {inscripcion.capacitacion.nombre}')
        except:
            logger.error(f'Error al obtener empleado o inscripción para el usuario {self.request.user.username}')
            context['object'] = None
            return context
        
        context['object'] = inscripcion
        # Asegurar que el contexto tenga los módulos filtrados y ordenados para el sidebar
        # Estructura limpia de módulos, lecciones activas y contenidos únicos y ordenados
        modulos_limpios = []
        modulos_queryset = inscripcion.capacitacion.modulocapacitacion_set.filter(activo=True).order_by('orden')
        for modulo in modulos_queryset:
            lecciones_limpias = []
            lecciones_queryset = modulo.leccion_set.filter(activa=True).order_by('orden')
            for leccion in lecciones_queryset:
                contenidos_queryset = leccion.contenidoleccion_set.all().order_by('orden')
                contenidos_unicos = []
                vistos = set()
                for c in contenidos_queryset:
                    clave = (c.nombre, c.orden)
                    if clave not in vistos:
                        contenidos_unicos.append(c)
                        vistos.add(clave)
                # Determinar si la lección está bloqueada para esta inscripción
                bloqueada = leccion.esta_bloqueada_por_prerequisito(inscripcion)
                lecciones_limpias.append({
                    'obj': leccion,
                    'contenidos': contenidos_unicos,
                    'bloqueada': bloqueada
                })
            modulos_limpios.append({
                'obj': modulo,
                'lecciones': lecciones_limpias
            })
        context['modulos_limpios'] = modulos_limpios
        
        try:
            # Obtener el contenido actual o el primero disponible
            contenido_id = self.request.GET.get('contenido')
            if contenido_id:
                contenido_actual = get_object_or_404(
                    ContenidoLeccion.objects.select_related(
                        'leccion', 
                        'leccion__modulo',
                        'tipo_contenido'
                    ),
                    pk=contenido_id,
                    leccion__modulo__capacitacion=inscripcion.capacitacion
                )
                logger.info(f'Tipo de contenido: {contenido_actual.tipo_contenido.codigo}')
                if contenido_actual.archivo:
                    logger.info(f'URL del archivo: {contenido_actual.archivo.url}')
                else:
                    logger.info('No hay archivo adjunto')
            else:
                # Obtener el primer contenido disponible
                contenido_actual = ContenidoLeccion.objects.filter(
                    leccion__modulo__capacitacion=inscripcion.capacitacion,
                    leccion__modulo__activo=True
                ).select_related(
                    'leccion',
                    'leccion__modulo',
                    'tipo_contenido'
                ).first()
                
            # Loggear información del contenido
            if contenido_actual:
                logger.info(f'Contenido encontrado: {contenido_actual.nombre}')
                logger.info(f'Tipo de contenido: {contenido_actual.tipo_contenido.codigo}')
                if contenido_actual.archivo:
                    logger.info(f'Archivo: {contenido_actual.archivo.name}')
                    logger.info(f'URL del archivo: {contenido_actual.archivo.url}')
                else:
                    logger.info('No hay archivo asociado al contenido')

            context['contenido_actual'] = contenido_actual
        except:
            logger.error(f'Error al obtener contenido para la inscripción {inscripcion.pk}')
            context['contenido_actual'] = None

        if context.get('contenido_actual'):
            # Obtener estado de evaluaciones y módulos
            def get_evaluacion_aprobada(modulo):
                logger.info(f'Verificando evaluación para módulo {modulo.nombre}')
                if hasattr(modulo, 'evaluacion'):
                    logger.info(f'Módulo {modulo.nombre} tiene evaluación')
                    aprobada = modulo.evaluacion.esta_aprobada(self.request.user)
                    logger.info(f'Evaluación del módulo {modulo.nombre} {"aprobada" if aprobada else "no aprobada"}')
                    return aprobada
                logger.info(f'Módulo {modulo.nombre} no tiene evaluación')
                return False

            # Obtener contenidos anterior y siguiente del mismo módulo
            modulo_actual = contenido_actual.leccion.modulo
            contenidos_modulo = list(ContenidoLeccion.objects.filter(
                leccion__modulo=modulo_actual,
                leccion__activa=True
            ).select_related('leccion').order_by('leccion__orden', 'orden'))
            
            # Preparar estados de evaluaciones para los módulos
            logger.info('Iniciando procesamiento de estados de evaluaciones para módulos')
            modulos_evaluacion = {}
            for modulo in inscripcion.capacitacion.modulocapacitacion_set.all():
                logger.info(f'Procesando módulo: {modulo.nombre} (ID: {modulo.id})')
                tiene_evaluacion = hasattr(modulo, 'evaluacion')
                evaluacion_aprobada = get_evaluacion_aprobada(modulo)
                modulos_evaluacion[modulo.id] = {
                    'tiene_evaluacion': tiene_evaluacion,
                    'evaluacion_aprobada': evaluacion_aprobada
                }
                logger.info(f'Estado del módulo {modulo.nombre}: tiene_evaluacion={tiene_evaluacion}, evaluacion_aprobada={evaluacion_aprobada}')
            
            idx = contenidos_modulo.index(contenido_actual)
            contenido_anterior = contenidos_modulo[idx - 1] if idx > 0 else None
            contenido_siguiente = contenidos_modulo[idx + 1] if idx < len(contenidos_modulo) - 1 else None
            
            # Si no hay siguiente contenido en el módulo actual, buscar en el siguiente módulo
            if not contenido_siguiente:
                modulos = list(inscripcion.capacitacion.modulocapacitacion_set.filter(
                    activo=True
                ).order_by('orden'))
                idx_modulo = modulos.index(modulo_actual)
                if idx_modulo < len(modulos) - 1:
                    siguiente_modulo = modulos[idx_modulo + 1]
                    contenido_siguiente = ContenidoLeccion.objects.filter(
                        leccion__modulo=siguiente_modulo,
                        leccion__activa=True
                    ).select_related('leccion').order_by('leccion__orden', 'orden').first()
        
            # Obtener contenidos completados y sus evaluaciones
            contenidos_completados = ProgresoCapacitacion.objects.filter(
                inscripcion=inscripcion,
                completado=True
            ).values_list('contenido', flat=True)
            
            # Verificar estado de evaluaciones
            leccion_actual = contenido_actual.leccion
            evaluacion_pendiente = False
            if hasattr(leccion_actual, 'evaluacion'):
                # Verificar si ya aprobó la evaluación
                intentos_aprobados = IntentoQuiz.objects.filter(
                    quiz=leccion_actual.evaluacion,
                    usuario=self.request.user,
                    aprobado=True
                ).exists()
                evaluacion_pendiente = not intentos_aprobados
            
            # Obtener o crear el progreso del contenido actual
            progreso_actual, _ = ProgresoCapacitacion.objects.get_or_create(
                inscripcion=inscripcion,
                contenido=contenido_actual,
                defaults={
                    'completado': False,
                    'tiempo_dedicado_segundos': 0,
                    'porcentaje_visto': 0
                }
            )
            
            # Verificar si puede ver este contenido 
            puede_ver = True
            if contenido_anterior and contenido_anterior.id not in contenidos_completados:
                puede_ver = False
            elif leccion_actual.leccion_prerequisito:
                # Verificar si completó la lección prerequisito usando el nuevo método
                puede_ver = leccion_actual.leccion_prerequisito.esta_completada(inscripcion)
            
            progreso_actual.puede_ver = puede_ver
            
            context.update({
                'object': inscripcion,
                'contenido_actual': contenido_actual,
                'leccion_actual': contenido_actual.leccion,
                'contenido_anterior': contenido_anterior,
                'contenido_siguiente': contenido_siguiente,
                'contenidos_completados': contenidos_completados,
                'progreso_actual': progreso_actual,
                'evaluacion_pendiente': evaluacion_pendiente,
                'modulos_evaluacion': modulos_evaluacion
            })
        else:
            context.update({
                'object': inscripcion,
                'contenido_actual': None,
                'mensaje_error': 'No hay contenido disponible para esta capacitación'
            })
        
        return context

@login_required
@require_http_methods(["POST"])
def completar_contenido(request, pk):
    """Marcar un contenido como completado"""
    try:
        logger.info(f'Iniciando proceso de completar contenido {pk}')
        
        # Verificar el contenido y sus relaciones
        contenido = get_object_or_404(
            ContenidoLeccion.objects.select_related('leccion__modulo__capacitacion'),
            pk=pk
        )
        logger.info(f'Contenido encontrado: {contenido.nombre}, Lección: {contenido.leccion.nombre}, Módulo: {contenido.leccion.modulo.nombre}')
        inscripcion = get_object_or_404(
            InscripcionCapacitacion,
            capacitacion=contenido.leccion.modulo.capacitacion,
            empleado=request.user.empleado
        )
        
        # Actualizar o crear el progreso
        data = json.loads(request.body)
        tiempo_dedicado = data.get('tiempo_dedicado', 0)
        porcentaje_visto = data.get('porcentaje_visto', 0)
        completado = data.get('completado', False)
        
        # Verificar si la lección y el módulo están activos
        leccion = contenido.leccion
        modulo = leccion.modulo
        
        if not leccion.activa:
            return JsonResponse({
                'success': False,
                'message': 'La lección no está disponible actualmente'
            }, status=400)
            
        if not modulo.activo:
            return JsonResponse({
                'success': False,
                'message': 'El módulo no está disponible actualmente'
            }, status=400)
        
        progreso, _ = ProgresoCapacitacion.objects.get_or_create(
            inscripcion=inscripcion,
            contenido=contenido,
            defaults={
                'completado': False,
                'tiempo_dedicado_segundos': 0,
                'porcentaje_visto': 0
            }
        )
        
        # Actualizar el progreso
        logger.info(f'Actualizando progreso - Tiempo: {tiempo_dedicado}s, Porcentaje: {porcentaje_visto}%, Completado: {completado}')
        
        if tiempo_dedicado:
            progreso.tiempo_dedicado_segundos = tiempo_dedicado
        if porcentaje_visto:
            progreso.porcentaje_visto = porcentaje_visto
        if completado:
            progreso.completado = True
            progreso.fecha_completado = timezone.now()
            progreso.porcentaje_visto = 100
            logger.info(f'Marcando contenido como completado para inscripción {inscripcion.id}')
        progreso.save()
        
        logger.info(f'Progreso guardado correctamente: completado={progreso.completado}, tiempo={progreso.tiempo_dedicado_segundos}s')
        
        # Verificar si se completó todo el módulo
        modulo_actual = contenido.leccion.modulo
        leccion_actual = contenido.leccion
        
        # Verificar si la lección está completa usando el nuevo método
        leccion_completada = leccion_actual.esta_completada(inscripcion)
        
        # Obtener el progreso de la lección
        total_contenidos_leccion = ContenidoLeccion.objects.filter(
            leccion=leccion_actual
        ).count()
        
        contenidos_completados_leccion = ProgresoCapacitacion.objects.filter(
            inscripcion=inscripcion,
            contenido__leccion=leccion_actual,
            completado=True
        ).count()
        
        # La evaluación está considerada en el método esta_completada
        necesita_evaluacion = hasattr(leccion_actual, 'evaluacion')
        evaluacion_aprobada = False
        if necesita_evaluacion:
            evaluacion_aprobada = IntentoQuiz.objects.filter(
                quiz=leccion_actual.evaluacion,
                usuario=request.user,
                aprobado=True
            ).exists()
        

        # Contar contenidos y completados en el módulo (incluye caso de solo una lección)
        total_contenidos = ContenidoLeccion.objects.filter(
            leccion__modulo=modulo_actual,
            leccion__activa=True
        ).count()
        contenidos_completados = ProgresoCapacitacion.objects.filter(
            inscripcion=inscripcion,
            contenido__leccion__modulo=modulo_actual,
            completado=True
        ).count()


        # Refuerzo: Verificar y actualizar estado de inscripción y progreso
        if inscripcion.estado == 'no_iniciado':
            inscripcion.estado = 'en_progreso'
            inscripcion.fecha_inicio = timezone.now()

        # Verificar si el módulo y la lección están activos antes de marcar como completado
        if not contenido.leccion.activa:
            return JsonResponse({
                'success': False,
                'message': 'La lección no está activa actualmente'
            }, status=400)

        if not contenido.leccion.modulo.activo:
            return JsonResponse({
                'success': False,
                'message': 'El módulo no está activo actualmente'
            }, status=400)

        # Marcar progreso como completado si no lo está
        if not progreso.completado:
            progreso.completado = True
            progreso.save()

        # Calcular porcentaje total completado
        total_contenidos_capacitacion = ContenidoLeccion.objects.filter(
            leccion__modulo__capacitacion=inscripcion.capacitacion,
            leccion__modulo__activo=True,
            leccion__activa=True
        ).count()
        contenidos_completados_capacitacion = ProgresoCapacitacion.objects.filter(
            inscripcion=inscripcion,
            completado=True
        ).count()

        inscripcion.porcentaje_completado = (contenidos_completados_capacitacion * 100) // total_contenidos_capacitacion

        # Si es la última lección (o única) y todos los contenidos están completos, pasar a 'aprobado'
        if contenidos_completados_capacitacion == total_contenidos_capacitacion and total_contenidos_capacitacion > 0:
            inscripcion.estado = 'aprobado'
        inscripcion.save()

        # Si es la última lección (o única) y todos los contenidos están completos, habilitar evaluación
        puede_valorar_modulo = (contenidos_completados == total_contenidos and total_contenidos > 0)

        # Determinar la URL del siguiente contenido (si existe)
        siguiente_contenido = None
        # Buscar el siguiente contenido de la lección actual en el módulo
        contenidos_modulo = list(ContenidoLeccion.objects.filter(
            leccion__modulo=modulo_actual,
            leccion__activa=True
        ).select_related('leccion').order_by('leccion__orden', 'orden'))
        try:
            idx = contenidos_modulo.index(contenido)
            if idx < len(contenidos_modulo) - 1:
                siguiente_contenido = contenidos_modulo[idx + 1]
        except ValueError:
            siguiente_contenido = None

        siguiente_contenido_url = None
        if siguiente_contenido and getattr(siguiente_contenido, 'pk', None):
            from django.urls import reverse
            siguiente_contenido_url = reverse('training:player', kwargs={'pk': str(inscripcion.pk)}) + f'?contenido={siguiente_contenido.pk}'
        # Si no hay siguiente contenido, asegurar que sea None
        if not siguiente_contenido_url:
            siguiente_contenido_url = None

        # Preparar respuesta
        response_data = {
            'success': True,
            'completado': progreso.completado,
            'progreso_leccion': (contenidos_completados_leccion * 100) // total_contenidos_leccion,
            'progreso_modulo': (contenidos_completados * 100) // total_contenidos if total_contenidos > 0 else 100,
            'progreso_total': inscripcion.porcentaje_completado,
            'leccion_completada': leccion_completada,
            'evaluacion_pendiente': necesita_evaluacion and not evaluacion_aprobada,
            'puede_continuar': leccion_completada,
            'puede_valorar_modulo': puede_valorar_modulo,
            'siguiente_contenido': siguiente_contenido_url
        }

        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f'Error al completar contenido {pk}: {str(e)}')
        return JsonResponse({
            'success': False, 
            'error': str(e),
            'message': 'Ocurrió un error al actualizar el progreso'
        }, status=400)

class MisCertificadosView(TemplateView):
    template_name = 'training/mis_certificados.html'