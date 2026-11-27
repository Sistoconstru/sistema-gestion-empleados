from django.utils.deprecation import MiddlewareMixin
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
import json
import logging

logger = logging.getLogger(__name__)


class MediaCORSMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path.startswith('/media/'):
            response['Access-Control-Allow-Origin'] = '*'
        return response


class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware para auditoría automática de todas las operaciones en la aplicación.
    Registra: usuario, acción, modelo, cambios, IP, user agent, etc.
    """

    # Rutas que NO deben ser auditadas (para evitar ruido en logs)
    EXCLUDE_PATHS = [
        '/admin/jsi18n/',
        '/static/',
        '/media/',
        '/favicon.ico',
        '/__debug__/',
        '/api/notifications/check/',  # Polling de notificaciones
        '/api/notifications/unread-count/',  # Contador de notificaciones
    ]

    # Métodos HTTP que se deben auditar
    AUDIT_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']

    def process_request(self, request):
        """Captura el estado inicial antes de procesar la petición"""
        # Solo auditar métodos que modifican datos
        if request.method not in self.AUDIT_METHODS:
            return None

        # Excluir rutas específicas
        if any(request.path.startswith(path) for path in self.EXCLUDE_PATHS):
            return None

        # Guardar datos de la request para usar en process_response
        request._audit_data = {
            'method': request.method,
            'path': request.path,
            'user': request.user if request.user.is_authenticated else None,
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
        }
        # Antes de la vista: ruta y objeto afectado (un borrado conserva el
        # nombre de lo que se borra). Ver apps/core/auditoria.py.
        try:
            from apps.core import auditoria
            request._audit_data['contexto'] = auditoria.preparar(request)
        except Exception as e:
            logger.warning(f"Auditoría: no se pudo preparar el contexto: {e}")
            request._audit_data['contexto'] = None

        return None

    def process_response(self, request, response):
        """Registra la auditoría después de procesar la petición"""
        # Solo procesar si tenemos datos de auditoría
        if not hasattr(request, '_audit_data'):
            return response

        # Solo registrar si la respuesta fue exitosa (2xx o 3xx). Excepción: el
        # bloqueo del login por demasiados intentos (429 de axes) sí interesa.
        es_bloqueo_login = response.status_code == 429 and 'login' in request.path
        if not (200 <= response.status_code < 400) and not es_bloqueo_login:
            return response

        # Registrar la acción en segundo plano
        try:
            self._create_audit_log(request, response)
        except Exception as e:
            # No fallar la request si hay error en auditoría
            logger.error(f"Error al crear log de auditoría: {e}", exc_info=True)

        return response

    def _create_audit_log(self, request, response):
        """Crea el registro de auditoría en la base de datos"""
        from apps.core import auditoria
        from apps.core.models import LogActividad

        audit_data = request._audit_data
        cambios = self._extraer_cambios(request)
        accion, modulo, texto = auditoria.interpretar(
            audit_data.get('contexto'), cambios, response.status_code,
        )

        # Tras un login exitoso el usuario ya está en la sesión; antes del
        # login (process_request) era anónimo.
        usuario = request.user if request.user.is_authenticated else audit_data['user']
        if accion == 'login_fallido' or accion == 'login_bloqueado':
            usuario = None
        if usuario:
            quien = usuario.get_full_name() or usuario.username
        elif modulo == 'odoo':
            quien = 'Odoo'
        else:
            quien = 'Alguien sin sesión'

        LogActividad.objects.create(
            usuario=usuario,
            accion=accion,
            modelo=(modulo or '')[:50],
            objeto_id=self._extraer_objeto_id(request),
            descripcion=f'{quien} {texto}',
            cambios_realizados=cambios,
            ip_address=audit_data['ip_address'],
            user_agent=audit_data['user_agent'],
            metodo_http=audit_data['method'],
            url_accedida=audit_data['path']
        )

    def _extraer_objeto_id(self, request):
        """Primer UUID o número de la URL (el objeto afectado)."""
        for part in request.path.strip('/').split('/')[1:]:
            if len(part) == 36 and part.count('-') == 4:
                return part
        return None

    # Subcadenas que marcan un campo como no auditable. Cubren los nombres de
    # los formularios de Django (old_password, new_password1/2), los del alta de
    # usuarios (password1/2) y los secretos de integraciones.
    FRAGMENTOS_SENSIBLES = ('password', 'passwd', 'contrasena', 'contraseña',
                            'token', 'secret', 'csrfmiddlewaretoken')

    def _es_campo_sensible(self, nombre):
        nombre_lower = str(nombre).lower()
        return any(fragmento in nombre_lower for fragmento in self.FRAGMENTOS_SENSIBLES)

    def _extraer_cambios(self, request):
        """Extrae los cambios del request.POST o request.body"""
        cambios = {}

        try:
            # Intentar obtener datos de POST
            if request.POST:
                cambios = dict(request.POST.lists())
                # Excluir campos sensibles. Se filtra por subcadena y no por
                # lista exacta: la lista anterior ('password', 'password1',
                # 'password2') no cubría los nombres que usan los formularios de
                # Django ('old_password', 'new_password1', 'new_password2'), así
                # que cada cambio o reset de contraseña quedaba guardado en claro
                # en LogActividad.cambios_realizados.
                cambios = {
                    clave: valor for clave, valor in cambios.items()
                    if not self._es_campo_sensible(clave)
                }

            # Si no hay POST, intentar leer el body (para APIs JSON).
            # Se filtra por content_type: en una subida multipart el stream ya
            # lo consumió el parser de archivos y tocar request.body lanza
            # RawPostDataException. Antes eso pasaba en cada imagen subida al
            # feed: llenaba el log de avisos y dejaba la acción sin auditar.
            elif request.content_type == 'application/json' and request.body:
                try:
                    cambios = json.loads(request.body)
                    if isinstance(cambios, dict):
                        cambios = {
                            clave: valor for clave, valor in cambios.items()
                            if not self._es_campo_sensible(clave)
                        }
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass

            # Limitar el tamaño del JSON a 10KB para evitar logs enormes
            cambios_json = json.dumps(cambios, cls=DjangoJSONEncoder)
            if len(cambios_json) > 10240:
                cambios = {'_nota': 'Datos muy grandes, no se registraron todos los cambios'}

        except Exception as e:
            logger.warning(f"Error al extraer cambios del request: {e}")
            cambios = {}

        return cambios if cambios else None

    def _get_client_ip(self, request):
        """Obtiene la IP real del cliente (considerando proxies)"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip
