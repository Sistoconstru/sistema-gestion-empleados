"""Reclasifica novedades dominicales que caen en franja nocturna.

Contexto: la migración 0047 renombró:
- 'hora_extra_dominical'  → 'hora_extra_dominical_diurna'
- 'recargo_dominical'     → 'recargo_dominical_diurno'

Ese rename es masivo pero incorrecto para los tramos que caen en franja
nocturna (00:00-06:00 y 19:00-24:00), que legalmente deben ser
'*_nocturna/nocturno' (recargo 150% vs 100%).

Este comando revisa las novedades ya renombradas a `_diurna/_diurno`,
detecta cuáles tienen hora_inicio o hora_fin en franja nocturna, y las
parte donde corresponda:
- Tramo diurno (06-19) queda como `_diurna/_diurno`.
- Tramo nocturno (00-06 o 19-24) pasa a `_nocturna/_nocturno`.

Idempotente: marca en observaciones `[Reclasificado dominical nocturno]`.
Modo dry-run por defecto; --apply ejecuta.
"""
from collections import defaultdict
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.employees.models import NovedadNomina
from apps.employees.utils.jornadas import (
    HORA_INICIO_DIURNA, HORA_FIN_DIURNA, _horas_entre,
)


MARCA = '[Reclasificado dominical nocturno]'

# Mapa tipo diurno → tipo nocturno correspondiente
NOCTURNO_PAIRS = {
    'hora_extra_dominical_diurna': 'hora_extra_dominical_nocturna',
    'recargo_dominical_diurno':    'recargo_dominical_nocturno',
}


def _partir(nov):
    """Devuelve lista de tramos {fecha, tipo, hora_inicio, hora_fin,
    total_horas} basado en el rango horario del registro. Si el rango
    entero es diurno, retorna 1 tramo idéntico al original."""
    if nov.hora_inicio is None or nov.hora_fin is None:
        return None  # sin rango, no se puede saber

    dt_ini = datetime.combine(nov.fecha, nov.hora_inicio)
    dt_fin = datetime.combine(nov.fecha, nov.hora_fin)
    if dt_fin <= dt_ini:
        dt_fin += timedelta(days=1)

    tipo_diurno = nov.tipo
    tipo_nocturno = NOCTURNO_PAIRS[nov.tipo]

    tramos = []
    cursor = dt_ini
    while cursor < dt_fin:
        fecha_actual = cursor.date()
        prox_dia = datetime.combine(fecha_actual + timedelta(days=1), time(0, 0))
        hora_actual = cursor.time()

        if HORA_INICIO_DIURNA <= hora_actual < HORA_FIN_DIURNA:
            corte = datetime.combine(fecha_actual, HORA_FIN_DIURNA)
            fin_tramo = min(corte, prox_dia, dt_fin)
            tipo = tipo_diurno
        else:
            if hora_actual >= HORA_FIN_DIURNA:
                corte = datetime.combine(fecha_actual + timedelta(days=1),
                                         HORA_INICIO_DIURNA)
            else:
                corte = datetime.combine(fecha_actual, HORA_INICIO_DIURNA)
            fin_tramo = min(corte, prox_dia, dt_fin)
            tipo = tipo_nocturno

        tramos.append({
            'fecha': fecha_actual,
            'tipo': tipo,
            'hora_inicio': cursor.time(),
            'hora_fin': fin_tramo.time() if fin_tramo != prox_dia else time(23, 59),
            'total_horas': _horas_entre(cursor, fin_tramo),
        })
        cursor = fin_tramo

    # Consolidar tramos consecutivos (fecha, tipo)
    consolidados = []
    for t in tramos:
        prev = consolidados[-1] if consolidados else None
        if prev and prev['fecha'] == t['fecha'] and prev['tipo'] == t['tipo']:
            prev['hora_fin'] = t['hora_fin']
            prev['total_horas'] += t['total_horas']
        else:
            consolidados.append(t)
    return consolidados


class Command(BaseCommand):
    help = 'Reclasifica dominicales que caen en franja nocturna (post migración 0047).'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true')
        parser.add_argument('--limit', type=int, default=None)

    def handle(self, *args, **options):
        apply = options['apply']
        limit = options['limit']

        qs = NovedadNomina.objects.filter(
            tipo__in=list(NOCTURNO_PAIRS),
            hora_inicio__isnull=False, hora_fin__isnull=False,
        ).exclude(observaciones__contains=MARCA).order_by('fecha', 'pk')

        # Filtrar solo las que necesitan partición (tienen algún tramo nocturno)
        candidatas = []
        for n in qs:
            tramos = _partir(n)
            if not tramos:
                continue
            tipos_generados = {t['tipo'] for t in tramos}
            if any(t.endswith('_nocturna') or t.endswith('_nocturno') for t in tipos_generados):
                candidatas.append((n, tramos))
        total = len(candidatas)
        self.stdout.write(f'Candidatas a reclasificar: {total}')

        if limit:
            candidatas = candidatas[:limit]
            self.stdout.write(f'Procesando las primeras {limit}.')

        registros_extras = sum(max(0, len(t) - 1) for _, t in candidatas)
        self.stdout.write('')
        self.stdout.write('--- Resumen ---')
        self.stdout.write(f'Reclasificaciones a aplicar:    {total}')
        self.stdout.write(f'Registros nuevos a crear:       {registros_extras}')

        # Muestra 5
        self.stdout.write('\n--- Muestra (primeras 5) ---')
        for n, tramos in candidatas[:5]:
            self.stdout.write(
                f'pk={n.pk}  {n.fecha}  {n.hora_inicio}-{n.hora_fin}  '
                f'{n.total_horas}h  [{n.tipo}]  emp={n.empleado.nombre_completo}'
            )
            for t in tramos:
                self.stdout.write(
                    f'    → {t["fecha"]} {t["hora_inicio"]}-{t["hora_fin"]} '
                    f'{t["total_horas"]}h [{t["tipo"]}]'
                )

        if not apply:
            self.stdout.write(self.style.WARNING(
                '\n*** DRY-RUN — sin cambios. Corre con --apply. ***'
            ))
            return

        self.stdout.write('\nAplicando cambios...')
        aplicados = 0
        with transaction.atomic():
            for n, tramos in candidatas:
                obs_original = n.observaciones or ''
                marca_final = f' {MARCA}'
                primer = tramos[0]
                n.fecha = primer['fecha']
                n.tipo = primer['tipo']
                n.hora_inicio = primer['hora_inicio']
                n.hora_fin = primer['hora_fin']
                n.total_horas = primer['total_horas']
                n.observaciones = (obs_original + marca_final).strip()
                n.save()

                for tr in tramos[1:]:
                    NovedadNomina.objects.create(
                        empleado=n.empleado,
                        fecha=tr['fecha'],
                        tipo=tr['tipo'],
                        hora_inicio=tr['hora_inicio'],
                        hora_fin=tr['hora_fin'],
                        total_horas=tr['total_horas'],
                        motivo=n.motivo,
                        observaciones=obs_original + marca_final,
                        registrado_por=n.registrado_por,
                        creado_por=n.creado_por,
                        estado_aprobacion=n.estado_aprobacion,
                        aprobado_por_rrhh=n.aprobado_por_rrhh,
                        fecha_aprobacion=n.fecha_aprobacion,
                    )
                aplicados += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Aplicado. Reclasificadas: {aplicados}. '
            f'Registros nuevos: {registros_extras}.'
        ))
