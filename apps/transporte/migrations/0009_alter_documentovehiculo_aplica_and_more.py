"""Semaforización como nombre, y el vencimiento de los tributos corregido.

El vencimiento de un tributo anual se venía calculando sobre el plazo de su
propio año, así que un impuesto pagado el 18 de junio aparecía vencido el 30
de ese mismo mes. Lo que vence no es el pago sino el plazo del siguiente.

Esta migración recalcula los que quedaron mal. Solo toca los que tienen
exactamente la fecha que producía la fórmula vieja: si alguien ya la
corrigió a mano, esa fecha se respeta.
"""
from datetime import date

from django.db import migrations, models

LIMITES = {'impuesto': (6, 30), 'rodamiento': (12, 31)}


def corregir_vencimientos(apps, schema_editor):
    Documento = apps.get_model('transporte', 'DocumentoVehiculo')
    corregidos = 0
    for doc in Documento.objects.filter(tipo__in=LIMITES.keys()):
        if not doc.fecha_vencimiento:
            continue
        mes, dia = LIMITES[doc.tipo]
        base = doc.fecha_expedicion or doc.fecha_creacion.date()
        if doc.fecha_vencimiento != date(base.year, mes, dia):
            continue  # la pusieron a mano; no se toca
        doc.fecha_vencimiento = date(base.year + 1, mes, dia)
        doc.save(update_fields=['fecha_vencimiento'])
        corregidos += 1
    if corregidos:
        print(f'  → {corregidos} vencimiento(s) de tributos recalculados.')


class Migration(migrations.Migration):

    dependencies = [
        ('transporte', '0008_alter_documentovehiculo_tipo'),
    ]

    operations = [
        migrations.RunPython(corregir_vencimientos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='documentovehiculo',
            name='aplica',
            field=models.BooleanField(default=True, help_text='Desmarcar cuando el tributo no aplica a este vehículo (p. ej. semaforización en municipios que no la cobran).'),
        ),
        migrations.AlterField(
            model_name='documentovehiculo',
            name='tipo',
            field=models.CharField(choices=[('soat', 'SOAT'), ('tecnomecanica', 'Revisión tecnicomecánica'), ('poliza', 'Póliza de responsabilidad civil'), ('impuesto', 'Impuesto vehicular'), ('rodamiento', 'Semaforización o derechos de tránsito')], max_length=20),
        ),
    ]
