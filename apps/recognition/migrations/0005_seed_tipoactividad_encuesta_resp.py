from django.db import migrations


def crear_tipos(apps, schema_editor):
    TipoActividad = apps.get_model('recognition', 'TipoActividad')
    defaults = [
        ('ENCUESTA_RESP', 'Encuesta respondida', 'Puntos por completar una encuesta asignada.', 5, 1.0),
        ('CAP_COMPLETADA', 'Capacitación completada', 'Puntos por completar una capacitación.', 20, 1.0),
        ('EVAL_EXCELENTE', 'Evaluación excelente', 'Evaluación con calificación excelente.', 50, 1.5),
        ('EVAL_BUENA', 'Evaluación buena', 'Evaluación con buena calificación.', 30, 1.2),
        ('EVAL_SATISFACTORIA', 'Evaluación satisfactoria', 'Evaluación satisfactoria.', 15, 1.0),
    ]
    for codigo, nombre, desc, base, mult in defaults:
        TipoActividad.objects.get_or_create(
            codigo=codigo,
            defaults=dict(nombre=nombre, descripcion=desc,
                          puntos_base=base, multiplicador_complejidad=mult, activo=True),
        )


def borrar_tipos(apps, schema_editor):
    TipoActividad = apps.get_model('recognition', 'TipoActividad')
    TipoActividad.objects.filter(codigo__in=[
        'ENCUESTA_RESP', 'CAP_COMPLETADA', 'EVAL_EXCELENTE',
        'EVAL_BUENA', 'EVAL_SATISFACTORIA',
    ]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('recognition', '0004_alter_tipobeneficio_imagen'),
    ]
    operations = [
        migrations.RunPython(crear_tipos, borrar_tipos),
    ]
