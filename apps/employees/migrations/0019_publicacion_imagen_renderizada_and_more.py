# Generated migration for imagen_renderizada field - December 1, 2025

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0018_publicacion_comentario_and_more'),
    ]

    operations = [
        # Add imagen_renderizada field to Publicacion model
        migrations.AddField(
            model_name='publicacion',
            name='imagen_renderizada',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='anuncios_renderizados/%Y/%m/%d/',
                help_text='Imagen final con texto renderizado'
            ),
        ),
        # Update estilos field help_text to include new fields
        migrations.AlterField(
            model_name='publicacion',
            name='estilos',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Estilos: font_family, font_size, text_color, stroke_width, stroke_color, titulo_x, titulo_y, titulo_width, titulo_height, contenido_x, contenido_y, contenido_width, contenido_height'
            ),
        ),
    ]
