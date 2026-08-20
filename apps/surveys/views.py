from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import models
from django.db.models import Count, Q, Avg, Max
from django.utils import timezone
from django.http import JsonResponse
from django.views import View
from datetime import datetime, timedelta

from .models import (
    Encuesta, TipoEncuesta, ParticipacionEncuesta,
    PreguntaEncuesta, RespuestaEncuesta, OpcionEncuesta
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


class ResponderEncuestaView(LoginRequiredMixin, View):
    """Vista para responder una encuesta específica"""
    template_name = 'surveys/responder_encuesta.html'

    def get(self, request, pk):
        """Mostrar formulario de encuesta"""
        encuesta = get_object_or_404(Encuesta, pk=pk, activa=True)

        # Verificar si ya completó la encuesta
        participacion = ParticipacionEncuesta.objects.filter(
            empleado__usuario=request.user,
            encuesta=encuesta
        ).first()

        if participacion and participacion.completada:
            messages.warning(request, 'Ya has completado esta encuesta.')
            return redirect('surveys:index')

        # Obtener o crear participación
        if not participacion:
            participacion = ParticipacionEncuesta.objects.create(
                empleado=request.user.empleado if hasattr(request.user, 'empleado') else None,
                encuesta=encuesta,
                ip_address=self.get_client_ip(request),
                dispositivo=request.META.get('HTTP_USER_AGENT', '')[:200]
            )

        # Obtener preguntas
        preguntas = PreguntaEncuesta.objects.filter(
            encuesta=encuesta,
            activa=True
        ).prefetch_related('opcionencuesta_set').order_by('orden')

        # Obtener respuestas existentes (para modo borrador)
        respuestas_existentes = {}
        if participacion:
            for respuesta in RespuestaEncuesta.objects.filter(participacion=participacion):
                if respuesta.opcion_seleccionada:
                    respuestas_existentes[str(respuesta.pregunta.id)] = respuesta.opcion_seleccionada.id
                elif respuesta.respuesta_texto:
                    respuestas_existentes[str(respuesta.pregunta.id)] = respuesta.respuesta_texto

        context = {
            'encuesta': encuesta,
            'participacion': participacion,
            'preguntas': preguntas,
            'respuestas_existentes': respuestas_existentes
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        """Guardar respuestas de encuesta"""
        encuesta = get_object_or_404(Encuesta, pk=pk, activa=True)

        # Obtener participación existente
        participacion = ParticipacionEncuesta.objects.filter(
            empleado__usuario=request.user,
            encuesta=encuesta
        ).first()

        if not participacion:
            return JsonResponse({'success': False, 'message': 'Participación no encontrada'}, status=400)

        if participacion.completada:
            return JsonResponse({'success': False, 'message': 'Ya completaste esta encuesta'}, status=400)

        # Verificar si es guardar borrador o finalizar
        es_borrador = request.POST.get('guardar_borrador') == 'true'
        finalizar = request.POST.get('finalizar_encuesta') == 'true'

        # Procesar respuestas
        preguntas = PreguntaEncuesta.objects.filter(encuesta=encuesta, activa=True)
        respuestas_guardadas = 0

        # OpcionEncuesta.pk es UUID — validamos que el valor recibido
        # corresponda efectivamente a una opción de la pregunta antes de
        # guardarlo en opcion_seleccionada_id. Si no matchea, cae a texto.
        tipos_con_opciones = [
            'multiple_choice', 'select', 'rating',
            'PREGMULT', 'ESCALA_5', 'SI_NO', 'ESCALA_3', 'checkbox',
        ]

        def _guardar(pregunta, valor):
            if pregunta.tipo_pregunta.codigo in tipos_con_opciones:
                opcion = pregunta.opcionencuesta_set.filter(pk=valor).first()
                if opcion:
                    RespuestaEncuesta.objects.update_or_create(
                        participacion=participacion, pregunta=pregunta,
                        defaults={'opcion_seleccionada': opcion, 'respuesta_texto': ''},
                    )
                    return True
                # No matchea ninguna opción → guardamos el texto crudo por si el
                # frontend mandó un valor libre (ej: "Otro").
                RespuestaEncuesta.objects.update_or_create(
                    participacion=participacion, pregunta=pregunta,
                    defaults={'opcion_seleccionada': None, 'respuesta_texto': str(valor)},
                )
                return True
            # Texto libre / texto corto
            RespuestaEncuesta.objects.update_or_create(
                participacion=participacion, pregunta=pregunta,
                defaults={'respuesta_texto': str(valor)},
            )
            return True

        for pregunta in preguntas:
            campo_nombre = f'pregunta_{pregunta.id}'

            if pregunta.tipo_pregunta.codigo == 'checkbox':
                # Múltiple selección: hoy el modelo tiene unique_together
                # (participacion, pregunta) → solo persiste la ÚLTIMA opción.
                # Se registra la última para no romper; para soportar checkbox
                # real hay que ajustar el modelo (fuera de este fix).
                valores = request.POST.getlist(f'{campo_nombre}[]')
                if valores:
                    _guardar(pregunta, valores[-1])
                    respuestas_guardadas += 1
            else:
                valor = request.POST.get(campo_nombre)
                if valor:
                    _guardar(pregunta, valor)
                    respuestas_guardadas += 1

        # Calcular porcentaje de completado
        total_preguntas = preguntas.count()
        total_respuestas = RespuestaEncuesta.objects.filter(participacion=participacion).count()
        porcentaje = round((total_respuestas / total_preguntas * 100)) if total_preguntas > 0 else 0

        # Actualizar participación
        participacion.porcentaje_completado = porcentaje

        if finalizar:
            participacion.completada = True
            participacion.fecha_completada = timezone.now()

            # Calcular tiempo empleado
            tiempo_delta = participacion.fecha_completada - participacion.fecha_inicio
            participacion.tiempo_empleado_minutos = int(tiempo_delta.total_seconds() / 60)

        participacion.save()

        if es_borrador:
            return JsonResponse({
                'success': True,
                'message': 'Borrador guardado correctamente',
                'porcentaje_completado': porcentaje
            })
        elif finalizar:
            messages.success(request, '¡Gracias por completar la encuesta!')
            return JsonResponse({
                'success': True,
                'message': 'Encuesta completada exitosamente',
                'redirect': '/encuestas/'
            })
        else:
            return JsonResponse({'success': True, 'message': 'Respuestas guardadas'})

    def get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class MisEncuestasView(LoginRequiredMixin, ListView):
    """Vista de encuestas del usuario actual"""
    template_name = 'surveys/mis_encuestas.html'
    context_object_name = 'participaciones'
    paginate_by = 10

    def get_queryset(self):
        return ParticipacionEncuesta.objects.filter(
            empleado__usuario=self.request.user
        ).order_by('-fecha_inicio')


# =============================================================================
# VISTAS DE ADMINISTRACIÓN DE ENCUESTAS (solo staff/superuser)
# =============================================================================

class EncuestaAdminListView(LoginRequiredMixin, ListView):
    """Lista de encuestas para administración"""
    model = Encuesta
    template_name = 'surveys/admin/encuesta_admin_list.html'
    context_object_name = 'encuestas'
    paginate_by = 15

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'No tienes permisos para acceder a esta sección')
            return redirect('surveys:index')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Encuesta.objects.all().select_related('tipo_encuesta', 'creada_por').order_by('-fecha_creacion')


class CrearEncuestaView(LoginRequiredMixin, View):
    """Vista para crear una nueva encuesta"""
    template_name = 'surveys/admin/crear_encuesta.html'

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'No tienes permisos para crear encuestas')
            return redirect('surveys:index')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Mostrar formulario de creación"""
        tipos_encuesta = TipoEncuesta.objects.filter(activo=True)
        context = {
            'tipos_encuesta': tipos_encuesta
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Guardar nueva encuesta"""
        try:
            # Validar datos requeridos
            codigo = request.POST.get('codigo')
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            instrucciones = request.POST.get('instrucciones', '')
            tipo_encuesta_id = request.POST.get('tipo_encuesta')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')

            if not all([codigo, nombre, tipo_encuesta_id, fecha_inicio, fecha_fin]):
                messages.error(request, 'Todos los campos obligatorios deben ser completados')
                return redirect('surveys:crear_encuesta')

            # Verificar que el código sea único
            if Encuesta.objects.filter(codigo=codigo).exists():
                messages.error(request, f'El código "{codigo}" ya existe. Usa otro código.')
                return redirect('surveys:crear_encuesta')

            # Crear encuesta
            encuesta = Encuesta.objects.create(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                instrucciones=instrucciones,
                tipo_encuesta_id=tipo_encuesta_id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                creada_por=request.user,
                activa=True
            )

            messages.success(request, f'Encuesta "{nombre}" creada exitosamente. Ahora agrega las preguntas.')
            return redirect('surveys:editar_preguntas', pk=encuesta.pk)

        except Exception as e:
            messages.error(request, f'Error al crear encuesta: {str(e)}')
            return redirect('surveys:crear_encuesta')


