# =============================================================================
# apps/employees/views_polla_mundial.py
# Vistas para la Polla Mundialista 2026
# =============================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import PartidoMundial, PrediccionMundial, Empleado
from .forms import PrediccionMundialForm


@login_required
def polla_mundial_lista(request):
    """Vista principal de la polla mundial - Lista de partidos"""

    # Verificar que el usuario tiene perfil de empleado
    if not hasattr(request.user, 'empleado'):
        messages.error(
            request,
            'Para participar en la Polla Mundial debes tener un perfil de empleado. '
            'Contacta al administrador del sistema.'
        )
        return redirect('producto_list')

    # Obtener filtros
    fase_filter = request.GET.get('fase', '')
    estado_filter = request.GET.get('estado', 'proximos')  # proximos, finalizados, todos

    # Obtener partidos
    partidos = PartidoMundial.objects.filter(activo=True)

    # Aplicar filtro de fase
    if fase_filter:
        partidos = partidos.filter(fase=fase_filter)

    # Aplicar filtro de estado
    if estado_filter == 'proximos':
        partidos = partidos.filter(finalizado=False, fecha_hora__gte=timezone.now())
    elif estado_filter == 'finalizados':
        partidos = partidos.filter(finalizado=True)
    # 'todos' no aplica filtro adicional

    # Ordenar por fecha
    partidos = partidos.order_by('fecha_hora')

    # Obtener predicciones del empleado actual
    empleado = request.user.empleado
    predicciones_dict = {}

    if empleado:
        predicciones = PrediccionMundial.objects.filter(
            empleado=empleado,
            partido__in=partidos
        ).select_related('partido')

        predicciones_dict = {
            pred.partido_id: pred for pred in predicciones
        }

    # Anotar cada partido con la predicción del usuario
    partidos_con_prediccion = []
    for partido in partidos:
        partido.mi_prediccion = predicciones_dict.get(partido.id)
        partidos_con_prediccion.append(partido)

    # Obtener estadísticas del usuario
    total_predicciones = PrediccionMundial.objects.filter(empleado=empleado).count()
    total_puntos = PrediccionMundial.objects.filter(empleado=empleado).aggregate(
        total=Sum('puntos_ganados')
    )['total'] or 0

    # Obtener ranking del usuario con criterios de desempate
    from django.db.models import Case, When, IntegerField, F, Avg, ExpressionWrapper, DurationField

    ranking = PrediccionMundial.objects.filter(
        empleado__isnull=False
    ).values('empleado').annotate(
        total_puntos=Sum('puntos_ganados'),
        total_predicciones=Count('id'),
        # Contar ganadores acertados (puntos >= 3 pero < 5, o puntos >= 3 con bonificación de goles)
        ganadores_acertados=Count(
            Case(
                When(puntos_ganados__gte=3, then=1),
                output_field=IntegerField()
            )
        ),
        # Contar marcadores exactos (5 puntos base o más por multiplicador)
        marcadores_exactos=Count(
            Case(
                When(puntos_ganados__gte=5, then=1),
                output_field=IntegerField()
            )
        ),
        # Promedio de anticipación: cuánto tiempo antes del partido hace sus predicciones
        anticipacion_promedio=Avg(
            ExpressionWrapper(
                F('partido__fecha_hora') - F('fecha_prediccion'),
                output_field=DurationField()
            )
        )
    ).order_by('-total_puntos', '-ganadores_acertados', '-marcadores_exactos', '-total_predicciones', '-anticipacion_promedio')

    posicion_usuario = None
    for idx, entry in enumerate(ranking, 1):
        if entry['empleado'] == empleado.id:
            posicion_usuario = idx
            break

    # Obtener TOP 10 para mostrar en banner
    top_10 = []
    for idx, entry in enumerate(ranking[:10], 1):
        try:
            emp = Empleado.objects.get(id=entry['empleado'])
            top_10.append({
                'posicion': idx,
                'empleado': emp,
                'puntos': entry['total_puntos']
            })
        except Empleado.DoesNotExist:
            continue

    # Opciones de fases para el filtro
    fases = PartidoMundial.FASES

    context = {
        'partidos': partidos_con_prediccion,
        'fases': fases,
        'fase_filter': fase_filter,
        'estado_filter': estado_filter,
        'total_predicciones': total_predicciones,
        'total_puntos': total_puntos,
        'posicion_usuario': posicion_usuario,
        'top_10': top_10,
    }

    return render(request, 'employees/polla_mundial/partidos_list.html', context)


