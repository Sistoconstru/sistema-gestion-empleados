"""Segmentación de horas extras según jornadas (diurna / nocturna / dominical).

Reglas Construinmuniza — actualización Ley Colombia 2025:
- Jornada DIURNA:  06:00 hasta 19:00
- Jornada NOCTURNA: 19:00 hasta 06:00 del día siguiente
- DOMINICAL/FESTIVO: día completo cuando fecha es domingo o festivo oficial
  (usa el calendario `holidays` que ya maneja la Ley Emiliani).
"""

from datetime import date, time, datetime, timedelta
from decimal import Decimal

from .dias_habiles import es_festivo_oficial


HORA_INICIO_DIURNA = time(6, 0)   # 06:00
HORA_FIN_DIURNA = time(19, 0)     # 19:00 = inicio nocturna


def _es_domingo_o_festivo(fecha: date) -> bool:
    return fecha.weekday() == 6 or es_festivo_oficial(fecha)


def _horas_entre(dt_ini: datetime, dt_fin: datetime) -> Decimal:
    """Diferencia en horas como Decimal con 2 decimales."""
    segundos = (dt_fin - dt_ini).total_seconds()
    return (Decimal(segundos) / Decimal('3600')).quantize(Decimal('0.01'))


def segmentar_hora_extra(fecha: date, hora_inicio: time, hora_fin: time) -> list[dict]:
    """Segmenta un rango de horas extras en 1 o más tramos según jornada.

    Args:
        fecha: fecha del INICIO del rango (si cruza medianoche, el resto se
            considera del mismo turno).
        hora_inicio: hora de inicio dentro del día.
        hora_fin: hora de fin. Si es <= hora_inicio se asume cruce de medianoche.

    Returns:
        Lista de dicts con: {'tipo', 'hora_inicio', 'hora_fin', 'total_horas'}.
        Cada dict corresponde a una novedad que debe crearse.
        - Si `fecha` es domingo/festivo → una sola entrada de tipo
          'hora_extra_dominical' con el total del rango.
        - Si el rango cae completo en diurno o nocturno → una sola entrada.
        - Si cruza 07:00 pm (u otro corte) → múltiples entradas.

    Raises:
        ValueError si el rango resultante es <= 0 minutos.
    """
    # Anclar en un datetime concreto para poder sumar timedeltas fácilmente
    anchor = datetime.combine(fecha, hora_inicio)
    dt_ini = anchor
    dt_fin = datetime.combine(fecha, hora_fin)
    if dt_fin <= dt_ini:
        dt_fin += timedelta(days=1)  # cruza medianoche

    if dt_fin <= dt_ini:
        raise ValueError("El rango de horas debe ser mayor a 0.")

    # Caso especial: domingo o festivo → todo dominical
    if _es_domingo_o_festivo(fecha):
        return [{
            'tipo': 'hora_extra_dominical',
            'hora_inicio': hora_inicio,
            'hora_fin': hora_fin,
            'total_horas': _horas_entre(dt_ini, dt_fin),
        }]

    # Día laboral (L-S no festivo): segmentar por cortes diurna/nocturna.
    # Recorremos el rango sumando tramos según el corte de las 19:00.
    # Los tramos entre 06:00 y 19:00 → diurno.
    # Los tramos entre 19:00 y 06:00 del día siguiente → nocturno.
    tramos = []
    cursor = dt_ini
    while cursor < dt_fin:
        # ¿En qué franja estoy?
        hora_actual = cursor.time()
        fecha_actual = cursor.date()

        if HORA_INICIO_DIURNA <= hora_actual < HORA_FIN_DIURNA:
            # DIURNO — hasta las 19:00 del mismo día o hasta dt_fin
            corte = datetime.combine(fecha_actual, HORA_FIN_DIURNA)
            fin_tramo = min(corte, dt_fin)
            tipo = 'hora_extra_diurna'
        else:
            # NOCTURNO — hasta las 06:00 del día siguiente o hasta dt_fin
            if hora_actual >= HORA_FIN_DIURNA:
                # 19:00 a 23:59 → corte es 06:00 del día siguiente
                corte = datetime.combine(fecha_actual + timedelta(days=1), HORA_INICIO_DIURNA)
            else:
                # 00:00 a 05:59 → corte es 06:00 del mismo día
                corte = datetime.combine(fecha_actual, HORA_INICIO_DIURNA)
            fin_tramo = min(corte, dt_fin)
            tipo = 'hora_extra_nocturna'

        tramos.append({
            'tipo': tipo,
            'hora_inicio': cursor.time(),
            'hora_fin': fin_tramo.time(),
            'total_horas': _horas_entre(cursor, fin_tramo),
        })
        cursor = fin_tramo

    # Consolidar tramos consecutivos del mismo tipo (caso raro pero posible)
    consolidados = []
    for t in tramos:
        if consolidados and consolidados[-1]['tipo'] == t['tipo']:
            consolidados[-1]['hora_fin'] = t['hora_fin']
            consolidados[-1]['total_horas'] += t['total_horas']
        else:
            consolidados.append(t)

    return consolidados
