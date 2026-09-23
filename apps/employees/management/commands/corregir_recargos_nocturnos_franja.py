"""Corrige recargos nocturnos históricos con horario fuera de la franja legal.

Colombia: la jornada nocturna que da derecho a recargo va de 19:00 a 06:00.
Cualquier novedad `recargo_nocturno` con `hora_inicio < 19:00` o `hora_fin > 06:00`
(entre 06:00 y 19:00) está sobre-atribuyendo horas.

El comando recorta cada registro a la ventana [19:00, 06:00] y ajusta
`total_horas`. Si el tramo cae en un día domingo/festivo, se reclasifica a
`recargo_dominical`. Si el rango cruza medianoche, se genera un segundo
registro con la fecha del día siguiente (mismo tipo o reclasificado).

Modo:
- Sin flags → dry-run (default).
- --apply → aplica cambios en una transacción atómica.

Idempotente: marca los ajustados con `[Recortado a franja nocturna]` en
observaciones y los excluye en corridas posteriores.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.employees.models import NovedadNomina
from apps.employees.utils.jornadas import segmentar_recargo_nocturno


MARCA = '[Recortado a franja nocturna]'


class Command(BaseCommand):
    help = 'Recorta recargos_nocturnos históricos con horario fuera de 19:00-06:00.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true',
                            help='Aplica los cambios. Sin este flag corre en modo dry-run.')
        parser.add_argument('--limit', type=int, default=None,
                            help='Procesar solo N novedades (para pruebas graduales).')

    def _necesita_recorte(self, nov):
        """True si el rango tiene parte diurna (fuera de 19:00-06:00)."""
        if nov.hora_inicio is None or nov.hora_fin is None:
            return False
        try:
            tramos, descartados = segmentar_recargo_nocturno(
                nov.fecha, nov.hora_inicio, nov.hora_fin,
            )
        except ValueError:
            return False
        return bool(descartados)

    def handle(self, *args, **options):
        apply = options['apply']
        limit = options['limit']

        qs = NovedadNomina.objects.filter(
            tipo='recargo_nocturno',
            hora_inicio__isnull=False, hora_fin__isnull=False,
        ).exclude(observaciones__contains=MARCA).order_by('fecha', 'pk')

        # Filtrar los que necesitan recorte (imposible con SQL puro por la
        # lógica de franjas + días festivos; se hace en memoria)
        candidatas = [n for n in qs if self._necesita_recorte(n)]
        total = len(candidatas)
        self.stdout.write(f'Candidatas a recortar: {total}')

        if limit:
            candidatas = candidatas[:limit]
            self.stdout.write(f'Procesando solo las primeras {limit}.')

        preview = []
        cambios_dominical = 0
        registros_extras = 0
        for nov in candidatas:
            tramos, descartados = segmentar_recargo_nocturno(
                nov.fecha, nov.hora_inicio, nov.hora_fin,
            )
            preview.append({
                'nov': nov, 'tramos': tramos, 'descartados': descartados,
            })
            if any(t['tipo'] == 'recargo_dominical' for t in tramos):
                cambios_dominical += 1
            registros_extras += max(0, len(tramos) - 1)

        self.stdout.write('')
        self.stdout.write(f'--- Resumen ---')
        self.stdout.write(f'Recortes a aplicar:              {total}')
        self.stdout.write(f'Reclasificaciones a dominical:   {cambios_dominical}')
        self.stdout.write(f'Registros nuevos a crear:        {registros_extras}')

        # Muestra 5
        self.stdout.write('\n--- Muestra (primeras 5) ---')
        for p in preview[:5]:
            n = p['nov']
            self.stdout.write(
                f'pk={n.pk}  {n.fecha}  {n.hora_inicio}-{n.hora_fin}  '
                f'{n.total_horas}h  [{n.tipo}]  emp={n.empleado.nombre_completo}'
            )
            for t in p['tramos']:
                self.stdout.write(
                    f'    → {t["fecha"]} {t["hora_inicio"]}-{t["hora_fin"]} '
                    f'{t["total_horas"]}h [{t["tipo"]}]'
                )
            for d in p['descartados']:
                self.stdout.write(
                    f'    ✗ descarta {d["fecha"]} {d["hora_inicio"]}-{d["hora_fin"]} '
                    f'{d["total_horas"]}h'
                )

        if not apply:
            self.stdout.write(self.style.WARNING(
                '\n*** DRY-RUN — no se modificó nada. Corre con --apply. ***'
            ))
            return

        self.stdout.write('\nAplicando cambios...')
        aplicados = 0
        with transaction.atomic():
            for p in preview:
                nov = p['nov']
                tramos = p['tramos']
                descartados = p['descartados']

                # Descripción del recorte para observaciones
                desc = f' {MARCA} original {nov.hora_inicio.strftime("%H:%M")}-{nov.hora_fin.strftime("%H:%M")}'
                for d in descartados:
                    desc += (
                        f'; descarta {d["hora_inicio"].strftime("%H:%M")}-'
                        f'{d["hora_fin"].strftime("%H:%M")} ({d["total_horas"]}h)'
                    )

                obs_original = nov.observaciones or ''
                primer = tramos[0]
                nov.fecha = primer['fecha']
                nov.tipo = primer['tipo']
                nov.hora_inicio = primer['hora_inicio']
                nov.hora_fin = primer['hora_fin']
                nov.total_horas = primer['total_horas']
                nov.observaciones = (obs_original + desc).strip()
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
                        observaciones=obs_original + desc,
                        registrado_por=nov.registrado_por,
                        creado_por=nov.creado_por,
                        estado_aprobacion=nov.estado_aprobacion,
                        aprobado_por_rrhh=nov.aprobado_por_rrhh,
                        fecha_aprobacion=nov.fecha_aprobacion,
                    )
                aplicados += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Aplicado. Recortadas: {aplicados}. '
            f'Registros nuevos creados: {registros_extras}.'
        ))
