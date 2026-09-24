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

    Cada tramo devuelto incluye la `fecha` real donde se ubica (no
    necesariamente la fecha inicial): si el rango cruza medianoche, los
    tramos posteriores se marcan con la fecha del día siguiente.

    Args:
        fecha: fecha del INICIO del rango.
        hora_inicio: hora de inicio dentro del día `fecha`.
        hora_fin: hora de fin. Si es <= hora_inicio se asume cruce de medianoche.

    Returns:
        Lista de dicts con: {'fecha', 'tipo', 'hora_inicio', 'hora_fin',
        'total_horas'}. Se consolidan tramos consecutivos del mismo (fecha,tipo).

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

    # Recorremos el rango cortando en cada límite relevante:
    #  a) cambio de día (medianoche)  → nueva fecha, posible cambio de tipo
    #     por domingo/festivo del día siguiente
    #  b) corte 06:00 y 19:00 dentro del día → cambio diurna/nocturna
    # En un día domingo/festivo distinguimos:
    #   06:00-19:00 → hora_extra_dominical_diurna
    #   19:00-06:00 → hora_extra_dominical_nocturna
    tramos = []
    cursor = dt_ini
    while cursor < dt_fin:
        fecha_actual = cursor.date()
        hora_actual = cursor.time()
        es_dominical = _es_domingo_o_festivo(fecha_actual)

        # El próximo cambio de día siempre es un candidato de corte
        prox_dia = datetime.combine(fecha_actual + timedelta(days=1), time(0, 0))

        if HORA_INICIO_DIURNA <= hora_actual < HORA_FIN_DIURNA:
            # Franja diurna — corta en 19:00 o al cambio de día.
            corte_diurna = datetime.combine(fecha_actual, HORA_FIN_DIURNA)
            fin_tramo = min(corte_diurna, prox_dia, dt_fin)
            tipo = ('hora_extra_dominical_diurna' if es_dominical
                    else 'hora_extra_diurna')
        else:
            # Franja nocturna — corta en 06:00 del día en que estemos y en
            # el cambio de día. Cuando estamos en 19:00-23:59, el corte de
            # 06:00 cae en el día siguiente y NO se usa hasta cruzar medianoche.
            if hora_actual >= HORA_FIN_DIURNA:
                corte_dia = datetime.combine(fecha_actual + timedelta(days=1),
                                             HORA_INICIO_DIURNA)
            else:
                corte_dia = datetime.combine(fecha_actual, HORA_INICIO_DIURNA)
            fin_tramo = min(corte_dia, prox_dia, dt_fin)
            tipo = ('hora_extra_dominical_nocturna' if es_dominical
                    else 'hora_extra_nocturna')

        tramos.append({
            'fecha': fecha_actual,
            'tipo': tipo,
            'hora_inicio': cursor.time(),
            'hora_fin': fin_tramo.time() if fin_tramo != prox_dia else time(23, 59),
            # A 00:00 del día siguiente lo representamos como 23:59 del día
            # actual para no perder el fin del turno en el registro (el modelo
            # almacena hora_fin como time del propio día del tramo).
            'total_horas': _horas_entre(cursor, fin_tramo),
        })
        cursor = fin_tramo

    # Consolidar tramos consecutivos del mismo (fecha, tipo)
    consolidados = []
    for t in tramos:
        prev = consolidados[-1] if consolidados else None
        if prev and prev['fecha'] == t['fecha'] and prev['tipo'] == t['tipo']:
            prev['hora_fin'] = t['hora_fin']
            prev['total_horas'] += t['total_horas']
        else:
            consolidados.append(t)

    return consolidados


def dividir_por_medianoche(fecha: date, hora_inicio: time, hora_fin: time) -> list[dict]:
    """Para tipos NO-auto: si el rango cruza medianoche, lo parte en dos
    dicts {fecha, hora_inicio, hora_fin, total_horas} — uno por día. Si no
    cruza, retorna una sola entrada. No clasifica por jornada (respeta el
    tipo que eligió el usuario)."""
    dt_ini = datetime.combine(fecha, hora_inicio)
    dt_fin = datetime.combine(fecha, hora_fin)
    if dt_fin <= dt_ini:
        dt_fin += timedelta(days=1)

    if dt_fin <= dt_ini:
        raise ValueError("El rango de horas debe ser mayor a 0.")

    partes = []
    cursor = dt_ini
    while cursor < dt_fin:
        prox_dia = datetime.combine(cursor.date() + timedelta(days=1), time(0, 0))
        fin_tramo = min(prox_dia, dt_fin)
        partes.append({
            'fecha': cursor.date(),
            'hora_inicio': cursor.time(),
            'hora_fin': fin_tramo.time() if fin_tramo != prox_dia else time(23, 59),
            'total_horas': _horas_entre(cursor, fin_tramo),
        })
        cursor = fin_tramo
    return partes


