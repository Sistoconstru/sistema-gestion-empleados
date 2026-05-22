from django.conf import settings
from rest_framework import authentication, exceptions


class _ServiceTokenUser:
    """Usuario sintético para el cliente Odoo: pasa IsAuthenticated sin ser un User real."""
    is_authenticated = True
    is_anonymous = False
    is_active = True
    is_staff = False
    is_superuser = False
    username = 'odoo-service'
    pk = None

    def __str__(self):
        return self.username


class OdooServiceTokenAuthentication(authentication.BaseAuthentication):
    """Valida el header `Authorization: Token <SIGHU_ODOO_TOKEN>` contra una env var.

    No usa la tabla `authtoken_token` de DRF — el token es un secreto estático
    rotable cambiando la env var y reiniciando el servicio.
    """

    keyword = 'Token'

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode('latin-1')
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        provided = parts[1]
        expected = getattr(settings, 'SIGHU_ODOO_TOKEN', None)
        if not expected:
            raise exceptions.AuthenticationFailed('SIGHU_ODOO_TOKEN no configurado en el servidor.')
        if provided != expected:
            raise exceptions.AuthenticationFailed('Token inválido.')

        return (_ServiceTokenUser(), provided)

    def authenticate_header(self, request):
        return self.keyword
