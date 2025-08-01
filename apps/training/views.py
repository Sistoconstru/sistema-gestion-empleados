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

from .models import (Capacitacion, InscripcionCapacitacion, TipoCapacitacion, 
                     CapacitacionCargo, ModuloCapacitacion, ProgresoCapacitacion)
from .forms import CapacitacionForm #InscripcionCapacitacionForm
from apps.employees.models import Empleado

class CapacitacionListView(LoginRequiredMixin, ListView):
    """Vista para administradores - gestión de capacitaciones"""
    model = Capacitacion
    template_name = 'training/capacitacion_list.html'
    context_object_name = 'capacitaciones'
    paginate_by = 20
    
    def get_queryset(self):
        # Lista todas las capacitaciones activas, ordenadas por fecha de creación
        return Capacitacion.objects.select_related('tipo').filter(activa=True).order_by('-fecha_creacion')

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
        
        return context

class CatalogoCapacitacionesView(LoginRequiredMixin, ListView):
    """Catálogo de capacitaciones disponibles para inscripción"""
    model = Capacitacion
    template_name = 'training/catalogo.html'
    context_object_name = 'capacitaciones'
    paginate_by = 15
    
    def get_queryset(self):
        # Solo capacitaciones libres activas
        queryset = Capacitacion.objects.filter(
            activa=True,
            tipo__codigo__in=['INTERNA_LIBRE', 'EXTERNA_LIBRE']
        ).select_related('tipo')
        
        # Aplicar filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | 
                Q(descripcion__icontains=search)
            )
        
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo__codigo=tipo)
        
        proveedor = self.request.GET.get('proveedor')
        if proveedor == 'interno':
            queryset = queryset.filter(proveedor_externo='')
        elif proveedor and proveedor != 'interno':
            queryset = queryset.filter(proveedor_externo__icontains=proveedor)
        
        return queryset.order_by('-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Marcar capacitaciones ya inscritas del empleado
        try:
            empleado = Empleado.objects.get(usuario=self.request.user)
            inscripciones_ids = InscripcionCapacitacion.objects.filter(
                empleado=empleado
            ).values_list('capacitacion_id', flat=True)
            context['inscripciones_ids'] = list(inscripciones_ids)
        except Empleado.DoesNotExist:
            context['inscripciones_ids'] = []
        
        return context

class CapacitacionDetailView(LoginRequiredMixin, DetailView):
    """Detalle de una capacitación"""
    model = Capacitacion
    template_name = 'training/capacitacion_detail.html'
    context_object_name = 'capacitacion'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        capacitacion = self.get_object()
        
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
            ).order_by('orden')
        
        return context

@login_required
def inscribir_capacitacion(request, pk):
    """Inscribir empleado a capacitación libre"""
    capacitacion = get_object_or_404(Capacitacion, pk=pk)
    
    # Verificar que sea capacitación libre
    if capacitacion.es_obligatoria():
        messages.error(request, 'No puedes inscribirte a capacitaciones obligatorias')
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