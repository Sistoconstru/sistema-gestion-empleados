"""Obliga a cambiar la contraseña antes de dejar usar el resto del sistema."""
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class ForzarCambioPasswordMiddleware(MiddlewareMixin):
    """Redirige al cambio de contraseña mientras `debe_cambiar_password` esté activo.

    Existe por el alta automática de usuarios: la contraseña inicial se genera
    como {PrimerNombre}{numero_documento}, y el número de documento aparece en
    listados y exportaciones, así que es derivable. Entregar una contraseña
    temporal no sirve de nada si el usuario puede seguir navegando sin
    cambiarla, de ahí el bloqueo a nivel de middleware y no solo un aviso.
    """

    # Rutas que tienen que seguir respondiendo con el flag activo. Sin ellas el
    # usuario entra en un bucle de redirecciones y no puede ni cambiar la
    # contraseña ni cerrar sesión. Las de PWA se eximen para no romper el
    # service worker, que no sabe seguir un redirect a una página HTML.
    PREFIJOS_EXENTOS = (
        '/auth/password-change/',
        '/auth/password-reset/',
        '/auth/reset/',
        '/auth/logout/',
        '/logout/',
        '/admin/logout/',
        '/static/',
        '/media/',
        '/sw.js',
        '/manifest.webmanifest',
        '/pwa/',
    )

    def process_request(self, request):
        usuario = getattr(request, 'user', None)
        if not usuario or not usuario.is_authenticated:
            return None
        # getattr porque el cliente Odoo autentica con un usuario sintético
        # (_ServiceTokenUser) que no es una fila de la tabla y no tiene el campo.
        if not getattr(usuario, 'debe_cambiar_password', False):
            return None
        if request.path.startswith(self.PREFIJOS_EXENTOS):
            return None
        return redirect('authentication:password_change')
