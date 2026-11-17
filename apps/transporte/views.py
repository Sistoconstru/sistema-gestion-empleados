"""Flota: ver los vehículos y asignarles conductor.

La asignación es lo que más se usa y por eso vive aquí y no en el admin de
Django: la hace el coordinador, no un técnico. Al guardar se le avisa a
Odoo, que es el dueño del maestro; si Odoo no contesta, el cambio queda
registrado y se reintenta solo.
"""
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.employees.models import Empleado

from .models import DocumentoVehiculo, Vehiculo
from .permisos import (
    admin_transporte_required, conductores_a_cargo, es_admin_transporte,
    es_conductor, empleado_de, transporte_required, vehiculos_visibles,
)


@login_required
@transporte_required
def flota(request):
    """Listado de vehículos con el estado de sus documentos."""
    vehiculos = list(
        vehiculos_visibles(request.user)
        .select_related('conductor')
        .prefetch_related(Prefetch(
            'documentos',
            queryset=DocumentoVehiculo.objects.order_by('tipo', '-fecha_vencimiento'),
        ))
        .order_by('-activo', 'placa')
    )

    empleado = empleado_de(request.user)
    es_admin = es_admin_transporte(request.user)

    # Los conductores que este usuario puede asignar. El staff ve todos los
    # que tengan cargo de conductor; un coordinador, solo los suyos.
    if es_admin:
        if request.user.is_staff:
            from .permisos import conductores_vigentes
            asignables = conductores_vigentes()
        else:
            asignables = conductores_a_cargo(empleado)
    else:
        asignables = Empleado.objects.none()

    # Resumen para el encabezado: lo que exige atención.
    vencidos = por_vencer = 0
    for v in vehiculos:
        for d in v.documentos_vigentes():
            if not d.aplica:
                continue
            if d.esta_vencido:
                vencidos += 1
            elif d.por_vencer:
                por_vencer += 1

    return render(request, 'transporte/flota.html', {
        'vehiculos': vehiculos,
        'hoy': timezone.localdate(),
        'es_admin': es_admin,
        'asignables': asignables.order_by('apellidos', 'nombres'),
        'total_vencidos': vencidos,
        'total_por_vencer': por_vencer,
        'sin_conductor': sum(1 for v in vehiculos if v.activo and not v.conductor_id),
        'es_solo_conductor': es_conductor(empleado) and not es_admin,
    })


@login_required
@admin_transporte_required
@require_POST
def asignar_conductor(request, vehiculo_id):
    """Asigna, cambia o quita el conductor de un vehículo.

    El aviso a Odoo lo dispara el signal al guardar. Aquí solo se traduce el
    resultado a un mensaje que explique qué pasó, porque "se guardó pero
    Odoo no se enteró todavía" no es lo mismo que "se guardó".
    """
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)

    if vehiculo not in vehiculos_visibles(request.user):
        messages.error(request, 'Ese vehículo no es de tu flota.')
        return redirect('transporte:flota')

    if not vehiculo.activo:
        messages.error(
            request,
            f'{vehiculo.placa} está dado de baja en Odoo, no admite conductor.')
        return redirect('transporte:flota')

    conductor_id = (request.POST.get('conductor') or '').strip()
    desde_raw = (request.POST.get('desde') or '').strip()
    try:
        desde = date.fromisoformat(desde_raw) if desde_raw else timezone.localdate()
    except ValueError:
        messages.error(request, 'La fecha de inicio no es válida.')
        return redirect('transporte:flota')

    if desde > timezone.localdate():
        messages.error(request, 'La asignación no puede empezar en el futuro.')
        return redirect('transporte:flota')

    anterior = vehiculo.conductor

    if not conductor_id:
        if not anterior:
            messages.info(request, f'{vehiculo.placa} ya estaba sin conductor.')
            return redirect('transporte:flota')
        vehiculo.conductor = None
        vehiculo.save()
        messages.success(
            request,
            f'{vehiculo.placa} queda sin conductor. '
            f'{anterior.nombre_completo} ya no lo tiene asignado.')
        return redirect('transporte:flota')

    # Solo se puede asignar a alguien que este usuario administre.
    if request.user.is_staff:
        from .permisos import conductores_vigentes
        permitidos = conductores_vigentes()
    else:
        permitidos = conductores_a_cargo(empleado_de(request.user))

    nuevo = permitidos.filter(pk=conductor_id).first()
    if not nuevo:
        messages.error(
            request, 'Ese conductor no está entre los que puedes asignar.')
        return redirect('transporte:flota')

    if anterior and anterior.pk == nuevo.pk:
        messages.info(
            request, f'{nuevo.nombre_completo} ya conducía {vehiculo.placa}.')
        return redirect('transporte:flota')

    # Un conductor no puede tener dos vehículos a la vez: Odoo cierra la
    # asignación anterior, así que conviene que SIGHU muestre lo mismo.
    otro = Vehiculo.objects.filter(
        conductor=nuevo, activo=True).exclude(pk=vehiculo.pk).first()

    vehiculo.conductor = nuevo
    vehiculo.asignacion_desde = desde
    vehiculo.save()
    vehiculo.refresh_from_db()

    if otro:
        otro.conductor = None
        otro.save()
        messages.info(
            request,
            f'{nuevo.nombre_completo} dejó de tener asignado {otro.placa}.')

    if vehiculo.asignacion_sincronizada:
        messages.success(
            request,
            f'{nuevo.nombre_completo} queda asignado a {vehiculo.placa} '
            f'desde el {desde:%d/%m/%Y}. Odoo ya lo registró.')
    else:
        messages.warning(
            request,
            f'{nuevo.nombre_completo} queda asignado a {vehiculo.placa} '
            f'desde el {desde:%d/%m/%Y}, pero Odoo no respondió. '
            f'El aviso se reintenta solo; no hay que repetir la asignación.')

    return redirect('transporte:flota')


@login_required
@transporte_required
def detalle_vehiculo(request, vehiculo_id):
    """Ficha del vehículo con el historial completo de documentos."""
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)
    if vehiculo not in vehiculos_visibles(request.user):
        messages.error(request, 'Ese vehículo no es de tu flota.')
        return redirect('transporte:flota')

    documentos = vehiculo.documentos.order_by('tipo', '-fecha_vencimiento')
    vigentes = {d.tipo: d for d in vehiculo.documentos_vigentes()}

    # Un renglón por tipo, con su documento vigente o sin él. Se arma aquí
    # porque la plantilla no puede indexar un diccionario por variable y
    # resolverlo allá sale en un enredo de bucles anidados.
    estado_por_tipo = [
        {'nombre': nombre, 'doc': vigentes.get(codigo)}
        for codigo, nombre in DocumentoVehiculo.TIPOS
    ]

    return render(request, 'transporte/detalle_vehiculo.html', {
        'vehiculo': vehiculo,
        'documentos': documentos,
        'estado_por_tipo': estado_por_tipo,
        'es_admin': es_admin_transporte(request.user),
    })
