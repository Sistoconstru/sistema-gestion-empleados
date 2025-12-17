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

        return None

    def process_response(self, request, response):
        """Registra la auditoría después de procesar la petición"""
        # Solo procesar si tenemos datos de auditoría
        if not hasattr(request, '_audit_data'):
            return response

        # Solo registrar si la respuesta fue exitosa (2xx o 3xx)
        if not (200 <= response.status_code < 400):
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
        from apps.core.models import LogActividad

        audit_data = request._audit_data

        # Determinar la acción basada en el método HTTP y la ruta
        accion = self._determinar_accion(request)

        # Intentar extraer información del modelo y objeto
        modelo, objeto_id = self._extraer_modelo_objeto(request)

        # Extraer cambios realizados del request
        cambios = self._extraer_cambios(request)

        # Generar descripción legible
        descripcion = self._generar_descripcion(audit_data['user'], accion, modelo, cambios, request.path)

        # Crear el log solo si tenemos información relevante
        if accion or modelo:
            LogActividad.objects.create(
                usuario=audit_data['user'],
                accion=accion,
                modelo=modelo,
                objeto_id=objeto_id,
                descripcion=descripcion,
                cambios_realizados=cambios,
                ip_address=audit_data['ip_address'],
                user_agent=audit_data['user_agent'],
                metodo_http=audit_data['method'],
                url_accedida=audit_data['path']
            )

    def _determinar_accion(self, request):
        """Determina la acción realizada basada en el método HTTP y la URL"""
        metodo = request.method
        path = request.path.lower()

        # Mapeo de métodos a acciones
        if metodo == 'POST':
            if 'delete' in path or 'eliminar' in path:
                return 'eliminar'
            elif 'upload' in path or 'subir' in path or 'cargar' in path:
                return 'subir_archivo'
            elif 'aprobar' in path:
                return 'aprobar'
            elif 'rechazar' in path:
                return 'rechazar'
            elif 'asignar' in path:
                return 'asignar'
            elif 'enviar' in path:
                return 'enviar'
            else:
                return 'crear'
        elif metodo in ['PUT', 'PATCH']:
            if 'estado' in path:
                return 'cambiar_estado'
            elif 'cargo' in path:
                return 'cambiar_cargo'
            else:
                return 'modificar'
        elif metodo == 'DELETE':
            return 'eliminar'

        return 'accion'

    def _extraer_modelo_objeto(self, request):
        """Extrae el nombre del modelo y el ID del objeto de la URL"""
        path_parts = request.path.strip('/').split('/')

        # Intentar detectar el modelo de la URL
        modelo = None
        objeto_id = None

        # Rutas comunes: /app/model/id/ o /app/model/id/action/
        if len(path_parts) >= 2:
            # El segundo elemento suele ser el modelo
            modelo_candidato = path_parts[1]

            # Limpiar y formatear el nombre del modelo
            if modelo_candidato:
                modelo = modelo_candidato.rstrip('s')  # Quitar plural simple

                # Buscar ID en la URL (usualmente es UUID o número)
                for part in path_parts[2:]:
                    # Detectar UUID
                    if len(part) == 36 and part.count('-') == 4:
                        objeto_id = part
                        break
                    # Detectar ID numérico
                    elif part.isdigit():
                        objeto_id = part
                        break

        return modelo, objeto_id

    def _extraer_cambios(self, request):
        """Extrae los cambios del request.POST o request.body"""
        cambios = {}

        try:
            # Intentar obtener datos de POST
            if request.POST:
                cambios = dict(request.POST.lists())
                # Excluir campos sensibles
                campos_sensibles = ['password', 'csrfmiddlewaretoken', 'password1', 'password2']
                for campo in campos_sensibles:
                    cambios.pop(campo, None)

            # Si no hay POST, intentar leer el body (para APIs JSON)
            elif request.body:
                try:
                    cambios = json.loads(request.body)
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

    def _generar_descripcion(self, usuario, accion, modelo, cambios, url):
        """Genera una descripción legible en español de la acción realizada"""

        # Mapeo de acciones a verbos en español
        acciones_es = {
            'crear': 'creó',
            'modificar': 'modificó',
            'eliminar': 'eliminó',
            'aprobar': 'aprobó',
            'rechazar': 'rechazó',
            'subir_archivo': 'subió archivo a',
            'cambiar_estado': 'cambió el estado de',
            'cambiar_cargo': 'cambió el cargo de',
            'asignar': 'asignó',
            'enviar': 'envió',
        }

        # Mapeo de modelos a nombres legibles
        modelos_es = {
            'empleado': 'un empleado',
            'documento': 'un documento',
            'documentoempleado': 'un documento de empleado',
            'cargo': 'un cargo',
            'historialcargo': 'el historial de cargo',
            'evaluacion': 'una evaluación',
            'asignacionevaluacion': 'una asignación de evaluación',
            'capacitacion': 'una capacitación',
            'inscripcioncapacitacion': 'una inscripción a capacitación',
            'producto': 'un producto',
            'venta': 'una venta',
            'publicacion': 'una publicación',
            'anuncio': 'un anuncio',
            'notificacion': 'una notificación',
            'mensaje': 'un mensaje',
        }

        # Obtener nombre del usuario
        usuario_nombre = usuario.get_full_name() if usuario and hasattr(usuario, 'get_full_name') and usuario.get_full_name() else (
            usuario.username if usuario else 'Sistema'
        )

        # Obtener verbo en español
        verbo = acciones_es.get(accion, accion)

        # Obtener nombre del modelo en español
        modelo_lower = modelo.lower() if modelo else 'registro'
        modelo_es = modelos_es.get(modelo_lower, f'el {modelo_lower}' if modelo else 'un registro')

        # Construir la descripción base
        descripcion = f"{usuario_nombre} {verbo} {modelo_es}"

        # Agregar información específica según el modelo y cambios
        if cambios:
            # Para empleados, agregar nombre si está disponible
            if modelo_lower == 'empleado' and isinstance(cambios, dict):
                nombre = self._extraer_nombre_de_cambios(cambios)
                if nombre:
                    descripcion = f"{usuario_nombre} {verbo} el empleado {nombre}"

            # Para documentos, mencionar tipo si está disponible
            elif 'documento' in modelo_lower and isinstance(cambios, dict):
                tipo_doc = cambios.get('tipo_documento', [''])[0] if isinstance(cambios.get('tipo_documento'), list) else cambios.get('tipo_documento', '')
                if tipo_doc:
                    descripcion = f"{usuario_nombre} {verbo} un documento tipo {tipo_doc}"

            # Para cambios de estado, mencionar el nuevo estado
            elif accion == 'cambiar_estado' and isinstance(cambios, dict):
                nuevo_estado = cambios.get('estado', [''])[0] if isinstance(cambios.get('estado'), list) else cambios.get('estado', '')
                if nuevo_estado:
                    descripcion = f"{usuario_nombre} cambió el estado a '{nuevo_estado}'"

            # Para publicaciones/anuncios, agregar título
            elif modelo_lower in ['publicacion', 'anuncio'] and isinstance(cambios, dict):
                titulo = cambios.get('titulo', [''])[0] if isinstance(cambios.get('titulo'), list) else cambios.get('titulo', '')
                if titulo:
                    titulo_corto = titulo[:50] + '...' if len(titulo) > 50 else titulo
                    descripcion = f"{usuario_nombre} {verbo} '{titulo_corto}'"

        # Agregar información de la URL si es relevante
        if '/aprobar/' in url.lower():
            descripcion = f"{usuario_nombre} aprobó un registro"
        elif '/rechazar/' in url.lower():
            descripcion = f"{usuario_nombre} rechazó un registro"

        return descripcion

    def _extraer_nombre_de_cambios(self, cambios):
        """Intenta extraer el nombre completo de los cambios"""
        if not isinstance(cambios, dict):
            return None

        # Intentar obtener nombres y apellidos
        nombres = cambios.get('nombres', [''])[0] if isinstance(cambios.get('nombres'), list) else cambios.get('nombres', '')
        apellidos = cambios.get('apellidos', [''])[0] if isinstance(cambios.get('apellidos'), list) else cambios.get('apellidos', '')

        if nombres and apellidos:
            return f"{nombres} {apellidos}"
        elif nombres:
            return nombres
        elif apellidos:
            return apellidos

        return None
