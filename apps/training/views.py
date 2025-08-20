# apps/training/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.utils.safestring import mark_safe
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
import logging

from .models import (Capacitacion, InscripcionCapacitacion, TipoCapacitacion, 
                     CapacitacionCargo, ModuloCapacitacion, ProgresoCapacitacion,
                     Leccion, ContenidoLeccion)
from .forms import CapacitacionForm #InscripcionCapacitacionForm
from apps.employees.models import Empleado

logger = logging.getLogger(__name__)

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
                
        return redirect('training:catalogo')
    except Exception as e:
        logger.error(f'Error general en el proceso de inscripción: {str(e)}')
        messages.error(request, 'Ocurrió un error inesperado al procesar la inscripción.')
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
                i.capacitacion.duracion_estimada_horas 
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
                estado__codigo='activo'  # Filtrar por el código del estado
            ).exclude(
                id__in=empleados_inscritos if empleados_inscritos else []
            ).select_related('estado').order_by('apellidos', 'nombres')
            
            # Estadísticas para admin
            context['total_inscritos'] = inscripciones.count()
            context['inscritos_pendientes'] = inscripciones.filter(estado='pendiente_validacion').count()
            context['inscritos_activos'] = inscripciones.exclude(
                estado__in=['pendiente_validacion', 'cancelado']
            ).count()
            
            # Lista de inscripciones pendientes para cursos externos
            if capacitacion.es_externa():
                context['inscripciones_pendientes'] = inscripciones.filter(
                    estado='pendiente_validacion'
                ).select_related('empleado')
            context['total_inscritos'] = inscripciones.count()
            context['inscritos_pendientes'] = inscripciones.filter(estado='pendiente_validacion').count()
            context['inscritos_activos'] = inscripciones.exclude(estado__in=['pendiente_validacion', 'cancelado']).count()
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
def validar_inscripcion(request, inscripcion_id):
    """Validar inscripción en capacitación externa"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para realizar esta acción')
        return redirect('training:catalogo')
        
    inscripcion = get_object_or_404(InscripcionCapacitacion, pk=inscripcion_id)
    
    try:
        with transaction.atomic():
            # Guardar el certificado si se proporcionó
            if request.FILES.get('certificado'):
                inscripcion.certificado_externo = request.FILES['certificado']
            
            # Actualizar estado y datos
            inscripcion.estado = 'no_iniciado'
            inscripcion.validado_por_admin = True
            inscripcion.aprobado_por = request.user
            inscripcion.observaciones_admin = request.POST.get('observaciones', '')
            inscripcion.save()
            
            messages.success(
                request, 
                f'Se ha validado la inscripción de {inscripcion.empleado.nombre_completo}'
            )
            
    except Exception as e:
        logger.error(f'Error al validar inscripción {inscripcion_id}: {str(e)}')
        messages.error(request, 'Ocurrió un error al validar la inscripción')
        
    return redirect('training:capacitacion_detail', pk=inscripcion.capacitacion.id)

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
                    for contenido in modulo.contenidoleccion_set.all():
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
                        f'El estado quedará pendiente hasta que presente el certificado del proveedor.'
                    )
                    return redirect('training:capacitacion_detail', pk=pk)
                else:
                    messages.success(
                        request,
                        mark_safe(
                            'Tu inscripción ha sido registrada como pendiente. '
                            'Por favor realiza la inscripción en el sitio del proveedor '
                            'y presenta el certificado para validar tu participación.'
                        )
                    )
                    if capacitacion.url_inscripcion_externa:
                        return redirect(capacitacion.url_inscripcion_externa)
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
        messages.success(request, 'Te has inscrito exitosamente. ¡Puedes comenzar cuando gustes!')
    
    return redirect('training:capacitacion_detail', pk=pk)

class PlayerView(TemplateView):
    template_name = 'training/player.html'

class MisCertificadosView(TemplateView):
    template_name = 'training/mis_certificados.html'