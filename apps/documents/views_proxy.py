from django.http import HttpResponse, HttpResponseBadRequest
import requests
from django.views.decorators.http import require_GET

@require_GET
def proxy_pdf(request):
    url = request.GET.get('file')
    if not url:
        return HttpResponseBadRequest('Missing file URL')
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return HttpResponse(response.content, content_type='application/pdf')
    except Exception as e:
        return HttpResponse(f'Error fetching PDF: {e}', status=404)
