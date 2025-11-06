# apps/recognition/management/commands/crear_beneficios_ejemplo.py

from django.core.management.base import BaseCommand
from apps.recognition.models import TipoBeneficio


class Command(BaseCommand):
    help = 'Crea beneficios de ejemplo para probar el sistema de canjes'

    def handle(self, *args, **options):
        beneficios_ejemplo = [
            {
                'codigo': 'DESC_ALMUERZO',
                'nombre': 'Descuento en Almuerzo',
                'descripcion': 'Descuento del 50% en almuerzo en el restaurante de la empresa',
                'categoria': 'alimentacion',
                'costo_puntos': 25,
                'stock_inicial': 100,
                'stock_actual': 100,
                'disponible': True
            },
            {
                'codigo': 'DIA_LIBRE',
                'nombre': 'Día Libre Adicional',
                'descripcion': 'Un día libre adicional a tu tiempo de vacaciones',
                'categoria': 'tiempo',
                'costo_puntos': 200,
                'stock_inicial': 10,
                'stock_actual': 10,
                'disponible': True
            },
            {
                'codigo': 'TARJETA_REGALO',
                'nombre': 'Tarjeta Regalo $50.000',
                'descripcion': 'Tarjeta regalo por valor de $50.000 COP para uso en tiendas afiliadas',
                'categoria': 'compras',
                'costo_puntos': 500,
                'stock_inicial': 20,
                'stock_actual': 20,
                'disponible': True
            },
            {
                'codigo': 'CURSO_ONLINE',
                'nombre': 'Curso Online de Capacitación',
                'descripcion': 'Acceso a curso online de desarrollo profesional de tu elección',
                'categoria': 'educacion',
                'costo_puntos': 150,
                'stock_inicial': None,  # Sin límite
                'stock_actual': None,
                'disponible': True
            },
            {
                'codigo': 'PARKING_VIP',
                'nombre': 'Parking VIP por 1 Mes',
                'descripcion': 'Acceso al estacionamiento VIP de la empresa por un mes',
                'categoria': 'comodidad',
                'costo_puntos': 100,
                'stock_inicial': 5,
                'stock_actual': 5,
                'disponible': True
            },
            {
                'codigo': 'CENA_RESTAURANTE',
                'nombre': 'Cena para 2 en Restaurante',
                'descripcion': 'Cena romántica para dos personas en restaurante exclusivo',
                'categoria': 'entretenimiento',
                'costo_puntos': 300,
                'stock_inicial': 8,
                'stock_actual': 8,
                'disponible': True
            },
            {
                'codigo': 'MASAJE_SPA',
                'nombre': 'Sesión de Masaje en Spa',
                'descripcion': 'Sesión de masaje relajante de 60 minutos en spa premium',
                'categoria': 'bienestar',
                'costo_puntos': 180,
                'stock_inicial': 15,
                'stock_actual': 15,
                'disponible': True
            },
            {
                'codigo': 'GADGET_TECH',
                'nombre': 'Gadget Tecnológico',
                'descripcion': 'Auriculares inalámbricos o dispositivo tecnológico similar',
                'categoria': 'tecnologia',
                'costo_puntos': 400,
                'stock_inicial': 6,
                'stock_actual': 6,
                'disponible': True
            }
        ]

        for beneficio_data in beneficios_ejemplo:
            beneficio, created = TipoBeneficio.objects.get_or_create(
                codigo=beneficio_data['codigo'],
                defaults=beneficio_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Creado: {beneficio.nombre} - {beneficio.costo_puntos} pts')
                )
            else:
                # Actualizar campos si ya existe
                for key, value in beneficio_data.items():
                    if key != 'codigo':  # No actualizar el código
                        setattr(beneficio, key, value)
                beneficio.save()
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Actualizado: {beneficio.nombre}')
                )

        self.stdout.write(
            self.style.SUCCESS('\n🎁 Beneficios de ejemplo creados correctamente!')
        )
        self.stdout.write(
            'Los empleados ya pueden canjear estos beneficios usando sus puntos.'
        )