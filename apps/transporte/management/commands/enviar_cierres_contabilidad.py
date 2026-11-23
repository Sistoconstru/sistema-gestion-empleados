"""Manda a Odoo los cierres de gastos que todavía no llegaron.

El envío se intenta primero en el momento de cerrar la cuenta, con el jefe
mirando la pantalla. Esto es la red: lo que no llegó porque Odoo estaba
caído, o porque el endpoint todavía no existe, se pone al día acá sin que
nadie tenga que acordarse.

Los que Odoo rechazó a propósito quedan fuera. Repetir un rechazo es
gastar llamadas para que conteste lo mismo cada dos horas; se resuelven a
mano con el botón "reenviar" del detalle del cierre, una vez arreglado lo
que allá los hizo fallar.

    --dry-run       no manda nada; dice qué mandaría
    --payload       imprime el JSON tal como viaja (para el dev de Odoo)
    --cierre <id>   solo ese, aunque ya esté sincronizado o rechazado
"""
import json

from django.core.management.base import BaseCommand

from apps.transporte import contabilidad
from apps.transporte.models import CierreGastos


class Command(BaseCommand):
    help = 'Envía a la contabilidad de Odoo los cierres de gastos pendientes.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Muestra qué se mandaría, sin mandar nada')
        parser.add_argument(
            '--payload', action='store_true',
            help='Imprime el JSON del envío. Implica --dry-run.')
        parser.add_argument(
            '--cierre', metavar='UUID',
            help='Un cierre en particular, sincronizado o no')

    def handle(self, **options):
        solo_mirar = options['dry_run'] or options['payload']

        if options['cierre']:
            cierres = list(CierreGastos.objects.filter(
                pk=options['cierre']).select_related(
                    'conductor', 'vehiculo', 'cerrado_por', 'anulado_por'))
            if not cierres:
                self.stdout.write(self.style.ERROR('No existe ese cierre.'))
                return
        else:
            cierres = list(contabilidad.pendientes().order_by('fecha_cierre'))

        if not cierres:
            self.stdout.write('No hay cierres pendientes de enviar a Odoo.')
            return

        self.stdout.write(f'Cierres por enviar: {len(cierres)}\n')
        enviados = en_cola = rechazados = 0
        ultimo = ''

        for cierre in cierres:
            etiqueta = (f'{cierre.get_ambito_display().lower()} '
                        f'{cierre.sujeto} — {cierre.cantidad} gasto(s), '
                        f'${cierre.total_costo:,.0f}')

            # Un cierre anulado no se reenvía: lo que le falta es el aviso
            # de que dejó de valer. Mandarlo de nuevo lo contabilizaría.
            anulacion = not cierre.esta_activo

            if options['payload']:
                datos = (contabilidad.payload_anulacion(cierre) if anulacion
                         else contabilidad.payload_cierre(cierre))
                destino = ('webhook/cierre_gastos_anulado' if anulacion
                           else 'webhook/cierre_gastos')
                self.stdout.write(self.style.MIGRATE_HEADING(
                    f'\nPOST /sighu_sync/{destino}  ({etiqueta})'))
                self.stdout.write(json.dumps(datos, indent=2,
                                             ensure_ascii=False))
                continue

            if solo_mirar:
                accion = 'avisaría la anulación de' if anulacion else 'enviaría'
                self.stdout.write(f'  {accion}: {etiqueta}')
                continue

            enviar = (contabilidad.enviar_anulacion if anulacion
                      else contabilidad.enviar)
            resultado, detalle = enviar(cierre)

            if resultado == contabilidad.ENVIADO:
                enviados += 1
                self.stdout.write(
                    f'  enviado: {etiqueta}'
                    + (f' → {detalle}' if detalle else ''))
            elif resultado == contabilidad.RECHAZADO:
                rechazados += 1
                self.stdout.write(self.style.ERROR(
                    f'  rechazado por Odoo: {etiqueta} — {detalle[:140]}'))
            else:
                en_cola += 1
                ultimo = detalle

        if solo_mirar:
            self.stdout.write(self.style.WARNING(
                f'\nDRY RUN sobre {len(cierres)} cierre(s). No se mandó nada.'))
            return

        if en_cola:
            # Un solo renglón: cuando el endpoint aún no existe fallan todos
            # por lo mismo y repetirlo solo hace ruido.
            self.stdout.write(self.style.WARNING(
                f'\nEnviados: {enviados} | en cola: {en_cola} '
                f'| rechazados: {rechazados}\n  {ultimo[:160]}'))
        else:
            estilo = self.style.ERROR if rechazados else self.style.SUCCESS
            self.stdout.write(estilo(
                f'\nEnviados: {enviados} | rechazados: {rechazados}'))

        if rechazados:
            self.stdout.write(
                'Los rechazados no se reintentan solos: se revisan en el '
                'detalle del cierre y se reenvían desde ahí.')
