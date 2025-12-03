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

        if not publicaciones_expiradas.exists():
            self.stdout.write(self.style.SUCCESS('No hay publicaciones expiradas para limpiar'))
            logger.info("[CLEANUP] No hay publicaciones expiradas para limpiar")
            return

        # Agrupar por tipo para logging detallado
        rapidas = publicaciones_expiradas.filter(es_rapida=True).count()
        con_imagen = publicaciones_expiradas.filter(imagen__isnull=False, es_rapida=False).count()
        anuncios = publicaciones_expiradas.filter(es_anuncio=True).count()

        total = publicaciones_expiradas.count()

        # Eliminar archivos de imagen si existen
        for pub in publicaciones_expiradas:
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

        # Eliminar publicaciones de la BD
        publicaciones_expiradas.delete()

        # Mensaje de éxito
        mensaje = (
            f'✓ Limpieza completada:\n'
            f'  - Publicaciones rápidas eliminadas: {rapidas}\n'
            f'  - Publicaciones con imagen eliminadas: {con_imagen}\n'
            f'  - Anuncios eliminados: {anuncios}\n'
            f'  - Total: {total}'
        )

        self.stdout.write(self.style.SUCCESS(mensaje))
        logger.info(
            f"[CLEANUP] Limpieza completada. Rápidas: {rapidas}, Con imagen: {con_imagen}, "
            f"Anuncios: {anuncios}, Total: {total}"
        )
