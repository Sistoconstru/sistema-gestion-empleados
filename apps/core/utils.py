# =============================================================================
# apps/core/utils.py
# Utilidades para el sistema de auditoría
# =============================================================================

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def registrar_auditoria(
    usuario,
    accion: str,
    modelo: str,
    objeto_id: Optional[str] = None,
    cambios: Optional[Dict[str, Any]] = None,
    descripcion: str = '',
    ip_address: str = '0.0.0.0',
    user_agent: str = '',
    metodo_http: str = 'MANUAL',
    url: str = ''
) -> None:
    """
    Función helper para registrar auditoría manualmente.

    Útil para:
    - Operaciones que no pasan por el middleware (commands, signals, etc.)
    - Agregar logs personalizados desde código
    - Registrar eventos del sistema

    Args:
        usuario: Usuario que realiza la acción (puede ser None para acciones del sistema)
        accion: Tipo de acción (crear, modificar, eliminar, etc.)
        modelo: Nombre del modelo afectado
        objeto_id: ID del objeto afectado (opcional)
        cambios: Diccionario con los cambios realizados (opcional)
        ip_address: Dirección IP (default: 0.0.0.0 para acciones del sistema)
        user_agent: User agent del navegador (opcional)
        metodo_http: Método HTTP usado (default: MANUAL)
        url: URL accedida (opcional)

    Ejemplo de uso:
        from apps.core.utils import registrar_auditoria

        # Registrar cambio de estado de empleado
        registrar_auditoria(
            usuario=request.user,
            accion='cambiar_estado',
            modelo='Empleado',
            objeto_id=str(empleado.pk),
            cambios={
                'estado_anterior': 'PRUEBA',
                'estado_nuevo': 'ACTIVO',
                'razon': 'Cumplió periodo de prueba'
            },
            ip_address='192.168.1.1'
        )

        # Registrar acción del sistema (scheduler)
        registrar_auditoria(
            usuario=None,
            accion='asignar_evaluacion_automatica',
            modelo='AsignacionEvaluacion',
            cambios={
                'evaluaciones_creadas': 5,
                'tipo': 'periodo_prueba'
            }
        )
    """
    try:
        from apps.core.models import LogActividad

        # Generar descripción automática si no se proporciona
        if not descripcion:
            usuario_nombre = usuario.username if usuario else 'Sistema'
            descripcion = f"{usuario_nombre} {accion} {modelo}"

        LogActividad.objects.create(
            usuario=usuario,
            accion=accion,
            modelo=modelo,
            objeto_id=objeto_id,
            descripcion=descripcion,
            cambios_realizados=cambios,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else '',
            metodo_http=metodo_http[:10],
            url_accedida=url[:500] if url else ''
        )

        logger.info(
            f"Auditoría registrada: {descripcion}"
        )

    except Exception as e:
        # No fallar si hay error en auditoría, solo loguear
        logger.error(f"Error al registrar auditoría: {e}", exc_info=True)


def obtener_ip_desde_request(request) -> str:
    """
    Extrae la IP real del cliente desde el request.
    Considera proxies y balanceadores de carga.

    Args:
        request: Objeto HttpRequest de Django

    Returns:
        str: Dirección IP del cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip


def registrar_auditoria_desde_request(
    request,
    accion: str,
    modelo: str,
    objeto_id: Optional[str] = None,
    cambios: Optional[Dict[str, Any]] = None,
    metodo_http: Optional[str] = None
) -> None:
    """
    Versión simplificada que extrae automáticamente datos del request.

    Args:
        request: Objeto HttpRequest de Django
        accion: Tipo de acción
        modelo: Nombre del modelo
        objeto_id: ID del objeto (opcional)
        cambios: Cambios realizados (opcional)
        metodo_http: Método HTTP (si no se especifica, se extrae del request)

    Ejemplo de uso:
        from apps.core.utils import registrar_auditoria_desde_request

        def cambiar_cargo_empleado(request, empleado_id):
            empleado = Empleado.objects.get(pk=empleado_id)
            cargo_anterior = empleado.cargo_actual

            # ... lógica de cambio de cargo ...

            registrar_auditoria_desde_request(
                request=request,
                accion='cambiar_cargo',
                modelo='Empleado',
                objeto_id=str(empleado.pk),
                cambios={
                    'cargo_anterior': cargo_anterior.nombre,
                    'cargo_nuevo': nuevo_cargo.nombre
                }
            )
    """
    usuario = request.user if request.user.is_authenticated else None
    ip_address = obtener_ip_desde_request(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    metodo = metodo_http or request.method
    url = request.path

    registrar_auditoria(
        usuario=usuario,
        accion=accion,
        modelo=modelo,
        objeto_id=objeto_id,
        cambios=cambios,
        ip_address=ip_address,
        user_agent=user_agent,
        metodo_http=metodo,
        url=url
    )


def obtener_cambios_modelo(instancia_anterior, instancia_nueva, campos_excluir=None) -> Dict[str, Any]:
    """
    Compara dos instancias del mismo modelo y retorna un diccionario con los cambios.

    Args:
        instancia_anterior: Instancia del modelo antes del cambio
        instancia_nueva: Instancia del modelo después del cambio
        campos_excluir: Lista de campos a excluir (opcional)

    Returns:
        Dict con formato: {'campo': {'anterior': valor, 'nuevo': valor}}

    Ejemplo de uso:
        from apps.core.utils import obtener_cambios_modelo

        empleado_anterior = Empleado.objects.get(pk=empleado_id)
        # ... se modifica el empleado ...
        empleado.save()
        empleado.refresh_from_db()

        cambios = obtener_cambios_modelo(
            empleado_anterior,
            empleado,
            campos_excluir=['fecha_actualizacion']
        )
    """
    if campos_excluir is None:
        campos_excluir = ['fecha_actualizacion', 'fecha_modificacion', 'updated_at']

    cambios = {}

    # Obtener todos los campos del modelo
    for field in instancia_anterior._meta.fields:
        campo_nombre = field.name

        # Saltar campos excluidos
        if campo_nombre in campos_excluir:
            continue

        valor_anterior = getattr(instancia_anterior, campo_nombre)
        valor_nuevo = getattr(instancia_nueva, campo_nombre)

        # Solo registrar si cambió
        if valor_anterior != valor_nuevo:
            # Convertir a string para evitar problemas con tipos no serializables
            cambios[campo_nombre] = {
                'anterior': str(valor_anterior) if valor_anterior is not None else None,
                'nuevo': str(valor_nuevo) if valor_nuevo is not None else None
            }

    return cambios
