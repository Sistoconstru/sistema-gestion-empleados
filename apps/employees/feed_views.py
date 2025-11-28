# =============================================================================
# apps/employees/feed_views.py - VISTAS PARA FEED/PUBLICACIONES
# =============================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta
import json
import logging

from .models import Publicacion, Comentario, Empleado
from .forms import PublicacionForm, AnuncioImportanteForm, ComentarioForm
from .views import EmpleadoRequiredMixin

logger = logging.getLogger(__name__)


# ===================== VISTAS DEL FEED =====================

class FeedListView(EmpleadoRequiredMixin, LoginRequiredMixin, ListView):
    """Vista principal del feed de publicaciones y anuncios"""
    model = Publicacion
    template_name = 'employees/feed/feed_list.html'
    context_object_name = 'publicaciones'
    paginate_by = 10

    def get_queryset(self):
        """Obtener publicaciones activas ordenadas por importancia"""
        ahora = timezone.now()

        # Obtener publicaciones activas
        queryset = Publicacion.objects.filter(
            Q(es_anuncio=False) |  # Publicaciones normales
            Q(es_anuncio=True, es_importante=False) |  # Anuncios normales
            Q(es_anuncio=True, es_importante=True, fecha_fin__gt=ahora)  # Anuncios importantes vigentes
        ).select_related('autor').prefetch_related('comentarios').annotate(
            num_comentarios=Count('comentarios')
        ).order_by(
            # Anuncios importantes primero
            '-es_importante',
            # Luego por fecha
            '-fecha_creacion'
        )

        # Filtrar por búsqueda si existe
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) |
                Q(contenido__icontains=search) |
                Q(autor__nombre_completo__icontains=search)
            )

        # Filtrar por tipo
        tipo = self.request.GET.get('tipo', '').strip()
        if tipo == 'anuncios':
            queryset = queryset.filter(es_anuncio=True)
        elif tipo == 'importantes':
            queryset = queryset.filter(es_importante=True, fecha_fin__gt=ahora)
        elif tipo == 'publicaciones':
            queryset = queryset.filter(es_anuncio=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['tipo'] = self.request.GET.get('tipo', '')
        context['tipos_filtro'] = [
            ('', 'Todas'),
            ('publicaciones', 'Publicaciones'),
            ('anuncios', 'Anuncios'),
            ('importantes', 'Importantes'),
        ]
        return context


class CrearPublicacionView(EmpleadoRequiredMixin, LoginRequiredMixin, CreateView):
    """Vista para crear una nueva publicación"""
    model = Publicacion
    form_class = PublicacionForm
    template_name = 'employees/feed/publicacion_form.html'
    success_url = reverse_lazy('employees:feed_list')

    def form_valid(self, form):
        """Establecer el autor automáticamente"""
        form.instance.autor = self.request.user.empleado
        form.instance.es_anuncio = False
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Nueva Publicación'
        context['boton_envio'] = 'Publicar'
        return context


class EditarPublicacionView(EmpleadoRequiredMixin, LoginRequiredMixin, UpdateView):
    """Vista para editar una publicación"""
    model = Publicacion
    form_class = PublicacionForm
    template_name = 'employees/feed/publicacion_form.html'
    success_url = reverse_lazy('employees:feed_list')

    def get_queryset(self):
        """Solo el autor o admin puede editar"""
        return Publicacion.objects.filter(
            Q(autor=self.request.user.empleado) | Q(autor__usuario__is_staff=True)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Editar Publicación'
        context['boton_envio'] = 'Guardar Cambios'
        return context


class EliminarPublicacionView(EmpleadoRequiredMixin, LoginRequiredMixin, DeleteView):
    """Vista para eliminar una publicación"""
    model = Publicacion
    template_name = 'employees/feed/publicacion_confirm_delete.html'
    success_url = reverse_lazy('employees:feed_list')

    def get_queryset(self):
        """Solo el autor o admin puede eliminar"""
        return Publicacion.objects.filter(
            Q(autor=self.request.user.empleado) | Q(autor__usuario__is_staff=True)
        )


class CrearAnuncioImportanteView(LoginRequiredMixin, CreateView):
    """Vista para crear anuncios importantes (solo admins)"""
    model = Publicacion
    form_class = AnuncioImportanteForm
    template_name = 'employees/feed/anuncio_form.html'
    success_url = reverse_lazy('employees:feed_list')

    def dispatch(self, request, *args, **kwargs):
        """Solo admins pueden acceder"""
        if not request.user.is_staff:
            return HttpResponseForbidden('No tienes permiso para crear anuncios importantes')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Establecer datos del anuncio"""
        # Crear usuario temporal si es necesario para poder asignar autor
        empleado = Empleado.objects.filter(usuario=self.request.user).first()
        if not empleado:
            # Si el admin no tiene empleado, usar el primero encontrado o crear uno
            empleado = Empleado.objects.first()

        form.instance.autor = empleado
        form.instance.es_anuncio = True
        form.instance.es_importante = True
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Nuevo Anuncio Importante'
        context['boton_envio'] = 'Publicar Anuncio'
        return context


# ===================== VISTAS DE COMENTARIOS =====================

@login_required
def agregar_comentario(request, publicacion_id):
    """Vista para agregar comentario a una publicación (AJAX)"""
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    empleado = get_object_or_404(Empleado, usuario=request.user)

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.publicacion = publicacion
            comentario.autor = empleado
            comentario.save()

            return JsonResponse({
                'success': True,
                'comentario': {
                    'id': str(comentario.id),
                    'autor': comentario.autor.nombre_completo,
                    'contenido': comentario.contenido,
                    'fecha_creacion': comentario.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errores': form.errors
            })

    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@require_POST
def eliminar_comentario(request, comentario_id):
    """Vista para eliminar un comentario (AJAX)"""
    comentario = get_object_or_404(Comentario, id=comentario_id)
    empleado = get_object_or_404(Empleado, usuario=request.user)

    # Solo el autor o admin puede eliminar
    if comentario.autor != empleado and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'No tienes permiso para eliminar este comentario'})

    comentario.delete()
    return JsonResponse({'success': True})


# ===================== VISTAS DE UTILIDAD =====================

@login_required
def editor_estilos(request):
    """Vista AJAX para obtener el editor de estilos"""
    if request.method == 'GET':
        # Retornar HTML del editor de estilos
        html = '''
        <div class="editor-estilos">
            <div class="form-group">
                <label for="font-size">Tamaño de letra</label>
                <select id="font-size" class="form-control" onchange="actualizarEstilo('font_size', this.value)">
                    <option value="">Por defecto</option>
                    <option value="12px">12px (Pequeño)</option>
                    <option value="14px">14px (Normal)</option>
                    <option value="16px">16px (Grande)</option>
                    <option value="18px">18px (Muy grande)</option>
                    <option value="20px">20px (Extra grande)</option>
                </select>
            </div>
            <div class="form-group">
                <label for="font-family">Tipografía</label>
                <select id="font-family" class="form-control" onchange="actualizarEstilo('font_family', this.value)">
                    <option value="">Por defecto</option>
                    <option value="Arial">Arial</option>
                    <option value="'Times New Roman'">Times New Roman</option>
                    <option value="'Courier New'">Courier New</option>
                    <option value="Georgia">Georgia</option>
                    <option value="Verdana">Verdana</option>
                    <option value="'Comic Sans MS'">Comic Sans</option>
                </select>
            </div>
            <div class="form-group">
                <label for="text-color">Color del texto</label>
                <input type="color" id="text-color" class="form-control" style="max-width: 100px;"
                       onchange="actualizarEstilo('text_color', this.value)">
            </div>
            <div class="form-group">
                <label for="background-opacity">Opacidad del fondo (imagen)</label>
                <input type="range" id="background-opacity" class="form-control-range" min="0" max="100" value="50"
                       onchange="actualizarEstilo('background_opacity', this.value)">
                <small class="form-text text-muted"><span id="opacity-value">50</span>%</small>
            </div>
        </div>
        '''
        return JsonResponse({'html': html})

    return JsonResponse({'error': 'Método no permitido'})
