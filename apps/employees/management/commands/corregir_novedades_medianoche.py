"""Corrige novedades registradas antes del fix de cruce de medianoche.

Las novedades afectadas quedaron con `hora_fin <= hora_inicio` en un solo
registro (ej: 20:00-06:00 en el día del inicio). Este comando las parte en
dos filas — una por día — reclasificando el tipo si el día siguiente es
festivo/domingo (opción B acordada con el usuario).

Modo:
- Sin flags → dry-run: muestra qué haría.
- --apply → aplica los cambios en una sola transacción.

Preserva empleado, motivo, observaciones, registrado_por, creado_por,
estado_aprobacion, aprobado_por_rrhh, fecha_aprobacion.
"""
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F

from apps.employees.models import NovedadNomina
from apps.employees.utils.jornadas import (
    segmentar_hora_extra, _es_domingo_o_festivo,
)


DEC2 = Decimal('0.01')


def _horas(dt_ini, dt_fin):
    seg = (dt_fin - dt_ini).total_seconds()
    return (Decimal(seg) / Decimal('3600')).quantize(DEC2)


def _construir_tramos(nov):
    """Devuelve lista de dicts {fecha, tipo, hora_inicio, hora_fin, total_horas}
    para el rango original de la novedad, ya reclasificados.

    Para tipos hora_extra_*: reutiliza segmentar_hora_extra() (reclasifica).
    Para recargo_nocturno: cambia a recargo_dominical si día siguiente es festivo.
    Para el resto (recargo_dominical, vigilancia): parte por medianoche,
    preservando el tipo.
    """
    fecha_ini = nov.fecha
    fecha_fin = fecha_ini + timedelta(days=1)
    dt_ini = datetime.combine(fecha_ini, nov.hora_inicio)
    dt_medianoche = datetime.combine(fecha_fin, time(0, 0))
    dt_fin = datetime.combine(fecha_fin, nov.hora_fin)

    horas_previa = _horas(dt_ini, dt_medianoche)
    horas_siguiente = _horas(dt_medianoche, dt_fin)

    if nov.tipo.startswith('hora_extra_'):
        # segmentar_hora_extra reclasifica diurna/nocturna/dominical y devuelve
        # tramos con fecha real.
        return segmentar_hora_extra(fecha_ini, nov.hora_inicio, nov.hora_fin)

    if nov.tipo == 'recargo_nocturno':
        tipo_siguiente = (
            'recargo_dominical' if _es_domingo_o_festivo(fecha_fin)
            else 'recargo_nocturno'
        )
        return [
            {'fecha': fecha_ini, 'tipo': nov.tipo,
             'hora_inicio': nov.hora_inicio, 'hora_fin': time(23, 59),
             'total_horas': horas_previa},
            {'fecha': fecha_fin, 'tipo': tipo_siguiente,
             'hora_inicio': time(0, 0), 'hora_fin': nov.hora_fin,
             'total_horas': horas_siguiente},
        ]

    # Otros tipos: preservar tipo, solo partir por medianoche.
    return [
        {'fecha': fecha_ini, 'tipo': nov.tipo,
         'hora_inicio': nov.hora_inicio, 'hora_fin': time(23, 59),
         'total_horas': horas_previa},
        {'fecha': fecha_fin, 'tipo': nov.tipo,
         'hora_inicio': time(0, 0), 'hora_fin': nov.hora_fin,
         'total_horas': horas_siguiente},
    ]


def _aplicar_correccion(nov, tramos):
    """Actualiza `nov` con el primer tramo y crea los demás. Marca en
    observaciones la corrección para trazabilidad."""
    marca = ' [Corregido cruce medianoche]'
    obs_original = nov.observaciones or ''

    primer = tramos[0]
    nov.fecha = primer['fecha']
    nov.tipo = primer['tipo']
    nov.hora_inicio = primer['hora_inicio']
    nov.hora_fin = primer['hora_fin']
    nov.total_horas = primer['total_horas']
    if marca not in obs_original:
        nov.observaciones = (obs_original + marca).strip()
    nov.save()

    for tr in tramos[1:]:
        NovedadNomina.objects.create(
            empleado=nov.empleado,
            fecha=tr['fecha'],
            tipo=tr['tipo'],
            hora_inicio=tr['hora_inicio'],
            hora_fin=tr['hora_fin'],
            total_horas=tr['total_horas'],
            motivo=nov.motivo,
            observaciones=obs_original + marca,
            registrado_por=nov.registrado_por,
            creado_por=nov.creado_por,
            estado_aprobacion=nov.estado_aprobacion,
            aprobado_por_rrhh=nov.aprobado_por_rrhh,
            fecha_aprobacion=nov.fecha_aprobacion,
        )


