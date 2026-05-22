from django.db import models


class OdooSyncFalla(models.Model):
    EVENTOS = (
        ('created', 'Creado'),
        ('updated', 'Actualizado'),
        ('deleted', 'Eliminado'),
    )

    empleado = models.ForeignKey(
        'employees.Empleado',
        on_delete=models.CASCADE,
        related_name='odoo_sync_fallas',
    )
    evento = models.CharField(max_length=10, choices=EVENTOS)
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=200, blank=True)
    detalle = models.TextField(blank=True)
    http_status = models.IntegerField(null=True, blank=True)
    resuelta = models.BooleanField(default=False, help_text="Marcar cuando el pull horario reconcilió el cambio")

    class Meta:
        db_table = 'odoo_sync_fallas'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['resuelta', '-fecha']),
            models.Index(fields=['empleado', '-fecha']),
        ]

    def __str__(self):
        return f"{self.empleado_id} | {self.evento} | {self.fecha:%Y-%m-%d %H:%M}"
