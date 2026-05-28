#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear predicciones de prueba con datos del Mundial 2022
Ejecutar: python manage.py shell < scripts/crear_predicciones_prueba.py
O copiar y pegar en: python manage.py shell
"""

from apps.employees.models import PartidoMundial, PrediccionMundial, Empleado
from django.db.models import Sum
from random import randint, choice

print("="*60)
print("🧪 Creando Predicciones de Prueba - Mundial 2022")
print("="*60)

# Obtener todos los partidos finalizados
partidos = PartidoMundial.objects.filter(finalizado=True).order_by('fecha_hora')[:15]  # Primeros 15 partidos

# Obtener empleados activos
empleados = Empleado.objects.filter(estado__codigo='ACTIVO')[:8]  # Hasta 8 empleados

if not empleados.exists():
    print("❌ ERROR: No hay empleados activos en la base de datos")
    print("   Crear empleados desde: /admin/employees/empleado/")
    print("   O asegurarse de que tengan estado ACTIVO")
else:
    print(f"\n📊 Configuración:")
    print(f"   • Partidos: {partidos.count()}")
    print(f"   • Empleados: {empleados.count()}")
    print(f"   • Predicciones totales a crear: {partidos.count() * empleados.count()}")

    # Limpiar predicciones anteriores
    print(f"\n🗑️  Limpiando predicciones anteriores...")
    PrediccionMundial.objects.all().delete()
    print(f"   ✓ Predicciones antiguas eliminadas")

    print(f"\n🎲 Generando predicciones aleatorias...")
    predicciones_creadas = 0
    errores = 0

    # Estrategias de predicción (para variedad)
    estrategias = ['optimista', 'pesimista', 'realista', 'conservador']

    for empleado in empleados:
        estrategia = choice(estrategias)
        puntos_empleado = 0

        for partido in partidos:
            try:
                # Generar predicción según estrategia
                if partido.goles_local is not None and partido.goles_visitante is not None:

                    if estrategia == 'optimista':
                        # Tiende a predecir más goles
                        pred_local = partido.goles_local + randint(0, 2)
                        pred_visitante = partido.goles_visitante + randint(0, 2)
                    elif estrategia == 'pesimista':
                        # Tiende a predecir menos goles
                        pred_local = max(0, partido.goles_local + randint(-2, 0))
                        pred_visitante = max(0, partido.goles_visitante + randint(-2, 0))
                    elif estrategia == 'conservador':
                        # Siempre predice empates o victorias mínimas
                        pred_local = randint(0, 2)
                        pred_visitante = randint(0, 2)
                    else:  # realista
                        # Predicción cercana al resultado real
                        pred_local = max(0, partido.goles_local + randint(-1, 1))
                        pred_visitante = max(0, partido.goles_visitante + randint(-1, 1))

                    # Crear predicción
                    prediccion = PrediccionMundial.objects.create(
                        empleado=empleado,
                        partido=partido,
                        goles_local_prediccion=pred_local,
                        goles_visitante_prediccion=pred_visitante
                    )

                    # Calcular puntos
                    puntos = prediccion.calcular_puntos()
                    prediccion.save()

                    puntos_empleado += puntos
                    predicciones_creadas += 1

            except Exception as e:
                errores += 1
                print(f"   ⚠️  Error creando predicción: {e}")

        print(f"   ✓ {empleado.nombre_completo} ({estrategia}): {puntos_empleado} puntos")

    print(f"\n✅ Predicciones creadas: {predicciones_creadas}")
    if errores > 0:
        print(f"⚠️  Errores encontrados: {errores}")

    # Mostrar ranking
    print(f"\n{'='*60}")
    print(f"🏆 TOP 10 Ranking Generado:")
    print(f"{'='*60}")

    ranking = PrediccionMundial.objects.values(
        'empleado__nombre_completo',
        'empleado__cargo_actual__nombre'
    ).annotate(
        total_puntos=Sum('puntos_ganados'),
        total_predicciones=Count('id')
    ).order_by('-total_puntos')[:10]

    for idx, entry in enumerate(ranking, 1):
        emoji = ''
        if idx == 1:
            emoji = '🥇'
        elif idx == 2:
            emoji = '🥈'
        elif idx == 3:
            emoji = '🥉'
        else:
            emoji = f'{idx}.'

        cargo = entry['empleado__cargo_actual__nombre'] or 'Sin cargo'
        print(f"{emoji:4} {entry['empleado__nombre_completo']:30} {entry['total_puntos']:4} pts ({entry['total_predicciones']} predicciones) - {cargo}")

    print(f"\n{'='*60}")
    print(f"✅ Datos de prueba creados exitosamente")
    print(f"{'='*60}")
    print(f"\n📍 Próximos pasos:")
    print(f"   1. Ver ranking web: http://localhost:8000/empleados/polla-mundial/ranking/")
    print(f"   2. Ver partidos: http://localhost:8000/empleados/polla-mundial/")
    print(f"   3. Admin: http://localhost:8000/admin/employees/prediccionmundial/")
    print(f"\n💡 Para regenerar datos, ejecuta este script nuevamente")
    print()

# Importaciones adicionales para evitar error
from django.db.models import Count
