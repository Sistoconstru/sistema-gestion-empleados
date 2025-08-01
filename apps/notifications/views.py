from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import JsonResponse
from django.utils import timezone

from .models import Notificacion


class NotificacionesListView(LoginRequiredMixin, ListView):
    """Vista de lista de notificaciones"""
    model = Notificacion
    template_name = 'notifications/list.html'
    context_object_name = 'notificaciones'
    paginate_by = 20
    
    def get_queryset(self):
        # Filtra las notificaciones del usuario actual, ordenadas por fecha de creación descendente
        return Notificacion.objects.filter(
            usuario=self.request.user
        ).order_by('-fecha_creacion')


@login_required
def marcar_leida(request, notification_id):
    """Marcar notificación como leída"""
    if request.method == 'POST':
        # Busca la notificación por ID y usuario
        notificacion = get_object_or_404(
            Notificacion, 
            id=notification_id, 
            usuario=request.user
        )
        notificacion.leida = True
        notificacion.fecha_leida = timezone.now()
        notificacion.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})


@login_required
def marcar_todas_leidas(request):
    """Marcar todas las notificaciones como leídas"""
    if request.method == 'POST':
        # Actualiza todas las notificaciones no leídas del usuario
        Notificacion.objects.filter(
            usuario=request.user,
            leida=False
        ).update(
            leida=True,
            fecha_leida=timezone.now()
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})


@login_required
def notificaciones_count(request):
    """Obtener contador de notificaciones no leídas"""
    count = Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).count()
    
    return JsonResponse({'count': count})
