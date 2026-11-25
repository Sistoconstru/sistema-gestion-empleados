"""Le avisa al conductor cuando Odoo le asigna un servicio o un viaje.

Los servicios se asignan en Odoo y Odoo no le avisa a SIGHU, así que SIGHU
pregunta cada pocos minutos (lo corre el scheduler) y compara contra lo que
ya avisó (`AvisoServicioAsignado`). Lo nuevo le llega al conductor como
notificación en SIGHU y como push al celular.

Un viaje es una sola salida, así que es un solo aviso con todas sus
paradas. Si después el coordinador le agrega una parada a un viaje ya
avisado, llega un aviso corto de esa parada.

Lo que no se avisa, y por qué:

- Lo que ya no está asignado (en curso o cerrado): ya lo sabe.
- Lo que Odoo no ha tocado en el último día: no es una asignación nueva,
  es lo que estaba cuando arrancó esto, o algo que se vio antes y de lo
  que no quedó registro. Se anota sin avisar.
- El conductor sin usuario en SIGHU: no hay a quién avisarle. Se anota
  para no volver a intentarlo cada pocos minutos.
"""
import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from apps.employees.models import Empleado
from apps.transporte.models import AvisoServicioAsignado
from apps.transporte.odoo_client import OdooTransporteError, listar_servicios
from apps.transporte.servicios import normalizar, resumen_de

logger = logging.getLogger(__name__)

# Una asignación que Odoo tocó hace más que esto ya no es noticia.
ANTIGUEDAD_MAXIMA = timedelta(days=1)


def _cuando(fecha):
    """"hoy a las 14:30", "mañana a las 07:00", "el 28/11 a las 06:00"."""
    if not fecha:
        return ''
    local = timezone.localtime(fecha)
    dias = (local.date() - timezone.localdate()).days
    hora = f'{local:%H:%M}'
    if dias == 0:
        return f'hoy a las {hora}'
    if dias == 1:
        return f'mañana a las {hora}'
    return f'el {local:%d/%m} a las {hora}'


def _plural(n, uno, varios):
    return f'{n} {uno if n == 1 else varios}'


