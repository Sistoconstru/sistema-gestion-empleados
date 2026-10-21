import os
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
)
from django.views.decorators.http import require_GET


def _host_permitido(hostname):
    """True solo para el dominio del bucket propio.

    Se compara el hostname ya parseado y no por substring: el chequeo anterior
    (`'amazonaws.com' in file_url`) dejaba pasar urls como
    https://atacante.com/amazonaws.com, lo que convertía esta vista en un proxy
    abierto hacia cualquier host de internet.
    """
    bucket = (getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', '') or '').lower()
    return bool(bucket) and (hostname or '').lower() == bucket


def _ruta_dentro_de_media(ruta_relativa):
    """Resuelve `ruta_relativa` bajo MEDIA_ROOT, o None si se escapa del directorio.

    Sin esta contención `?file=/media/../.env` entregaba el .env completo
    (SECRET_KEY, credenciales de BD), porque os.path.join() concatena los '..'
    sin resolverlos y no había ninguna validación posterior.
    """
    base = os.path.realpath(settings.MEDIA_ROOT)
    destino = os.path.realpath(os.path.join(base, ruta_relativa.lstrip('/\\')))
    if destino != base and not destino.startswith(base + os.sep):
        return None
    return destino


@login_required
@require_GET
def proxy_pdf(request):
    """Sirve un PDF para el visor pdf.js del reproductor de capacitaciones.

    Solo acepta dos orígenes: el bucket propio (urls firmadas de S3) y archivos
    bajo MEDIA_ROOT. Cualquier otro destino se rechaza.
    """
    file_url = request.GET.get('file')
    if not file_url:
        return HttpResponseBadRequest('Missing file URL')

    partes = urlparse(file_url)

    if partes.scheme or partes.netloc:
        if partes.netloc != request.get_host():
            # URL externa: únicamente https hacia nuestro propio bucket.
            if partes.scheme != 'https' or not _host_permitido(partes.hostname):
                return HttpResponseForbidden('Origen no permitido')
            if not partes.path.lower().endswith('.pdf'):
                return HttpResponseBadRequest('Solo se permiten archivos PDF')
            try:
                upstream = requests.get(file_url, stream=True, timeout=10)
                upstream.raise_for_status()
            except requests.RequestException:
                return HttpResponseNotFound('No se pudo obtener el PDF')
            return HttpResponse(upstream.content, content_type='application/pdf')
        # Mismo host (ej. http://127.0.0.1:8000/media/...): se resuelve por la
        # rama local con el path, sin hacer una petición de vuelta a nosotros.
        ruta = partes.path
    else:
        ruta = file_url

    # Rama local: solo lo que vive bajo /media/.
    if not ruta.startswith('/media/'):
        return HttpResponseBadRequest('Invalid file URL format')
    if not ruta.lower().endswith('.pdf'):
        return HttpResponseBadRequest('Solo se permiten archivos PDF')

    destino = _ruta_dentro_de_media(ruta[len('/media/'):])
    if destino is None:
        return HttpResponseForbidden('Ruta no permitida')
    if not os.path.isfile(destino):
        return HttpResponseNotFound('File not found')

    response = FileResponse(open(destino, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(destino)}"'
    return response
