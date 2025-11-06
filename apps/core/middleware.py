from django.utils.deprecation import MiddlewareMixin

class MediaCORSMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path.startswith('/media/'):
            response['Access-Control-Allow-Origin'] = '*'
        return response
