from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.http import require_GET
from django.conf import settings
import os
import requests

@require_GET
def proxy_pdf(request):
    file_url = request.GET.get('file')
    if not file_url:
        return HttpResponseBadRequest('Missing file URL')

    try:
        # Caso 1: Si la URL es externa (S3, etc.), usar requests
        if file_url.startswith('https://') and 'amazonaws.com' in file_url:
            response = requests.get(file_url, stream=True, timeout=10)
            response.raise_for_status()
            return HttpResponse(response.content, content_type='application/pdf')

        # Caso 2: Si es una URL local (/media/...), servir desde el sistema de archivos
        if file_url.startswith('/media/'):
            # Extraer la ruta relativa del archivo
            relative_path = file_url.replace('/media/', '')
            file_path = os.path.join(settings.MEDIA_ROOT, relative_path)

            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                return HttpResponseNotFound(f'File not found: {relative_path}')

            # Leer y servir el archivo
            with open(file_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
                return response

        # Caso 3: URL completa local (http://127.0.0.1:8000/media/...)
        if '/media/' in file_url:
            # Extraer solo la parte de /media/...
            media_index = file_url.find('/media/')
            relative_url = file_url[media_index:]
            relative_path = relative_url.replace('/media/', '')
            file_path = os.path.join(settings.MEDIA_ROOT, relative_path)

            if not os.path.exists(file_path):
                return HttpResponseNotFound(f'File not found: {relative_path}')

            with open(file_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
                return response

        return HttpResponseBadRequest('Invalid file URL format')

    except Exception as e:
        return HttpResponse(f'Error fetching PDF: {str(e)}', status=500)
