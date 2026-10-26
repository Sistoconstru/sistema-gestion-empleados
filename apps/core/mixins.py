"""Mixins de autorización compartidos entre apps."""
from django.contrib.auth.mixins import UserPassesTestMixin


class StaffRequiredMixin(UserPassesTestMixin):
    """Restringe la vista al personal administrativo (is_staff o superuser).

    Existe porque varias vistas de RRHH solo tenían LoginRequiredMixin, que
    autentica pero no autoriza: cualquier empleado llegaba escribiendo la URL
    aunque el menú no se la ofreciera, y los `{% if perms %}` de los templates
    solo esconden botones. Esconder un enlace no es un control de acceso.

    Frente a `staff_member_required`, este mixin manda al login propio del
    sistema en vez del admin de Django, y devuelve 403 a quien ya tiene sesión
    pero no privilegios — el mismo comportamiento que PermissionRequiredMixin
    en el resto del proyecto.
    """

    def test_func(self):
        usuario = self.request.user
        return bool(usuario.is_staff or usuario.is_superuser)