class Command(BaseCommand):
    help = 'Parte las novedades con hora_fin <= hora_inicio en 2+ tramos por día.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply', action='store_true',
            help='Aplica los cambios. Sin este flag corre en modo dry-run.',
        )
        parser.add_argument(
            '--limit', type=int, default=None,
            help='Procesar solo N novedades (útil para pruebas graduales).',
        )

    def handle(self, *args, **options):
        apply = options['apply']
        limit = options['limit']

        qs = NovedadNomina.objects.filter(
            hora_inicio__isnull=False, hora_fin__isnull=False,
            hora_fin__lte=F('hora_inicio'),
        ).order_by('fecha', 'pk')
        # Excluir las ya corregidas (marca en observaciones)
        qs = qs.exclude(observaciones__contains='Corregido cruce medianoche')

        total = qs.count()
        self.stdout.write(f'Candidatas a corregir: {total}')

        if limit:
            qs = qs[:limit]
            self.stdout.write(f'Procesando solo las primeras {limit}.')

        procesadas = 0
        tramos_generados = 0
        cambios_tipo = 0
        errores = []
        preview = []

        for nov in qs:
            try:
                tramos = _construir_tramos(nov)
            except Exception as e:
                errores.append((nov.pk, str(e)))
                continue

            hubo_cambio_tipo = any(t['tipo'] != nov.tipo for t in tramos)
            if hubo_cambio_tipo:
                cambios_tipo += 1

            preview.append({
                'pk': nov.pk, 'emp': nov.empleado.nombre_completo,
                'fecha_orig': nov.fecha,
                'rango_orig': f'{nov.hora_inicio}-{nov.hora_fin}',
                'horas_orig': str(nov.total_horas),
                'tipo_orig': nov.tipo,
                'tramos': tramos,
            })
            procesadas += 1
            tramos_generados += len(tramos)

        self.stdout.write('')
        self.stdout.write(f'--- Resumen ---')
        self.stdout.write(f'Procesables: {procesadas}')
        self.stdout.write(f'Tramos que se generarían: {tramos_generados}')
        self.stdout.write(f'  → registros nuevos a crear: {tramos_generados - procesadas}')
        self.stdout.write(f'Cambios de tipo detectados: {cambios_tipo}')
        if errores:
            self.stdout.write(f'Errores: {len(errores)}')
            for pk, msg in errores[:5]:
                self.stdout.write(f'  pk={pk}: {msg}')

        # Mostrar muestra
        self.stdout.write('\n--- Muestra (primeras 5) ---')
        for p in preview[:5]:
            self.stdout.write(
                f'pk={p["pk"]} {p["emp"]} — original: {p["fecha_orig"]} '
                f'{p["rango_orig"]} {p["horas_orig"]}h [{p["tipo_orig"]}]'
            )
            for tr in p['tramos']:
                self.stdout.write(
                    f'    → {tr["fecha"]} {tr["hora_inicio"]}-{tr["hora_fin"]} '
                    f'{tr["total_horas"]}h [{tr["tipo"]}]'
                )

        if not apply:
            self.stdout.write(self.style.WARNING(
                '\n*** DRY-RUN — no se modificó nada. Corre con --apply para ejecutar. ***'
            ))
            return

        # APPLY
        self.stdout.write('\nAplicando cambios...')
        aplicadas = 0
        with transaction.atomic():
            for nov in qs:
                try:
                    tramos = _construir_tramos(nov)
                    _aplicar_correccion(nov, tramos)
                    aplicadas += 1
                except Exception as e:
                    errores.append((nov.pk, str(e)))
                    raise  # rollback total si algo falla

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Aplicado. Novedades corregidas: {aplicadas}. '
            f'Registros totales resultantes: {tramos_generados}.'
        ))