def segmentar_recargo_nocturno(fecha: date, hora_inicio: time, hora_fin: time) -> tuple[list[dict], list[dict]]:
    """Recorta un rango de recargo_nocturno a la franja nocturna legal.

    Colombia: la jornada nocturna va de 19:00 a 06:00. Cualquier tramo fuera
    NO lleva recargo nocturno. Si el coordinador registra 18:00-23:59, solo
    19:00-23:59 se contabiliza; el tramo 18:00-19:00 se descarta.

    Además:
    - Si el rango cruza medianoche, se parte por día real.
    - Si el tramo cae en un día domingo/festivo, se reclasifica a
      `recargo_dominical`.

    Retorna (tramos_validos, tramos_descartados):
    - tramos_validos: [{fecha, tipo, hora_inicio, hora_fin, total_horas}]
      con tipo = 'recargo_nocturno' o 'recargo_dominical'. Vacío si el rango
      no intersecta con la franja nocturna.
    - tramos_descartados: [{fecha, hora_inicio, hora_fin, total_horas}] con
      las porciones diurnas que se ignoraron (para reportar al usuario).

    Raises ValueError si el rango dura 0.
    """
    dt_ini = datetime.combine(fecha, hora_inicio)
    dt_fin = datetime.combine(fecha, hora_fin)
    if dt_fin <= dt_ini:
        dt_fin += timedelta(days=1)
    if dt_fin <= dt_ini:
        raise ValueError("El rango de horas debe ser mayor a 0.")

    validos = []
    descartados = []
    cursor = dt_ini
    while cursor < dt_fin:
        fecha_actual = cursor.date()
        prox_dia = datetime.combine(fecha_actual + timedelta(days=1), time(0, 0))
        # Franjas del día actual
        # Ventana nocturna dentro del calendario diario: [00:00, 06:00] ∪ [19:00, 24:00]
        v_madrugada_ini = datetime.combine(fecha_actual, time(0, 0))
        v_madrugada_fin = datetime.combine(fecha_actual, HORA_INICIO_DIURNA)   # 06:00
        v_noche_ini = datetime.combine(fecha_actual, HORA_FIN_DIURNA)          # 19:00
        v_noche_fin = prox_dia                                                 # 24:00

        fin_tramo_dia = min(prox_dia, dt_fin)

        def _push_valido(dt_a, dt_b):
            if dt_b <= dt_a:
                return
            # Los tramos válidos por definición están en franja nocturna
            # (00-06 o 19-24), así que en día festivo son 'recargo_dominical_nocturno'.
            tipo = ('recargo_dominical_nocturno'
                    if _es_domingo_o_festivo(fecha_actual)
                    else 'recargo_nocturno')
            validos.append({
                'fecha': fecha_actual,
                'tipo': tipo,
                'hora_inicio': dt_a.time(),
                'hora_fin': dt_b.time() if dt_b != prox_dia else time(23, 59),
                'total_horas': _horas_entre(dt_a, dt_b),
            })

        def _push_descartado(dt_a, dt_b):
            if dt_b <= dt_a:
                return
            descartados.append({
                'fecha': fecha_actual,
                'hora_inicio': dt_a.time(),
                'hora_fin': dt_b.time(),
                'total_horas': _horas_entre(dt_a, dt_b),
            })

        # Interseccion con las 2 ventanas nocturnas del día actual
        # Ventana madrugada 00:00-06:00
        madrugada_a = max(cursor, v_madrugada_ini)
        madrugada_b = min(fin_tramo_dia, v_madrugada_fin)
        # Ventana noche 19:00-24:00
        noche_a = max(cursor, v_noche_ini)
        noche_b = min(fin_tramo_dia, v_noche_fin)

        # Recorrer el tramo [cursor, fin_tramo_dia] identificando qué cae y
        # qué se descarta, en orden temporal.
        walker = cursor
        # 1) porción antes de madrugada — imposible dentro del día si day 0:00
        # 2) madrugada [0:00-6:00] válida
        _push_valido(madrugada_a, madrugada_b)
        walker = max(walker, madrugada_b)
        # 3) porción diurna 6:00-19:00 descartada
        diurna_a = max(walker, v_madrugada_fin)
        diurna_b = min(fin_tramo_dia, v_noche_ini)
        _push_descartado(diurna_a, diurna_b)
        walker = max(walker, diurna_b)
        # 4) noche 19:00-24:00 válida
        _push_valido(noche_a, noche_b)

        cursor = fin_tramo_dia

    # Consolidar tramos válidos consecutivos del mismo (fecha, tipo)
    consolidados = []
    for t in validos:
        prev = consolidados[-1] if consolidados else None
        if prev and prev['fecha'] == t['fecha'] and prev['tipo'] == t['tipo']:
            prev['hora_fin'] = t['hora_fin']
            prev['total_horas'] += t['total_horas']
        else:
            consolidados.append(t)
    return consolidados, descartados
