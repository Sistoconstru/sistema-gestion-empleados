import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.views import View
from django.utils.encoding import smart_str

class PDFMediaView(View):
    def get(self, request, path):
        # Permitir cualquier PDF dentro de MEDIA_ROOT
        safe_base = os.path.abspath(settings.MEDIA_ROOT)
        abs_path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, path))
        print(f"[PDFMediaView] path param: {path}")
        print(f"[PDFMediaView] abs_path: {abs_path}")
        print(f"[PDFMediaView] safe_base: {safe_base}")
        if not abs_path.startswith(safe_base):
            print(f"[PDFMediaView] Archivo fuera de MEDIA_ROOT: {abs_path}")
            raise Http404('Archivo no permitido')
        if not os.path.exists(abs_path):
            print(f"[PDFMediaView] Archivo no encontrado: {abs_path}")
            raise Http404('Archivo no encontrado')
        response = FileResponse(open(abs_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="%s"' % smart_str(os.path.basename(abs_path))
        response['Access-Control-Allow-Origin'] = '*'
        print(f"[PDFMediaView] Archivo servido correctamente: {abs_path}")
        return response