@login_required
@require_POST
def guardar_prediccion(request, partido_id):
    """Vista AJAX para guardar/actualizar predicción de un partido"""

    # Verificar que el usuario tiene perfil de empleado
    if not hasattr(request.user, 'empleado'):
        return JsonResponse({
            'success': False,
            'error': 'Debes tener un perfil de empleado para participar'
        }, status=403)

    partido = get_object_or_404(PartidoMundial, id=partido_id, activo=True)
    empleado = request.user.empleado

    # Verificar que el empleado aceptó los términos y condiciones
    if not empleado.acepto_terminos_polla_mundial:
        return JsonResponse({
            'success': False,
            'error': 'Debes aceptar los términos y condiciones antes de participar',
            'mostrar_terminos': True  # Flag para que el frontend muestre el modal
        }, status=403)

    # Verificar que el partido aún acepta predicciones
    if not partido.acepta_predicciones:
        return JsonResponse({
            'success': False,
            'error': 'Este partido ya no acepta predicciones'
        }, status=400)

    # Intentar obtener predicción existente
    try:
        prediccion = PrediccionMundial.objects.get(
            empleado=empleado,
            partido=partido
        )
        created = False
    except PrediccionMundial.DoesNotExist:
        prediccion = None
        created = True

    # Procesar el formulario
    form = PrediccionMundialForm(
        request.POST,
        instance=prediccion,
        partido=partido,
        empleado=empleado
    )

    if form.is_valid():
        prediccion = form.save(commit=False)
        prediccion.empleado = empleado
        prediccion.partido = partido
        prediccion.save()

        return JsonResponse({
            'success': True,
            'message': 'Predicción guardada exitosamente' if created else 'Predicción actualizada',
            'prediccion': {
                'goles_local': prediccion.goles_local_prediccion,
                'goles_visitante': prediccion.goles_visitante_prediccion
            }
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)


@login_required
def ranking_mundial(request):
    """Vista del ranking completo de la polla mundial"""

    from django.db.models import Case, When, IntegerField, F, Avg, ExpressionWrapper, DurationField

    # Obtener todos los empleados con predicciones
    ranking_data = PrediccionMundial.objects.filter(
        empleado__isnull=False
    ).values('empleado').annotate(
        total_puntos=Sum('puntos_ganados'),
        total_predicciones=Count('id'),
        aciertos_exactos=Count('id', filter=Q(puntos_ganados__gte=5)),
        ganadores_acertados=Count(
            Case(
                When(puntos_ganados__gte=3, then=1),
                output_field=IntegerField()
            )
        ),
        # Promedio de anticipación: cuánto tiempo antes del partido hace sus predicciones
        anticipacion_promedio=Avg(
            ExpressionWrapper(
                F('partido__fecha_hora') - F('fecha_prediccion'),
                output_field=DurationField()
            )
        )
    ).order_by('-total_puntos', '-ganadores_acertados', '-aciertos_exactos', '-total_predicciones', '-anticipacion_promedio')

    # Enriquecer con datos del empleado
    ranking = []
    for idx, entry in enumerate(ranking_data, 1):
        try:
            empleado = Empleado.objects.get(id=entry['empleado'])

            # Convertir anticipación promedio a formato legible
            anticipacion = entry.get('anticipacion_promedio')
            if anticipacion:
                dias = anticipacion.days
                horas = anticipacion.seconds // 3600
                if dias > 0:
                    anticipacion_texto = f"{dias}d {horas}h"
                else:
                    anticipacion_texto = f"{horas}h"
            else:
                anticipacion_texto = "-"

            # Calcular efectividad en porcentaje (basado en 5 puntos máximo base)
            if entry['total_predicciones'] > 0:
                promedio_puntos = entry['total_puntos'] / entry['total_predicciones']
                efectividad = round((promedio_puntos / 5) * 100, 1)
            else:
                efectividad = 0

            ranking.append({
                'posicion': idx,
                'empleado': empleado,
                'total_puntos': entry['total_puntos'],
                'total_predicciones': entry['total_predicciones'],
                'aciertos_exactos': entry['aciertos_exactos'],
                'efectividad': efectividad,
                'anticipacion': anticipacion_texto
            })
        except Empleado.DoesNotExist:
            continue

    # Estadísticas generales
    total_partidos = PartidoMundial.objects.filter(activo=True).count()
    partidos_finalizados = PartidoMundial.objects.filter(activo=True, finalizado=True).count()
    total_participantes = len(ranking)

    context = {
        'ranking': ranking,
        'total_partidos': total_partidos,
        'partidos_finalizados': partidos_finalizados,
        'total_participantes': total_participantes,
    }

    return render(request, 'employees/polla_mundial/ranking.html', context)


@login_required
@require_POST
def aceptar_terminos_polla(request):
    """Vista AJAX para aceptar términos y condiciones de la Polla Mundial"""

    if not hasattr(request.user, 'empleado'):
        return JsonResponse({
            'success': False,
            'error': 'Debes tener un perfil de empleado'
        }, status=403)

    empleado = request.user.empleado

    # Registrar aceptación
    from django.utils import timezone
    empleado.acepto_terminos_polla_mundial = True
    empleado.fecha_aceptacion_terminos_polla = timezone.now()
    empleado.save()

    return JsonResponse({
        'success': True,
        'message': 'Términos aceptados correctamente'
    })


@login_required
def estadisticas_partido(request, partido_id):
    """Vista AJAX para obtener estadísticas de predicciones de un partido"""

    partido = get_object_or_404(PartidoMundial, id=partido_id, activo=True)
    predicciones = PrediccionMundial.objects.filter(partido=partido)

    total_predicciones = predicciones.count()

    if total_predicciones == 0:
        return JsonResponse({
            'total': 0,
            'tendencias': {},
            'marcadores': []
        })

    # Calcular tendencias (ganador)
    local_gana = 0
    visitante_gana = 0
    empate = 0

    for pred in predicciones:
        if pred.goles_local_prediccion > pred.goles_visitante_prediccion:
            local_gana += 1
        elif pred.goles_local_prediccion < pred.goles_visitante_prediccion:
            visitante_gana += 1
        else:
            empate += 1

    # Agrupar por marcador
    from collections import Counter
    marcadores = Counter()

    for pred in predicciones:
        marcador = f"{pred.goles_local_prediccion}-{pred.goles_visitante_prediccion}"
        marcadores[marcador] += 1

    # Ordenar por popularidad
    marcadores_lista = [
        {'marcador': marcador, 'cantidad': cantidad}
        for marcador, cantidad in marcadores.most_common()
    ]

    return JsonResponse({
        'total': total_predicciones,
        'tendencias': {
            'local': {'cantidad': local_gana, 'porcentaje': round(local_gana / total_predicciones * 100)},
            'visitante': {'cantidad': visitante_gana, 'porcentaje': round(visitante_gana / total_predicciones * 100)},
            'empate': {'cantidad': empate, 'porcentaje': round(empate / total_predicciones * 100)}
        },
        'marcadores': marcadores_lista,
        'equipo_local': partido.equipo_local,
        'equipo_visitante': partido.equipo_visitante
    })


@login_required
def mis_predicciones(request):
    """Vista de predicciones del usuario actual"""

    # Verificar que el usuario tiene perfil de empleado
    if not hasattr(request.user, 'empleado'):
        messages.error(
            request,
            'Para ver tus predicciones debes tener un perfil de empleado. '
            'Contacta al administrador del sistema.'
        )
        return redirect('producto_list')

    empleado = request.user.empleado

    # Obtener todas las predicciones del empleado
    predicciones = PrediccionMundial.objects.filter(
        empleado=empleado
    ).select_related('partido').order_by('-partido__fecha_hora')

    # Agrupar por fase
    predicciones_por_fase = {}
    for prediccion in predicciones:
        fase = prediccion.partido.get_fase_display()
        if fase not in predicciones_por_fase:
            predicciones_por_fase[fase] = []
        predicciones_por_fase[fase].append(prediccion)

    # Estadísticas
    total_puntos = predicciones.aggregate(total=Sum('puntos_ganados'))['total'] or 0
    total_predicciones = predicciones.count()
    aciertos_exactos = predicciones.filter(puntos_ganados__gte=5).count()

    context = {
        'predicciones_por_fase': predicciones_por_fase,
        'total_puntos': total_puntos,
        'total_predicciones': total_predicciones,
        'aciertos_exactos': aciertos_exactos,
    }

    return render(request, 'employees/polla_mundial/mis_predicciones.html', context)
