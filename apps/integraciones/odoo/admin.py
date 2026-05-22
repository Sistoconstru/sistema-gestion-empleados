from django.contrib import admin

from .models import OdooSyncFalla


@admin.register(OdooSyncFalla)
class OdooSyncFallaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'empleado', 'evento', 'http_status', 'motivo', 'resuelta')
    list_filter = ('resuelta', 'evento', 'fecha')
    search_fields = ('empleado__numero_documento', 'empleado__nombres', 'empleado__apellidos', 'motivo')
    readonly_fields = ('empleado', 'evento', 'fecha', 'motivo', 'detalle', 'http_status')
    list_per_page = 50
    date_hierarchy = 'fecha'

    def has_add_permission(self, request):
        return False
