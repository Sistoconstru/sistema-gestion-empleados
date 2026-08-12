"""Cálculos del módulo de aprendices SENA.

Aísla la lógica de conteo, vencimientos y sanción para que la vista, los
widgets del dashboard y los cron jobs consuman la misma fuente.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional

from django.db.models import Q

# Duración típica de la ETAPA PRODUCTIVA del contrato de aprendizaje.
# El máximo legal es 2 años (Ley 789 art. 30) pero en Construinmuniza la
# productiva se firma por 6 meses por defecto. Para aprendices profesionales
# u otros casos particulares, RRHH puede fijar manualmente
# HistorialCargo.fecha_fin_contrato_aprendizaje y ese valor prevalece.
CONTRATO_APRENDIZAJE_MAX_MESES = 6
# Fallback si no hay SalarioMinimoAnual cargado — solo se usa como último
# recurso en caso de BD vacía. La fuente autoritativa es el modelo.
SMMLV_FALLBACK = Decimal('1423500')
DIAS_ALERTA_VENCIMIENTO = 60


def _smmlv_vigente() -> Decimal:
    """Retorna el SMMLV vigente desde la BD; cae al fallback si no hay registros."""
    from apps.organizational.models import SalarioMinimoAnual
    valor = SalarioMinimoAnual.valor_vigente()
    return valor if valor is not None else SMMLV_FALLBACK


@dataclass
class AprendizItem:
    empleado: object            # apps.employees.models.Empleado
    cargo: object               # apps.organizational.models.Cargo
    historial_id: int           # pk del HistorialCargo activo (para edición inline)
    fecha_inicio: date          # inicio del HistorialCargo activo
    fecha_fin_estimada: date    # fecha manual si existe, si no fecha_inicio + 6 meses
    fecha_fin_manual: bool      # True si RRHH cargó la fecha (override activo)
    dias_restantes: int         # (fecha_fin_estimada - hoy).days
    etapa: str                  # 'lectiva' | 'productiva'
    proximo_a_vencer: bool      # dias_restantes <= 60


@dataclass
class EstadoCuotaSena:
    """Snapshot del estado de cumplimiento de la cuota SENA hoy."""
    fecha: date
    resolucion: Optional[object]                # ResolucionSena o None
    cuota_requerida: int                        # 0 si no hay resolución vigente
    aprendices_actuales: int
    faltantes: int                              # max(cuota - actuales, 0)
    sancion_mensual_estimada: Decimal           # faltantes * 1 SMMLV
    cumple: bool                                # aprendices_actuales >= cuota_requerida
    aprendices: List[AprendizItem] = field(default_factory=list)
    proximos_a_vencer: List[AprendizItem] = field(default_factory=list)


def _etapa_desde_cargo(cargo) -> str:
    """En SIGHU, la lectiva se identifica porque su cargo no crea usuario del sistema."""
    return 'productiva' if getattr(cargo, 'crea_usuario_sistema', True) else 'lectiva'


def _fecha_fin_estimada(fecha_inicio: date) -> date:
    """Fin estimado del contrato de aprendizaje: 24 meses desde el inicio."""
    # Aproximación segura sin dependencia de dateutil.
    anios_extra, meses = divmod(CONTRATO_APRENDIZAJE_MAX_MESES, 12)
    nuevo_mes = fecha_inicio.month + meses
    nuevo_anio = fecha_inicio.year + anios_extra
    if nuevo_mes > 12:
        nuevo_mes -= 12
        nuevo_anio += 1
    from calendar import monthrange
    dia = min(fecha_inicio.day, monthrange(nuevo_anio, nuevo_mes)[1])
    return date(nuevo_anio, nuevo_mes, dia)


def calcular_estado(fecha: Optional[date] = None) -> EstadoCuotaSena:
    """Retorna el snapshot completo del cumplimiento SENA para la fecha dada."""
    from apps.employees.models import HistorialCargo
    from apps.organizational.models import ResolucionSena

    hoy = fecha or date.today()
    resolucion = ResolucionSena.vigente(hoy)
    cuota = resolucion.cuota_aprendices if resolucion else 0

    hcs = list(
        HistorialCargo.objects
        .filter(activo=True, cargo__es_cargo_aprendiz=True)
        .select_related('empleado', 'cargo')
        .order_by('fecha_inicio')
    )

    aprendices = []
    proximos = []
    for h in hcs:
        # Si RRHH cargó una fecha fin manual (aprendiz profesional u otros
        # casos), esa gana sobre el cálculo automático de 6 meses.
        manual = h.fecha_fin_contrato_aprendizaje is not None
        fin = h.fecha_fin_contrato_aprendizaje or _fecha_fin_estimada(h.fecha_inicio)
        dias_rest = (fin - hoy).days
        item = AprendizItem(
            empleado=h.empleado,
            cargo=h.cargo,
            historial_id=h.pk,
            fecha_inicio=h.fecha_inicio,
            fecha_fin_estimada=fin,
            fecha_fin_manual=manual,
            dias_restantes=dias_rest,
            etapa=_etapa_desde_cargo(h.cargo),
            proximo_a_vencer=(0 <= dias_rest <= DIAS_ALERTA_VENCIMIENTO),
        )
        aprendices.append(item)
        if item.proximo_a_vencer:
            proximos.append(item)

    actuales = len(aprendices)
    faltantes = max(cuota - actuales, 0)
    sancion = Decimal(faltantes) * _smmlv_vigente()

    return EstadoCuotaSena(
        fecha=hoy,
        resolucion=resolucion,
        cuota_requerida=cuota,
        aprendices_actuales=actuales,
        faltantes=faltantes,
        sancion_mensual_estimada=sancion,
        cumple=(actuales >= cuota),
        aprendices=aprendices,
        proximos_a_vencer=sorted(proximos, key=lambda x: x.dias_restantes),
    )