class Command(BaseCommand):
    help = ('Avisa a los conductores de los servicios y viajes que Odoo '
            'les acaba de asignar.')

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Muestra qué se avisaría, sin avisar ni anotar nada')

    def handle(self, **options):
        dry_run = options['dry_run']
        try:
            crudos = listar_servicios(estado='asignado')
        except OdooTransporteError as e:
            # El scheduler vuelve a intentar en unos minutos; no hay nada
            # que perder porque lo que no se avisó sigue sin anotarse.
            logger.warning('Avisos de servicios: Odoo no contestó (%s)', e)
            return

        servicios = [s for s in (normalizar(c) for c in crudos)
                     if s and s['estado'] == 'asignado' and s['conductor_cedula']]
        if not servicios:
            return

        ya = set(AvisoServicioAsignado.objects
                 .filter(odoo_id__in=[s['odoo_id'] for s in servicios])
                 .values_list('odoo_id', 'cedula'))
        nuevos = [s for s in servicios
                  if (s['odoo_id'], s['conductor_cedula']) not in ya]
        if not nuevos:
            return

        cedulas = {s['conductor_cedula'] for s in nuevos}
        empleados = {e.numero_documento: e for e in
                     Empleado.objects.filter(numero_documento__in=cedulas)
                     .select_related('usuario')}

        # Un aviso por viaje y conductor; los servicios sueltos, uno cada uno.
        grupos = {}
        for s in nuevos:
            viaje = s['viaje']
            clave = (s['conductor_cedula'],
                     ('viaje', viaje['odoo_id']) if viaje else ('srv', s['odoo_id']))
            grupos.setdefault(clave, []).append(s)

        limite = timezone.now() - ANTIGUEDAD_MAXIMA
        avisados = 0
        for (cedula, _), lote in grupos.items():
            empleado = empleados.get(cedula)
            usuario = empleado.usuario if empleado else None
            recientes = any(s['actualizado'] and s['actualizado'] >= limite
                            for s in lote)
            avisar = bool(usuario) and recientes
            titulo, cuerpo = self._mensaje(lote, cedula)

            if not usuario:
                logger.warning('Servicio %s asignado a la cédula %s, que no '
                               'tiene usuario en SIGHU: no se le avisa.',
                               ', '.join(s['ref'] for s in lote), cedula)
            self.stdout.write(f'{"→" if avisar else "·"} {cedula}: {titulo} — {cuerpo}')
            if dry_run:
                continue

            with transaction.atomic():
                AvisoServicioAsignado.objects.bulk_create([
                    AvisoServicioAsignado(
                        odoo_id=s['odoo_id'], cedula=cedula, empleado=empleado,
                        viaje_odoo_id=s['viaje']['odoo_id'] if s['viaje'] else None,
                        ref=s['ref'][:60], avisado=avisar)
                    for s in lote], ignore_conflicts=True)
                if avisar:
                    self._notificar(usuario, titulo, cuerpo, lote)
            if avisar:
                avisados += 1

        if avisados:
            logger.info('Avisos de servicios asignados enviados: %s', avisados)

    def _mensaje(self, lote, cedula):
        """Título y cuerpo del aviso: servicio suelto, viaje nuevo o parada nueva."""
        s = lote[0]
        placa = f' — {s["placa"]}' if s['placa'] else ''
        urgente = 'URGENTE · ' if any(x['urgente'] for x in lote) else ''
        viaje = s['viaje']

        if not viaje:
            cuando = _cuando(s['fecha'])
            cuerpo = resumen_de(s) + (f'. Para {cuando}.' if cuando else '.')
            return f'{urgente}Nuevo servicio {s["ref"]}{placa}', cuerpo

        lote.sort(key=lambda x: (x['viaje']['parada'] or 999, x['odoo_id']))
        destinos = ', '.join(x['destino'] or x['ref'] for x in lote)
        ya_tenia = AvisoServicioAsignado.objects.filter(
            viaje_odoo_id=viaje['odoo_id'], cedula=cedula).exists()

        if ya_tenia:
            paradas = ', '.join(str(x['viaje']['parada']) for x in lote
                                if x['viaje']['parada'])
            titulo = (f'{urgente}'
                      f'{"Nueva parada" if len(lote) == 1 else "Nuevas paradas"} '
                      f'en el viaje {viaje["numero"]}')
            cuerpo = (f'{"Parada" if len(lote) == 1 else "Paradas"} {paradas}: '
                      f'{destinos}.' if paradas else f'{destinos}.')
            return titulo, cuerpo

        total = max(viaje['total_paradas'], len(lote))
        cuando = _cuando(viaje['salida'] or s['fecha'])
        # Paradas que Odoo cuenta pero que no vinieron (de otro vehículo, o
        # ya cerradas): se dicen, para que no parezca que faltan.
        otras = total - len(lote)
        cuerpo = (f'{_plural(total, "parada", "paradas")}: {destinos}'
                  f'{f" y {otras} más" if otras > 0 else ""}.')
        if cuando:
            cuerpo += f' Salida {cuando}.'
        return f'{urgente}Nuevo viaje {viaje["numero"]}{placa}', cuerpo

    def _notificar(self, usuario, titulo, cuerpo, lote):
        from apps.notifications.models import Notificacion, TipoNotificacion

        tipo, _ = TipoNotificacion.objects.get_or_create(
            codigo='servicio_asignado',
            defaults={
                'nombre': 'Servicio de transporte asignado',
                'plantilla_titulo': '{titulo}',
                'plantilla_mensaje': '{mensaje}',
                'enviar_push': True,
            },
        )
        url = reverse('transporte:servicios')
        Notificacion.objects.create(
            usuario=usuario,
            tipo_notificacion=tipo,
            titulo=titulo[:200],
            mensaje=cuerpo,
            datos_adicionales={'url': url,
                               'servicios_odoo': [s['odoo_id'] for s in lote]},
        )
        # El push sale cuando la fila ya quedó guardada: si la transacción
        # se cae, no le llega al celular un aviso que después no aparece.
        etiqueta = 'srv-' + '-'.join(str(s['odoo_id']) for s in lote)[:60]

        def enviar():
            try:
                from apps.notifications.push_utils import send_push
                send_push(usuario, titulo, cuerpo, url=url, tag=etiqueta,
                          vibrate=[200, 100, 200])
            except Exception as e:
                logger.warning('Push de servicio asignado no enviado: %s', e)

        transaction.on_commit(enviar)
