"""
Comando para limpiar automáticamente publicaciones expiradas del sistema.

Política de expiración:
- Publicaciones con imagen: 15 días (se eliminan completamente)
- Publicaciones rápidas: 6 meses (se eliminan completamente)
- Anuncios: Manual basado en fecha_fin (se eliminan cuando llega la fecha)

Ejecutar con: python manage.py limpiar_publicaciones_expiradas
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from apps.employees.models import Publicacion
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Elimina automáticamente publicaciones expiradas del sistema'

    def handle(self, *args, **options):
        ahora = timezone.now()

        # Obtener publicaciones expiradas
        publicaciones_expiradas = Publicacion.objects.filter(
            fecha_eliminacion_automatica__lte=ahora
        ).exclude(fecha_eliminacion_automatica__isnull=True)

        # También obtener anuncios importantes expirados (fecha_fin pasada)
        anuncios_expirados = Publicacion.objects.filter(
            es_anuncio=True,
            es_importante=True,
            fecha_fin__lte=ahora
        )

        # Combinar ambos querysets
        todas_expiradas = (publicaciones_expiradas | anuncios_expirados).distinct()

        if not todas_expiradas.exists():
            self.stdout.write(self.style.SUCCESS('No hay publicaciones expiradas para limpiar'))
            logger.info("[CLEANUP] No hay publicaciones expiradas para limpiar")
            return

        # Agrupar por tipo para logging detallado
        rapidas = todas_expiradas.filter(es_rapida=True).count()
        con_imagen = todas_expiradas.filter(imagen__isnull=False, es_rapida=False, es_anuncio=False).count()
        anuncios = todas_expiradas.filter(es_anuncio=True).count()

        total = todas_expiradas.count()

        # Limpiar notificaciones asociadas a anuncios expirados
        from apps.notifications.models import Notificacion
        notificaciones_eliminadas = 0

        for pub in todas_expiradas.filter(es_anuncio=True):
            notificaciones = Notificacion.objects.filter(
                datos_adicionales__publicacion_id=str(pub.id)
            )
            count = notificaciones.count()
            if count > 0:
                notificaciones.delete()
                notificaciones_eliminadas += count
                logger.info(f"[CLEANUP] Eliminadas {count} notificaciones del anuncio ID {pub.id}")

        if notificaciones_eliminadas > 0:
            self.stdout.write(self.style.SUCCESS(f'✓ Eliminadas {notificaciones_eliminadas} notificaciones de anuncios expirados'))
            logger.info(f"[CLEANUP] Total notificaciones eliminadas: {notificaciones_eliminadas}")

        # Eliminar archivos de imagen si existen
        for pub in todas_expiradas:
            if pub.imagen:
                try:
                    pub.imagen.delete(save=False)
                    logger.info(f"[CLEANUP] Imagen eliminada: {pub.imagen.name}")
                except Exception as e:
                    logger.error(f"[CLEANUP] Error al eliminar imagen {pub.imagen.name}: {e}")

            if pub.imagen_renderizada:
                try:
                    pub.imagen_renderizada.delete(save=False)
                    logger.info(f"[CLEANUP] Imagen renderizada eliminada: {pub.imagen_renderizada.name}")
                except Exception as e:
                    logger.error(f"[CLEANUP] Error al eliminar imagen renderizada {pub.imagen_renderizada.name}: {e}")

        # Eliminar publicaciones de la BD (esto también disparará el signal post_delete)
        todas_expiradas.delete()

        # Mensaje de éxito
        mensaje = (
            f'✓ Limpieza completada:\n'
            f'  - Publicaciones rápidas eliminadas: {rapidas}\n'
            f'  - Publicaciones con imagen eliminadas: {con_imagen}\n'
            f'  - Anuncios eliminados: {anuncios}\n'
            f'  - Notificaciones eliminadas: {notificaciones_eliminadas}\n'
            f'  - Total publicaciones: {total}'
        )

        self.stdout.write(self.style.SUCCESS(mensaje))
        logger.info(
            f"[CLEANUP] Limpieza completada. Rápidas: {rapidas}, Con imagen: {con_imagen}, "
            f"Anuncios: {anuncios}, Notificaciones: {notificaciones_eliminadas}, Total: {total}"
        )
