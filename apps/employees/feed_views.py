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
from django.views.decorators.http import require_POST, require_http_methods
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
        es_admin = self.request.user.is_staff

        # Publicaciones activas (que cumplan fecha_inicio y fecha_fin)
        queryset_activas = Publicacion.objects.filter(
            # Fecha inicio: debe estar NULL o ser <= ahora
            Q(fecha_inicio__isnull=True) | Q(fecha_inicio__lte=ahora)
        ).filter(
            # Fecha fin: debe estar NULL o ser > ahora
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gt=ahora)
        ).exclude(
            # Excluir anuncios importantes que ya no están vigentes
            es_anuncio=True, es_importante=True, fecha_fin__lte=ahora
        )

        # Si es admin, también mostrar publicaciones pendientes
        if es_admin:
            try:
                empleado_actual = self.request.user.empleado
            except:
                empleado_actual = None

            queryset_pendientes = Publicacion.objects.filter(
                # Mostrar si es autor
                Q(autor=empleado_actual) | Q(autor__usuario__is_staff=True)
            ).filter(
                # Fecha inicio en el futuro (aún no publicadas)
                fecha_inicio__gt=ahora
            )
            queryset = queryset_activas | queryset_pendientes
        else:
            queryset = queryset_activas

        queryset = queryset.select_related('autor').prefetch_related('comentarios').annotate(
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
    template_name = 'employees/feed/publicacion_crear_nuevo.html'
    success_url = reverse_lazy('employees:feed_list')

    def form_valid(self, form):
        """Establecer el autor y fecha de eliminación automáticamente"""
        from datetime import timedelta

        form.instance.autor = self.request.user.empleado
        form.instance.es_anuncio = False

        # Si tiene imagen, se elimina en 15 días
        if form.instance.imagen:
            form.instance.fecha_eliminacion_automatica = timezone.now() + timedelta(days=15)
            logger.info(f"[PUB_CREATE] Publicación con imagen. Eliminación en 15 días.")

        return super().form_valid(form)


class EditarPublicacionView(EmpleadoRequiredMixin, LoginRequiredMixin, UpdateView):
    """Vista para editar una publicación"""
    model = Publicacion
    form_class = PublicacionForm
    template_name = 'employees/feed/publicacion_crear_nuevo.html'
    success_url = reverse_lazy('employees:feed_list')

    def get_queryset(self):
        """Solo el autor o admin puede editar"""
        # Si el usuario es admin, puede editar cualquier publicación
        if self.request.user.is_staff:
            return Publicacion.objects.all()

        # Si no es admin, solo puede editar sus propias publicaciones
        try:
            empleado_actual = self.request.user.empleado
            return Publicacion.objects.filter(autor=empleado_actual)
        except:
            # Si no tiene empleado vinculado, no puede editar nada
            return Publicacion.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Editar Publicación'
        context['es_edicion'] = True
        return context


class EliminarPublicacionView(EmpleadoRequiredMixin, LoginRequiredMixin, DeleteView):
    """Vista para eliminar una publicación"""
    model = Publicacion
    template_name = 'employees/feed/publicacion_confirm_delete.html'
    success_url = reverse_lazy('employees:feed_list')

    def get_queryset(self):
        """Solo el autor o admin puede eliminar"""
        # Si el usuario es admin, puede eliminar cualquier publicación
        if self.request.user.is_staff:
            return Publicacion.objects.all()

        # Si no es admin, solo puede eliminar sus propias publicaciones
        try:
            empleado_actual = self.request.user.empleado
            return Publicacion.objects.filter(autor=empleado_actual)
        except:
            # Si no tiene empleado vinculado, no puede eliminar nada
            return Publicacion.objects.none()


class CrearAnuncioImportanteView(LoginRequiredMixin, CreateView):
    """Vista para crear anuncios importantes (solo admins)"""
    model = Publicacion
    form_class = AnuncioImportanteForm
    template_name = 'employees/feed/anuncio_crear_nuevo.html'
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

        # Fecha de eliminación = fecha_fin del anuncio (control manual)
        # Al terminar la fecha_fin, se elimina automáticamente del sistema
        if form.instance.fecha_fin:
            form.instance.fecha_eliminacion_automatica = form.instance.fecha_fin
            logger.info(f"[ANUNCIO_CREATE] Anuncio importante. Eliminación en fecha_fin: {form.instance.fecha_fin}")

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Nuevo Anuncio Importante'
        context['boton_envio'] = 'Publicar Anuncio'
        return context


# ===================== VISTAS DE COMENTARIOS =====================

@login_required
def agregar_comentario(request, publicacion_pk):
    """Vista para agregar comentario a una publicación (AJAX)"""
    publicacion = get_object_or_404(Publicacion, id=publicacion_pk)
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


# ===================== PUBLICACIÓN RÁPIDA =====================

@login_required
@require_POST
def crear_publicacion_rapida(request):
    """Vista para crear una publicación rápida sin estilos avanzados"""
    try:
        from datetime import timedelta

        contenido = request.POST.get('contenido', '').strip()

        if not contenido:
            return redirect('employees:feed_list')

        # Limitar longitud
        if len(contenido) > 1000:
            contenido = contenido[:1000]

        # Calcular fecha de eliminación (6 meses desde ahora)
        fecha_eliminacion = timezone.now() + timedelta(days=180)

        # Crear publicación simple (sin imagen, sin estilos)
        publicacion = Publicacion.objects.create(
            autor=request.user.empleado,
            titulo='',  # Sin título en publicaciones rápidas
            contenido=contenido,
            es_anuncio=False,
            es_importante=False,
            es_rapida=True,  # Marcar como publicación rápida
            fecha_eliminacion_automatica=fecha_eliminacion  # 6 meses
        )

        logger.info(f"[QUICK_POST] Usuario {request.user.username} creó publicación rápida #{publicacion.id} (exp: {fecha_eliminacion})")

        return redirect('employees:feed_list')

    except Exception as e:
        logger.error(f"[QUICK_POST] Error al crear publicación rápida: {e}", exc_info=True)
        return redirect('employees:feed_list')


@login_required
@require_http_methods(["POST"])
def preview_renderizado_anuncio(request):
    """
    Vista AJAX para preview del renderizado de anuncio/publicación.
    Renderiza la imagen temporalmente y devuelve la URL.
    """
    import json
    import tempfile
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from .renderizado_anuncios import renderizar_anuncio_v2
    from django.core.files.storage import default_storage

    try:
        # Obtener datos del request
        imagen = request.FILES.get('imagen')
        titulo = request.POST.get('titulo', '')
        contenido = request.POST.get('contenido', '')
        estilos_json = request.POST.get('estilos', '{}')
        estilos = json.loads(estilos_json)

        logger.info(f"[PREVIEW] Usuario {request.user.username} solicitó preview")
        logger.info(f"[PREVIEW] Estilos: {estilos}")

        if not imagen:
            return JsonResponse({'success': False, 'error': 'No se proporcionó imagen'})

        # Renderizar la imagen
        imagen_renderizada = renderizar_anuncio_v2(
            imagen_file=imagen,
            titulo=titulo,
            contenido=contenido,
            estilos=estilos
        )

        # Guardar temporalmente en S3 con prefijo temporal
        import uuid
        temp_filename = f'temp/preview_{uuid.uuid4().hex[:8]}.png'
        temp_path = default_storage.save(temp_filename, imagen_renderizada)
        temp_url = default_storage.url(temp_path)

        logger.info(f"[PREVIEW] Imagen renderizada guardada temporalmente: {temp_url}")

        return JsonResponse({
            'success': True,
            'url': temp_url,
            'temp_path': temp_path  # Para limpiar después si es necesario
        })

    except Exception as e:
        logger.error(f"[PREVIEW] Error al generar preview: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
