from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    Encuesta, TipoEncuesta, ParticipacionEncuesta, 
    PreguntaEncuesta, RespuestaEncuesta
)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal del módulo de encuestas"""
    template_name = 'surveys/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Métricas generales
        context['total_encuestas'] = Encuesta.objects.filter(activa=True).count()
        context['encuestas_pendientes'] = self.get_encuestas_pendientes_count()
        context['encuestas_completadas'] = self.get_encuestas_completadas_count()
        context['tipos_encuesta'] = TipoEncuesta.objects.filter(activo=True).count()
        
        # Encuestas disponibles para el usuario
        context['encuestas_disponibles'] = self.get_encuestas_disponibles()
        
        # Encuestas recientes
        context['encuestas_recientes'] = Encuesta.objects.filter(
            activa=True,
            fecha_inicio__lte=timezone.now().date(),
            fecha_fin__gte=timezone.now().date()
        ).order_by('-fecha_creacion')[:5]
        
        # Estadísticas de participación
        context['participacion_stats'] = self.get_participacion_stats()
        
        return context
    
    def get_encuestas_pendientes_count(self):
        """Conteo de encuestas pendientes para el usuario actual"""
        # Encuestas activas donde el usuario no ha participado
        encuestas_activas = Encuesta.objects.filter(
            activa=True,
            fecha_inicio__lte=timezone.now().date(),
            fecha_fin__gte=timezone.now().date()
        )
        
        participaciones_completadas = ParticipacionEncuesta.objects.filter(
            empleado__usuario=self.request.user,
            completada=True
        ).values_list('encuesta_id', flat=True)
        
        return encuestas_activas.exclude(id__in=participaciones_completadas).count()
    
    def get_encuestas_completadas_count(self):
        """Conteo de encuestas completadas por el usuario actual"""
        return ParticipacionEncuesta.objects.filter(
            empleado__usuario=self.request.user,
            completada=True
        ).count()
    
    def get_encuestas_disponibles(self):
        """Encuestas disponibles para el usuario actual"""
        encuestas_activas = Encuesta.objects.filter(
            activa=True,
            fecha_inicio__lte=timezone.now().date(),
            fecha_fin__gte=timezone.now().date()
        )
        
        participaciones_completadas = ParticipacionEncuesta.objects.filter(
            empleado__usuario=self.request.user,
            completada=True
        ).values_list('encuesta_id', flat=True)
        
        return encuestas_activas.exclude(id__in=participaciones_completadas)[:6]
    
    def get_participacion_stats(self):
        """Estadísticas de participación general"""
        total_participaciones = ParticipacionEncuesta.objects.count()
        participaciones_completadas = ParticipacionEncuesta.objects.filter(completada=True).count()
        
        if total_participaciones > 0:
            porcentaje_completado = round((participaciones_completadas / total_participaciones) * 100, 1)
        else:
            porcentaje_completado = 0
            
        return {
            'total_participaciones': total_participaciones,
            'participaciones_completadas': participaciones_completadas,
            'porcentaje_completado': porcentaje_completado
        }


class EncuestaListView(LoginRequiredMixin, ListView):
    """Lista de todas las encuestas disponibles"""
    model = Encuesta
    template_name = 'surveys/encuesta_list.html'
    context_object_name = 'encuestas'
    paginate_by = 10
    
    def get_queryset(self):
        return Encuesta.objects.filter(
            activa=True,
            fecha_inicio__lte=timezone.now().date(),
            fecha_fin__gte=timezone.now().date()
        ).order_by('-fecha_creacion')


class ResponderEncuestaView(LoginRequiredMixin, DetailView):
    """Vista para responder una encuesta específica"""
    model = Encuesta
    template_name = 'surveys/responder_encuesta.html'
    context_object_name = 'encuesta'
    
    def get_object(self):
        encuesta = get_object_or_404(Encuesta, pk=self.kwargs['pk'], activa=True)
        
        # Verificar si ya completó la encuesta
        participacion = ParticipacionEncuesta.objects.filter(
            empleado__usuario=self.request.user,
            encuesta=encuesta
        ).first()
        
        if participacion and participacion.completada:
            messages.warning(self.request, 'Ya has completado esta encuesta.')
            return redirect('surveys:index')
            
        return encuesta
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        encuesta = self.get_object()
        
        # Obtener o crear participación
        participacion, created = ParticipacionEncuesta.objects.get_or_create(
            empleado__usuario=self.request.user,
            encuesta=encuesta,
            defaults={
                'empleado': self.request.user.empleado if hasattr(self.request.user, 'empleado') else None
            }
        )
        
        context['participacion'] = participacion
        context['preguntas'] = PreguntaEncuesta.objects.filter(
            encuesta=encuesta, 
            activa=True
        ).order_by('orden')
        
        return context


class MisEncuestasView(LoginRequiredMixin, ListView):
    """Vista de encuestas del usuario actual"""
    template_name = 'surveys/mis_encuestas.html'
    context_object_name = 'participaciones'
    paginate_by = 10
    
    def get_queryset(self):
        return ParticipacionEncuesta.objects.filter(
            empleado__usuario=self.request.user
        ).order_by('-fecha_inicio')