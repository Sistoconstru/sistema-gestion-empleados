"""Reescribe acción y descripción de registros de auditoría viejos.

Los registros anteriores al catálogo de apps/core/auditoria.py dicen "crear"
casi siempre. Con la URL y los datos guardados se reinterpretan con la misma
lógica que los nuevos. No toca la URL, los datos enviados, la IP, el usuario
ni la fecha: solo `accion`, `modelo` y `descripcion`.

Limitaciones de los registros viejos:
- El login no guardaba si funcionó. Se deduce: si el mismo usuario que se
  escribió en el formulario tiene un movimiento desde la misma IP en los 10
  minutos siguientes, entró; si no, queda como "intento (resultado no
  registrado)". No se le asigna nunca a otra persona.
- Si el objeto ya no existe (p. ej. un anexo borrado), la frase dice
  "un registro" en vez de su nombre.

    python manage.py reprocesar_auditoria              # muestra ejemplos, no guarda
    python manage.py reprocesar_auditoria --apply
"""
from collections import Counter
from datetime import timedelta

from django.core.management.base import BaseCommand

from apps.core import auditoria
from apps.core.models import LogActividad

LOTE = 1000


class Command(BaseCommand):
    help = 'Reinterpreta acción y descripción de registros de auditoría existentes.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Guardar los cambios.')
        parser.add_argument('--ejemplos', type=int, default=25)

    def handle(self, *args, **opts):
        # Lotes cortos y no un cursor abierto todo el recorrido: el proxy
        # público de Railway corta las conexiones largas. Con --apply cada lote
        # se guarda al terminarlo, así que un corte no deja nada a medias.
        ids = list(LogActividad.objects.order_by('fecha_accion').values_list('pk', flat=True))
        self.cache_rutas = {}
        resumen = Counter()
        ejemplos = actualizados = 0

        for inicio in range(0, len(ids), LOTE):
            lote = LogActividad.objects.filter(pk__in=ids[inicio:inicio + LOTE]).select_related('usuario')
            cambiados = []
            for log in lote:
                nuevo = self._interpretar(log)
                if not nuevo:
                    continue
                accion, modulo, descripcion = nuevo
                if (log.accion, log.modelo, log.descripcion) == (accion, modulo, descripcion):
                    continue
                resumen[(log.accion, accion)] += 1
                if ejemplos < opts['ejemplos'] and log.accion != accion:
                    ejemplos += 1
                    self.stdout.write(f'  [{log.accion} -> {accion}] {descripcion}')
                log.accion, log.modelo, log.descripcion = accion, modulo, descripcion
                cambiados.append(log)
            if opts['apply'] and cambiados:
                LogActividad.objects.bulk_update(cambiados, ['accion', 'modelo', 'descripcion'])
            actualizados += len(cambiados)

        self.stdout.write(f'\nRegistros: {len(ids)} | a actualizar: {actualizados}')
        for (antes, despues), n in resumen.most_common(30):
            self.stdout.write(f'  {n:6}  {antes} -> {despues}')
        if opts['apply']:
            self.stdout.write(self.style.SUCCESS(f'Actualizados {actualizados} registros.'))
        else:
            self.stdout.write(self.style.WARNING('Sin --apply: no se guardó nada.'))

    def _interpretar(self, log):
        contexto = self.cache_rutas.get(log.url_accedida)
        if contexto is None:
            contexto = auditoria.preparar_ruta(log.url_accedida)
            self.cache_rutas[log.url_accedida] = contexto

        siguiente = None
        status = None
        if contexto.get('vista') in ('authentication:login', 'admin:login'):
            siguiente = self._siguiente_del_mismo_usuario(log)
            status = 302 if siguiente else None
        try:
            accion, modulo, texto = auditoria.interpretar(contexto, log.cambios_realizados, status)
        except Exception as e:
            self.stderr.write(f'{log.pk}: {e}')
            return None

        if log.usuario:
            quien = log.usuario.get_full_name() or log.usuario.username
        elif siguiente:
            quien = siguiente.usuario.get_full_name() or siguiente.usuario.username
        elif modulo == 'odoo':
            quien = 'Odoo'
        else:
            quien = 'Alguien sin sesión'
        return accion, (modulo or '')[:50], f'{quien} {texto}'

    def _siguiente_del_mismo_usuario(self, log):
        """Movimiento del MISMO usuario que escribió en el formulario, desde la
        misma IP y en los 10 minutos siguientes. Solo la IP no basta: la de la
        oficina la comparten casi todos y se le atribuiría a otra persona."""
        username = auditoria._valor(log.cambios_realizados, 'username')
        if not username:
            return None
        return (
            LogActividad.objects.filter(
                ip_address=log.ip_address, usuario__username__iexact=username,
                fecha_accion__gt=log.fecha_accion,
                fecha_accion__lte=log.fecha_accion + timedelta(minutes=10),
            ).select_related('usuario').order_by('fecha_accion').first()
        )
