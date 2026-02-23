"""
Comando para poblar datos iniciales del módulo de encuestas.
Uso: python manage.py poblar_encuestas
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.surveys.models import TipoEncuesta
from apps.evaluations.models import TipoPregunta


class Command(BaseCommand):
    help = 'Pobla datos iniciales para el módulo de encuestas (tipos de pregunta y tipos de encuesta)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Poblando datos iniciales de Encuestas ===\n'))

        with transaction.atomic():
            # 1. Crear Tipos de Pregunta
            self._crear_tipos_pregunta()

            # 2. Crear Tipos de Encuesta
            self._crear_tipos_encuesta()

        self.stdout.write(self.style.SUCCESS('\n=== Proceso completado exitosamente ==='))

    def _crear_tipos_pregunta(self):
        """Crea los tipos de pregunta básicos"""
        self.stdout.write('\n1. Creando Tipos de Pregunta...')

        tipos_pregunta = [
            {
                'codigo': 'multiple_choice',
                'nombre': 'Opción Múltiple',
                'descripcion': 'Pregunta de selección única entre varias opciones',
                'permite_opciones': True,
                'permite_texto_libre': False
            },
            {
                'codigo': 'checkbox',
                'nombre': 'Checkbox (Múltiples selecciones)',
                'descripcion': 'Permite seleccionar múltiples opciones',
                'permite_opciones': True,
                'permite_texto_libre': False
            },
            {
                'codigo': 'text',
                'nombre': 'Texto Libre',
                'descripcion': 'Respuesta de texto largo (textarea)',
                'permite_opciones': False,
                'permite_texto_libre': True
            },
            {
                'codigo': 'short_text',
                'nombre': 'Texto Corto',
                'descripcion': 'Respuesta de texto corto (input)',
                'permite_opciones': False,
                'permite_texto_libre': True
            },
            {
                'codigo': 'rating',
                'nombre': 'Calificación (Escala Likert)',
                'descripcion': 'Escala de calificación del 1 al 5',
                'permite_opciones': True,
                'permite_texto_libre': False
            },
            {
                'codigo': 'select',
                'nombre': 'Lista Desplegable',
                'descripcion': 'Selección desde un menú desplegable',
                'permite_opciones': True,
                'permite_texto_libre': False
            },
        ]

        creados = 0
        actualizados = 0

        for tipo_data in tipos_pregunta:
            tipo, created = TipoPregunta.objects.update_or_create(
                codigo=tipo_data['codigo'],
                defaults={
                    'nombre': tipo_data['nombre'],
                    'descripcion': tipo_data.get('descripcion', ''),
                    'permite_opciones': tipo_data['permite_opciones'],
                    'permite_texto_libre': tipo_data['permite_texto_libre']
                }
            )

            if created:
                creados += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Creado: {tipo.nombre}'))
            else:
                actualizados += 1
                self.stdout.write(self.style.WARNING(f'  ↻ Actualizado: {tipo.nombre}'))

        self.stdout.write(
            self.style.SUCCESS(f'\nTipos de Pregunta: {creados} creados, {actualizados} actualizados')
        )

    def _crear_tipos_encuesta(self):
        """Crea los tipos de encuesta básicos"""
        self.stdout.write('\n2. Creando Tipos de Encuesta...')

        tipos_encuesta = [
            {
                'codigo': 'CLIMA_ORG',
                'nombre': 'Encuesta de Clima Organizacional',
                'descripcion': 'Evaluación del ambiente laboral y satisfacción de los empleados',
                'obligatoria': True,
                'anonima': False,
                'frecuencia_dias': 180,  # Cada 6 meses
                'activo': True
            },
            {
                'codigo': 'SATISFACCION',
                'nombre': 'Encuesta de Satisfacción Laboral',
                'descripcion': 'Medición de la satisfacción de los empleados con su trabajo',
                'obligatoria': False,
                'anonima': True,
                'frecuencia_dias': 90,  # Cada 3 meses
                'activo': True
            },
            {
                'codigo': 'LIDERAZGO',
                'nombre': 'Evaluación de Liderazgo',
                'descripcion': 'Evaluación de las competencias de liderazgo',
                'obligatoria': False,
                'anonima': True,
                'frecuencia_dias': 365,  # Anual
                'activo': True
            },
            {
                'codigo': 'CAPACITACION',
                'nombre': 'Encuesta Post-Capacitación',
                'descripcion': 'Evaluación de la efectividad de capacitaciones',
                'obligatoria': False,
                'anonima': False,
                'frecuencia_dias': None,  # Según demanda
                'activo': True
            },
            {
                'codigo': 'RIESGOS',
                'nombre': 'Identificación de Riesgos Psicosociales',
                'descripcion': 'Evaluación de factores de riesgo en el ambiente laboral',
                'obligatoria': True,
                'anonima': True,
                'frecuencia_dias': 365,  # Anual
                'activo': True
            },
            {
                'codigo': 'ENGAGEMENT',
                'nombre': 'Encuesta de Compromiso (Engagement)',
                'descripcion': 'Medición del nivel de compromiso de los empleados',
                'obligatoria': False,
                'anonima': False,
                'frecuencia_dias': 180,  # Cada 6 meses
                'activo': True
            },
            {
                'codigo': 'GENERAL',
                'nombre': 'Encuesta General',
                'descripcion': 'Encuesta de propósito general',
                'obligatoria': False,
                'anonima': False,
                'frecuencia_dias': None,
                'activo': True
            },
        ]

        creados = 0
        actualizados = 0

        for tipo_data in tipos_encuesta:
            tipo, created = TipoEncuesta.objects.update_or_create(
                codigo=tipo_data['codigo'],
                defaults={
                    'nombre': tipo_data['nombre'],
                    'descripcion': tipo_data['descripcion'],
                    'obligatoria': tipo_data['obligatoria'],
                    'anonima': tipo_data['anonima'],
                    'frecuencia_dias': tipo_data['frecuencia_dias'],
                    'activo': tipo_data['activo']
                }
            )

            if created:
                creados += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Creado: {tipo.nombre}'))
            else:
                actualizados += 1
                self.stdout.write(self.style.WARNING(f'  ↻ Actualizado: {tipo.nombre}'))

        self.stdout.write(
            self.style.SUCCESS(f'\nTipos de Encuesta: {creados} creados, {actualizados} actualizados')
        )

        # Mostrar guía de escalas Likert
        self._mostrar_guia_escalas()

    def _mostrar_guia_escalas(self):
        """Muestra guía para crear preguntas con escala Likert"""
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('GUÍA: Cómo crear preguntas con Escala Likert (1-5)'))
        self.stdout.write('='*70)
        self.stdout.write('''
Al crear una pregunta tipo "Calificación (Escala Likert)" o "Opción Múltiple",
puedes agregar las siguientes opciones:

ESCALA DE SATISFACCIÓN:
  Opción 1: Muy insatisfecho      | Valor: 1
  Opción 2: Insatisfecho          | Valor: 2
  Opción 3: Neutral               | Valor: 3
  Opción 4: Satisfecho            | Valor: 4
  Opción 5: Muy satisfecho        | Valor: 5

ESCALA DE FRECUENCIA:
  Opción 1: Nunca                 | Valor: 1
  Opción 2: Rara vez              | Valor: 2
  Opción 3: Algunas veces         | Valor: 3
  Opción 4: Frecuentemente        | Valor: 4
  Opción 5: Siempre               | Valor: 5

ESCALA DE ACUERDO:
  Opción 1: Totalmente en desacuerdo  | Valor: 1
  Opción 2: En desacuerdo             | Valor: 2
  Opción 3: Neutral                   | Valor: 3
  Opción 4: De acuerdo                | Valor: 4
  Opción 5: Totalmente de acuerdo     | Valor: 5

ESCALA DE IMPORTANCIA:
  Opción 1: Nada importante       | Valor: 1
  Opción 2: Poco importante       | Valor: 2
  Opción 3: Moderadamente importante | Valor: 3
  Opción 4: Importante            | Valor: 4
  Opción 5: Muy importante        | Valor: 5

Estos valores numéricos permiten calcular promedios y generar reportes
estadísticos de clima organizacional.
        ''')
        self.stdout.write('='*70 + '\n')
