# apps/training/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
import logging

from .models import (Capacitacion, InscripcionCapacitacion, TipoCapacitacion, 
                     CapacitacionCargo, ModuloCapacitacion, ProgresoCapacitacion)
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
                queryset = queryset.filter(es_externa=False)
            elif tipo == 'externo':
                queryset = queryset.filter(es_externa=True)
                
        if nivel:
            queryset = queryset.filter(nivel_dificultad=nivel)
            
        if duracion:
            queryset = queryset.filter(duracion=duracion)
            
        return queryset.select_related('tipo').order_by('nombre')

@login_required
def inscribir_capacitacion(request, capacitacion_id):
    """Vista para procesar la inscripción a una capacitación"""
    capacitacion = get_object_or_404(Capacitacion, id=capacitacion_id, activa=True)
    empleado = get_object_or_404(Empleado, usuario=request.user)
    
    # Verificar si ya está inscrito
    if InscripcionCapacitacion.objects.filter(empleado=empleado, capacitacion=capacitacion).exists():
        messages.warning(request, 'Ya estás inscrito en esta capacitación.')
        return redirect('training:catalogo')
        
    if request.method == 'POST':
        try:
            # Crear la inscripción
            inscripcion = InscripcionCapacitacion.objects.create(
                empleado=empleado,
                capacitacion=capacitacion,
                fecha_inscripcion=timezone.now()
            )
            
            # Crear registros de progreso para cada módulo
            for modulo in capacitacion.modulos.all():
                ProgresoCapacitacion.objects.create(
                    inscripcion=inscripcion,
                    modulo=modulo
                )
                
            messages.success(request, f'Te has inscrito exitosamente en la capacitación: {capacitacion.nombre}')
            
            # Si es externa, redirigir a la URL externa
            if capacitacion.es_externa and capacitacion.url_externa:
                return redirect(capacitacion.url_externa)
                
        except Exception as e:
            logger.error(f'Error al inscribir empleado {empleado.id} en capacitación {capacitacion_id}: {str(e)}')
            messages.error(request, 'Ocurrió un error al procesar tu inscripción. Por favor intenta nuevamente.')
            
    return redirect('training:catalogo')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas
        context['total_capacitaciones'] = Capacitacion.objects.filter(activa=True).count()
        context['total_obligatorias'] = CapacitacionCargo.objects.filter(
            capacitacion__activa=True,
            obligatoria=True
        ).values('capacitacion').distinct().count()
        
        # Capacitaciones en progreso - usando values y distinct
        context['en_progreso'] = InscripcionCapacitacion.objects.filter(
            estado='en_progreso'
        ).values('empleado').distinct().count()
        
        # Completadas este mes
        inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0)
        context['completadas_mes'] = InscripcionCapacitacion.objects.filter(
            estado__in=['completado', 'aprobado'],
            fecha_finalizacion__gte=inicio_mes
        ).count()
        
        # Tipos para filtros
        context['tipos_capacitacion'] = TipoCapacitacion.objects.all()
        
        return context

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
        
        # Obtener la inscripción del empleado si existe
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            try:
                empleado = Empleado.objects.get(usuario=self.request.user)
                context['inscripcion'] = InscripcionCapacitacion.objects.get(
                    empleado=empleado,
                    capacitacion=capacitacion
                )
            except (Empleado.DoesNotExist, InscripcionCapacitacion.DoesNotExist):
                context['inscripcion'] = None
        
        # Estadísticas de inscripciones (solo para admin)
        inscripciones = InscripcionCapacitacion.objects.filter(capacitacion=capacitacion)
        context['total_inscritos'] = inscripciones.count()
        context['en_progreso'] = inscripciones.filter(estado='en_progreso').count()
        context['completados'] = inscripciones.filter(estado__in=['completado', 'aprobado']).count()
        
        # Calcular porcentajes para las barras de progreso
        if context['total_inscritos'] > 0:
            context['porcentaje_progreso'] = (context['en_progreso'] / context['total_inscritos']) * 100
            context['porcentaje_completados'] = (context['completados'] / context['total_inscritos']) * 100
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
def inscribir_capacitacion(request, pk):
    """Inscribir empleado a capacitación libre"""
    capacitacion = get_object_or_404(Capacitacion.objects.select_related('tipo'), pk=pk)
    
    # Verificar que sea capacitación libre
    if not capacitacion.tipo.permite_inscripcion_libre:
        messages.error(request, 'Esta capacitación no permite inscripción libre')
        return redirect('training:catalogo')
    
    try:
        empleado = Empleado.objects.get(usuario=request.user)
    except Empleado.DoesNotExist:
        messages.error(request, 'No se encontró tu perfil de empleado')
        return redirect('training:catalogo')
    
    # Verificar si ya está inscrito
    if InscripcionCapacitacion.objects.filter(empleado=empleado, capacitacion=capacitacion).exists():
        messages.warning(request, 'Ya estás inscrito en esta capacitación')
        return redirect('training:capacitacion_detail', pk=pk)
    
    # Crear inscripción
    inscripcion = InscripcionCapacitacion.objects.create(
        empleado=empleado,
        capacitacion=capacitacion,
        obligatoria=False,
        aprobada_supervisor=True,  # Las libres se aprueban automáticamente
        inscrito_por=request.user
    )
    
    if capacitacion.es_externa():
        messages.success(
            request, 
            f'Te has inscrito exitosamente. '
            f'<a href="{capacitacion.url_inscripcion_externa}" target="_blank" class="alert-link">'
            f'Haz clic aquí para ir al sitio del proveedor</a>.'
        )
    else:
        messages.success(request, 'Te has inscrito exitosamente. ¡Puedes comenzar cuando gustes!')
    
    return redirect('training:capacitacion_detail', pk=pk)

class PlayerView(TemplateView):
    template_name = 'training/player.html'

class MisCertificadosView(TemplateView):
    template_name = 'training/mis_certificados.html'