class EditarPreguntasView(LoginRequiredMixin, View):
    """Vista para agregar/editar preguntas de una encuesta"""
    template_name = 'surveys/admin/editar_preguntas.html'

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'No tienes permisos para editar encuestas')
            return redirect('surveys:index')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        """Mostrar formulario de preguntas"""
        from apps.evaluations.models import TipoPregunta

        encuesta = get_object_or_404(Encuesta, pk=pk)
        preguntas = PreguntaEncuesta.objects.filter(encuesta=encuesta).order_by('orden')
        tipos_pregunta = TipoPregunta.objects.all()

        context = {
            'encuesta': encuesta,
            'preguntas': preguntas,
            'tipos_pregunta': tipos_pregunta
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        """Agregar nueva pregunta"""
        encuesta = get_object_or_404(Encuesta, pk=pk)

        try:
            pregunta_texto = request.POST.get('pregunta')
            tipo_pregunta_id = request.POST.get('tipo_pregunta')
            categoria = request.POST.get('categoria', '')
            descripcion = request.POST.get('descripcion', '')
            obligatoria = request.POST.get('obligatoria') == 'on'

            # Obtener siguiente orden
            ultimo_orden = PreguntaEncuesta.objects.filter(encuesta=encuesta).aggregate(
                max_orden=models.Max('orden')
            )['max_orden'] or 0

            # Crear pregunta
            pregunta = PreguntaEncuesta.objects.create(
                encuesta=encuesta,
                tipo_pregunta_id=tipo_pregunta_id,
                categoria=categoria,
                pregunta=pregunta_texto,
                descripcion=descripcion,
                obligatoria=obligatoria,
                orden=ultimo_orden + 1,
                activa=True
            )

            # Si tiene opciones, crearlas
            opciones = request.POST.getlist('opciones[]')
            valores = request.POST.getlist('valores[]')

            for idx, opcion_texto in enumerate(opciones):
                if opcion_texto.strip():
                    OpcionEncuesta.objects.create(
                        pregunta=pregunta,
                        opcion=opcion_texto,
                        valor_numerico=valores[idx] if idx < len(valores) and valores[idx].isdigit() else None,
                        orden=idx + 1,
                        activa=True
                    )

            messages.success(request, 'Pregunta agregada exitosamente')
            return redirect('surveys:editar_preguntas', pk=encuesta.pk)

        except Exception as e:
            messages.error(request, f'Error al agregar pregunta: {str(e)}')
            return redirect('surveys:editar_preguntas', pk=encuesta.pk)


class AsignarEncuestaView(LoginRequiredMixin, View):
    """Vista para asignar encuesta a empleados/áreas"""
    template_name = 'surveys/admin/asignar_encuesta.html'

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'No tienes permisos para asignar encuestas')
            return redirect('surveys:index')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        """Mostrar formulario de asignación"""
        from apps.employees.models import Empleado
        from apps.organizational.models import AreaEmpresa, Cargo

        encuesta = get_object_or_404(Encuesta, pk=pk)

        # Obtener empleados, áreas y cargos
        empleados = Empleado.objects.filter(estado__codigo='999').select_related('usuario', 'estado').order_by('apellidos', 'nombres')
        areas = AreaEmpresa.objects.all().order_by('nombre')
        cargos = Cargo.objects.all().order_by('nombre')

        # Obtener asignaciones existentes
        from .models import EncuestaArea, EncuestaCargo
        areas_asignadas = EncuestaArea.objects.filter(encuesta=encuesta).values_list('area_id', flat=True)
        cargos_asignados = EncuestaCargo.objects.filter(encuesta=encuesta).values_list('cargo_id', flat=True)

        # Obtener empleados que ya tienen participación
        participaciones_existentes = ParticipacionEncuesta.objects.filter(
            encuesta=encuesta
        ).values_list('empleado_id', flat=True)

        context = {
            'encuesta': encuesta,
            'empleados': empleados,
            'areas': areas,
            'cargos': cargos,
            'areas_asignadas': list(areas_asignadas),
            'cargos_asignados': list(cargos_asignados),
            'participaciones_existentes': list(participaciones_existentes)
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        """Procesar asignación"""
        from apps.employees.models import Empleado
        from apps.organizational.models import AreaEmpresa, Cargo
        from .models import EncuestaArea, EncuestaCargo

        encuesta = get_object_or_404(Encuesta, pk=pk)

        try:
            asignar_a = request.POST.get('asignar_a')

            if asignar_a == 'todos':
                # Asignar a todos los empleados activos
                empleados = Empleado.objects.filter(estado__codigo='999')
                creados = 0

                for empleado in empleados:
                    _, created = ParticipacionEncuesta.objects.get_or_create(
                        empleado=empleado,
                        encuesta=encuesta
                    )
                    if created:
                        creados += 1

                messages.success(request, f'Encuesta asignada a {creados} empleados')

            elif asignar_a == 'areas':
                # Asignar por áreas
                areas_ids = request.POST.getlist('areas[]')

                # Guardar relaciones
                EncuestaArea.objects.filter(encuesta=encuesta).delete()
                for area_id in areas_ids:
                    EncuestaArea.objects.create(encuesta=encuesta, area_id=area_id)

                # Crear participaciones para empleados de esas áreas
                creados = 0
                for area_id in areas_ids:
                    empleados = Empleado.objects.filter(
                        historialcargo__cargo__area_id=area_id,
                        historialcargo__activo=True,
                        estado__codigo='999'
                    ).distinct()

                    for empleado in empleados:
                        _, created = ParticipacionEncuesta.objects.get_or_create(
                            empleado=empleado,
                            encuesta=encuesta
                        )
                        if created:
                            creados += 1

                messages.success(request, f'Encuesta asignada a {creados} empleados de las áreas seleccionadas')

            elif asignar_a == 'cargos':
                # Asignar por cargos
                cargos_ids = request.POST.getlist('cargos[]')

                # Guardar relaciones
                EncuestaCargo.objects.filter(encuesta=encuesta).delete()
                for cargo_id in cargos_ids:
                    EncuestaCargo.objects.create(encuesta=encuesta, cargo_id=cargo_id)

                # Crear participaciones para empleados con esos cargos
                creados = 0
                for cargo_id in cargos_ids:
                    empleados = Empleado.objects.filter(
                        historialcargo__cargo_id=cargo_id,
                        historialcargo__activo=True,
                        estado__codigo='999'
                    ).distinct()

                    for empleado in empleados:
                        _, created = ParticipacionEncuesta.objects.get_or_create(
                            empleado=empleado,
                            encuesta=encuesta
                        )
                        if created:
                            creados += 1

                messages.success(request, f'Encuesta asignada a {creados} empleados de los cargos seleccionados')

            elif asignar_a == 'empleados':
                # Asignar a empleados específicos
                empleados_ids = request.POST.getlist('empleados[]')
                creados = 0

                for empleado_id in empleados_ids:
                    _, created = ParticipacionEncuesta.objects.get_or_create(
                        empleado_id=empleado_id,
                        encuesta=encuesta
                    )
                    if created:
                        creados += 1

                messages.success(request, f'Encuesta asignada a {creados} empleados seleccionados')

            return redirect('surveys:asignar_encuesta', pk=encuesta.pk)

        except Exception as e:
            messages.error(request, f'Error al asignar encuesta: {str(e)}')
            return redirect('surveys:asignar_encuesta', pk=encuesta.pk)

class ResultadosEncuestaView(LoginRequiredMixin, View):
    """Dashboard de resultados de una encuesta específica. Solo staff.

    Muestra por pregunta:
    - Con opciones: distribución (conteos + %) para cada OpcionEncuesta,
      más una fila "Otro (texto libre)" cuando hay respuestas sueltas.
    - Texto libre: lista de respuestas paginadas por respuesta_texto.
    """
    template_name = 'surveys/admin/resultados_encuesta.html'

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'No tienes permisos para ver resultados.')
            return redirect('surveys:index')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        encuesta = get_object_or_404(Encuesta, pk=pk)

        # === KPIs ===
        participaciones = ParticipacionEncuesta.objects.filter(encuesta=encuesta)
        total_part = participaciones.count()
        completadas = participaciones.filter(completada=True).count()
        en_progreso = total_part - completadas
        tiempo_promedio = participaciones.filter(
            completada=True, tiempo_empleado_minutos__isnull=False,
        ).aggregate(m=Avg('tiempo_empleado_minutos'))['m']

        # === Preguntas y distribuciones ===
        preguntas = list(
            PreguntaEncuesta.objects.filter(encuesta=encuesta, activa=True)
            .select_related('tipo_pregunta').order_by('orden')
        )

        # IDs de participaciones completadas — solo estas cuentan para agregación
        part_ids_completas = list(
            participaciones.filter(completada=True).values_list('id', flat=True)
        )

        preguntas_data = []
        tipos_con_opciones = {
            'multiple_choice', 'PREGMULT', 'select', 'rating',
            'ESCALA_5', 'ESCALA_3', 'SI_NO', 'checkbox',
        }
        for p in preguntas:
            respuestas_p = RespuestaEncuesta.objects.filter(
                pregunta=p, participacion_id__in=part_ids_completas,
            )
            total_resp = respuestas_p.count()

            item = {
                'pregunta': p,
                'total_respuestas': total_resp,
                'tiene_opciones': p.tipo_pregunta.codigo in tipos_con_opciones,
                'opciones': [],
                'respuestas_texto': [],
                'otras_texto_count': 0,
            }

            if item['tiene_opciones']:
                opciones = list(p.opcionencuesta_set.filter(activa=True).order_by('orden'))
                conteos = dict(
                    respuestas_p.exclude(opcion_seleccionada__isnull=True)
                    .values_list('opcion_seleccionada_id')
                    .annotate(n=Count('id')).values_list('opcion_seleccionada_id', 'n')
                )
                for o in opciones:
                    n = conteos.get(o.id, 0)
                    pct = round(100 * n / total_resp, 1) if total_resp else 0
                    item['opciones'].append({'opcion': o, 'n': n, 'pct': pct})
                # Texto libre ("Otro" o mismatch): respuestas sin opción pero con texto
                otras = respuestas_p.filter(
                    opcion_seleccionada__isnull=True,
                ).exclude(respuesta_texto='')
                item['otras_texto_count'] = otras.count()
                item['otras_texto'] = list(otras.values_list('respuesta_texto', flat=True)[:20])
            else:
                # Texto libre — muestro las últimas 50 respuestas
                item['respuestas_texto'] = list(
                    respuestas_p.exclude(respuesta_texto='')
                    .order_by('-fecha_respuesta')
                    .values_list('respuesta_texto', flat=True)[:50]
                )

            preguntas_data.append(item)

        # Cobertura: cuántos empleados fueron elegibles (asignados por cargo/área)
        # y cuántos respondieron. Si no hay asignación, cobertura queda como None.
        from apps.employees.models import Empleado
        from .models import EncuestaCargo, EncuestaArea
        cargos_asig = EncuestaCargo.objects.filter(encuesta=encuesta).values_list('cargo_id', flat=True)
        areas_asig = EncuestaArea.objects.filter(encuesta=encuesta).values_list('area_id', flat=True)
        cobertura_total = None
        if cargos_asig or areas_asig:
            filt = Q()
            if cargos_asig:
                filt |= Q(historialcargo__activo=True, historialcargo__cargo_id__in=list(cargos_asig))
            if areas_asig:
                filt |= Q(historialcargo__activo=True, historialcargo__cargo__area_id__in=list(areas_asig))
            cobertura_total = Empleado.objects.filter(filt, estado__codigo='999').distinct().count()

        pct_respuesta = (
            round(100 * completadas / cobertura_total, 1)
            if cobertura_total else None
        )

        return render(request, self.template_name, {
            'encuesta': encuesta,
            'total_participaciones': total_part,
            'completadas': completadas,
            'en_progreso': en_progreso,
            'tiempo_promedio': round(tiempo_promedio, 1) if tiempo_promedio else None,
            'cobertura_total': cobertura_total,
            'pct_respuesta': pct_respuesta,
            'preguntas_data': preguntas_data,
        })
