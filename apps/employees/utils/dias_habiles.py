"""Cálculo de días hábiles y festivos según jornada Construinmuniza.

Regla local: la semana laboral es de lunes a sábado. Los domingos y los
festivos oficiales de Colombia (con Ley Emiliani aplicada) NO son hábiles.
"""

from datetime import date, timedelta
from functools import lru_cache

import holidays


@lru_cache(maxsize=32)
def _festivos_del_anio(year: int) -> frozenset:
    """Festivos oficiales Colombia para un año (con Ley Emiliani ya aplicada).

    Cacheado por año — es una consulta puramente determinista.
    """
    return frozenset(holidays.Colombia(years=[year]).keys())


def es_festivo_oficial(d: date) -> bool:
    """True si la fecha es festivo oficial en Colombia (excluye domingos)."""
    return d in _festivos_del_anio(d.year)


def es_domingo(d: date) -> bool:
    return d.weekday() == 6  # lunes=0 ... domingo=6


def es_habil(d: date) -> bool:
    """True si la fecha es día hábil (L-S y no festivo)."""
    if es_domingo(d):
        return False
    if es_festivo_oficial(d):
        return False
    return True


def es_no_habil(d: date) -> bool:
    """True si la fecha NO es hábil (domingo o festivo)."""
    return not es_habil(d)


def clasificar_rango(inicio: date, fin: date) -> dict:
    """Cuenta días hábiles y no hábiles (festivos + domingos) en un rango
    inclusive.

    Returns:
        dict con:
            - 'total': total de días calendario.
            - 'habiles': número de días L-S no festivos.
            - 'festivos': número de días domingo o festivo.
            - 'detalle_festivos': lista de dates que fueron festivo/domingo.
    """
    if inicio > fin:
        return {'total': 0, 'habiles': 0, 'festivos': 0, 'detalle_festivos': []}

    total = 0
    habiles = 0
    festivos_lista = []
    cursor = inicio
    while cursor <= fin:
        total += 1
        if es_habil(cursor):
            habiles += 1
        else:
            festivos_lista.append(cursor)
        cursor += timedelta(days=1)

    return {
        'total': total,
        'habiles': habiles,
        'festivos': len(festivos_lista),
        'detalle_festivos': festivos_lista,
    }


def proximo_dia_habil(d: date) -> date:
    """Retorna el primer día hábil estrictamente posterior a `d`.

    Ej: si fecha_fin de vacaciones es viernes → regresa el sábado (si es hábil)
    o si es sábado y el domingo no es festivo → lunes.
    """
    candidato = d + timedelta(days=1)
    # Ceiling defensivo: en escenarios patológicos (feriados consecutivos),
    # no más de 30 días de avance
    limite = 30
    while limite > 0:
        if es_habil(candidato):
            return candidato
        candidato += timedelta(days=1)
        limite -= 1
    return candidato  # fallback
