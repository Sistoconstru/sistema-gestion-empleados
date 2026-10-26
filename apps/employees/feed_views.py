# =============================================================================
# apps/employees/feed_views.py - VISTAS PARA FEED/PUBLICACIONES
# =============================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.db.models import BooleanField, Count, Exists, OuterRef, Q, Value
from django.utils import timezone
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST, require_http_methods
from datetime import timedelta
import json
import logging

from .models import DIAS_VIGENCIA_PUBLICACION, Publicacion, Comentario, Empleado, Reaccion
from .forms import AnuncioImportanteForm, ComentarioForm
from .views import EmpleadoRequiredMixin

logger = logging.getLogger(__name__)


# ===================== VISTAS DEL FEED =====================

class FeedListView(EmpleadoRequiredMixin, LoginRequiredMixin, ListView):
    """Vista principal del feed de publicaciones y anuncios"""
    model = Publicacion
    template_name = 'employees/feed/feed_list.html'
    context_object_name = 'publicaciones'
    paginate_by = 10

    def _limpiar_notificaciones_expiradas(self):
        """Limpia notificaciones de anuncios que ya no existen o están expirados"""
        try:
            from apps.notifications.models import Notificacion
            ahora = timezone.now()

            # Obtener todas las notificaciones de anuncios importantes del usuario actual
            notificaciones_anuncios = Notificacion.objects.filter(
                usuario=self.request.user,
                tipo_notificacion__codigo='anuncio_importante'
            ).select_related('tipo_notificacion')

            notificaciones_a_eliminar = []

            for notif in notificaciones_anuncios:
                # Obtener ID de publicación desde datos_adicionales
                publicacion_id = notif.datos_adicionales.get('publicacion_id') if notif.datos_adicionales else None

                if publicacion_id:
                    # Verificar si el anuncio existe y está vigente
                    try:
                        anuncio = Publicacion.objects.get(id=publicacion_id, es_anuncio=True)
                        # Si el anuncio expiró, marcar para eliminar
                        if anuncio.fecha_fin and anuncio.fecha_fin <= ahora:
                            notificaciones_a_eliminar.append(notif.id)
                    except Publicacion.DoesNotExist:
                        # El anuncio ya no existe, marcar para eliminar
                        notificaciones_a_eliminar.append(notif.id)

            # Eliminar notificaciones en lote
            if notificaciones_a_eliminar:
                count = Notificacion.objects.filter(id__in=notificaciones_a_eliminar).delete()[0]
                logger.info(f"[FEED] Limpiadas {count} notificaciones expiradas para usuario {self.request.user.username}")

        except Exception as e:
            logger.warning(f"[FEED] Error al limpiar notificaciones expiradas: {e}")

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
        ).exclude(
            # Vencidas por vigencia: se ocultan aquí aunque el borrado físico
            # (limpiar_publicaciones_expiradas) no haya corrido todavía.
            fecha_eliminacion_automatica__lte=ahora
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

        try:
            empleado_actual = self.request.user.empleado
        except Exception:
            empleado_actual = None

        queryset = queryset.select_related('autor').prefetch_related('comentarios').annotate(
            # distinct=True en ambos: al unir comentarios y reacciones en la
            # misma consulta, las filas se multiplican y sin distinct los dos
            # contadores saldrían inflados.
            num_comentarios=Count('comentarios', distinct=True),
            num_reacciones=Count('reacciones', distinct=True),
            # Si el empleado actual ya reaccionó, resuelto en la misma consulta
            # para no lanzar una query por publicación al pintar el feed.
            reaccionado=Exists(
                Reaccion.objects.filter(
                    publicacion=OuterRef('pk'),
                    autor=empleado_actual,
                )
            ) if empleado_actual else Value(False, output_field=BooleanField()),
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
        # Limpiar notificaciones expiradas antes de renderizar
        self._limpiar_notificaciones_expiradas()

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


# ===================== PUBLICACIÓN RÁPIDA =====================

@login_required
@require_POST
def crear_publicacion_rapida(request):
    """Publicación rápida desde el propio feed: texto, imagen o ambos.

    Antes solo aceptaba texto y para adjuntar una foto había que irse al editor
    completo, que en realidad es un diseñador de carteles. Ahora el caso común
    —compartir una imagen— se resuelve sin salir del feed.

    Responde JSON con la tarjeta ya renderizada cuando la llamada es AJAX, para
    insertarla arriba sin recargar; si llega sin JavaScript, redirige al feed
    como siempre.
    """
    es_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def _error(mensaje, status=400):
        if es_ajax:
            return JsonResponse({'success': False, 'error': mensaje}, status=status)
        messages.error(request, mensaje)
        return redirect('employees:feed_list')

    try:
        contenido = request.POST.get('contenido', '').strip()
        imagen = request.FILES.get('imagen')

        # Una foto sin pie de texto es una publicación válida; lo que no vale
        # es enviar el formulario vacío.
        if not contenido and not imagen:
            return _error('Escribe algo o adjunta una imagen.')

        if len(contenido) > 1000:
            contenido = contenido[:1000]

        if imagen:
            if not (imagen.content_type or '').startswith('image/'):
                return _error('El archivo debe ser una imagen.')
            if imagen.size > 5 * 1024 * 1024:
                return _error('La imagen no debe superar 5MB.')

        publicacion = Publicacion.objects.create(
            autor=request.user.empleado,
            titulo='',  # Las publicaciones rápidas no llevan título
            contenido=contenido,
            imagen=imagen,
            es_anuncio=False,
            es_importante=False,
            es_rapida=True,
            fecha_eliminacion_automatica=timezone.now() + timedelta(days=DIAS_VIGENCIA_PUBLICACION),
        )

        logger.info(
            f"[QUICK_POST] {request.user.username} creó publicación rápida "
            f"{publicacion.id} (imagen={'sí' if imagen else 'no'})"
        )

        if es_ajax:
            # Se recarga con las anotaciones que espera la tarjeta; recién
            # creada no tiene comentarios ni reacciones.
            publicacion.num_comentarios = 0
            publicacion.num_reacciones = 0
            publicacion.reaccionado = False
            html = render_to_string(
                'employees/feed/_publicacion_card.html',
                {'publicacion': publicacion, 'user': request.user},
                request=request,
            )
            return JsonResponse({'success': True, 'html': html})

        return redirect('employees:feed_list')

    except Exception as e:
        logger.error(f"[QUICK_POST] Error al crear publicación rápida: {e}", exc_info=True)
        return _error('No se pudo publicar. Inténtalo de nuevo.', status=500)


@login_required
@require_POST
def alternar_reaccion(request, publicacion_pk):
    """Pone o quita el "me gusta" del empleado actual en una publicación."""
    publicacion = get_object_or_404(Publicacion, id=publicacion_pk)
    empleado = get_object_or_404(Empleado, usuario=request.user)

    # get_or_create + delete en vez de contar primero: con doble clic rápido,
    # la restricción única de la tabla evita duplicados.
    reaccion, creada = Reaccion.objects.get_or_create(
        publicacion=publicacion, autor=empleado,
    )
    if not creada:
        reaccion.delete()

    return JsonResponse({
        'success': True,
        'reaccionado': creada,
        'total': publicacion.reacciones.count(),
    })


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
        logger.info(f"[PREVIEW] Usuario {request.user.username} solicitó preview")
        logger.info(f"[PREVIEW] FILES: {request.FILES.keys()}")
        logger.info(f"[PREVIEW] POST: {request.POST.keys()}")

        imagen = request.FILES.get('imagen')
        titulo = request.POST.get('titulo', '')
        contenido = request.POST.get('contenido', '')
        estilos_json = request.POST.get('estilos', '{}')

        logger.info(f"[PREVIEW] Imagen recibida: {imagen}")
        logger.info(f"[PREVIEW] Titulo: {titulo[:50] if titulo else 'None'}")
        logger.info(f"[PREVIEW] Contenido: {contenido[:50] if contenido else 'None'}")

        estilos = json.loads(estilos_json)
        logger.info(f"[PREVIEW] Estilos: {estilos}")

        if not imagen:
            logger.error("[PREVIEW] No se proporcionó imagen en request.FILES")
            return JsonResponse({'success': False, 'error': 'No se proporcionó imagen'})

        # Renderizar la imagen
        imagen_renderizada = renderizar_anuncio_v2(
            imagen_file=imagen,
            titulo=titulo,
            contenido=contenido,
            estilos=estilos
        )

        # Convertir imagen a base64 para evitar problemas de CORS
        import base64
        imagen_renderizada.seek(0)
        imagen_bytes = imagen_renderizada.read()
        imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
        data_url = f"data:image/png;base64,{imagen_base64}"

        logger.info(f"[PREVIEW] Imagen renderizada convertida a base64 (tamaño: {len(imagen_base64)} chars)")

        return JsonResponse({
            'success': True,
            'url': data_url,
            'is_base64': True
        })

    except Exception as e:
        logger.error(f"[PREVIEW] Error al generar preview: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
