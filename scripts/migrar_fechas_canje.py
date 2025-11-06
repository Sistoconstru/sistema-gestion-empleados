#!/usr/bin/env python
"""
Script para migrar datos de fecha_entrega a fecha_reclamo_programada
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.recognition.models import CanjeoBeneficio
from django.utils import timezone
from datetime import datetime, time

def migrar_fechas():
    print("=== Migración de fechas de canje ===")
    
    # Buscar canjes aprobados que tienen fecha_entrega pero no fecha_reclamo_programada
    canjes_a_migrar = CanjeoBeneficio.objects.filter(
        estado='aprobado',
        fecha_entrega__isnull=False,
        fecha_reclamo_programada__isnull=True
    )
    
    print(f"Encontrados {canjes_a_migrar.count()} canjes para migrar")
    
    for canje in canjes_a_migrar:
        # Si la fecha_entrega tiene hora 00:00:00, probablemente era una fecha programada
        if canje.fecha_entrega.time() == time(0, 0, 0):
            print(f"Migrando canje {canje.codigo_canje}: {canje.fecha_entrega}")
            canje.fecha_reclamo_programada = canje.fecha_entrega.date()
            canje.fecha_entrega = None  # Limpiar fecha_entrega porque no se ha entregado aún
            canje.save()
            print(f"  -> Fecha reclamo programada: {canje.fecha_reclamo_programada}")
        else:
            print(f"Canje {canje.codigo_canje} parece tener fecha de entrega real, no se migra")
    
    print("Migración completada")
    
    # Mostrar estadísticas finales
    print("\n=== Estadísticas ===")
    print(f"Total canjes: {CanjeoBeneficio.objects.count()}")
    print(f"Canjes solicitados: {CanjeoBeneficio.objects.filter(estado='solicitado').count()}")
    print(f"Canjes aprobados: {CanjeoBeneficio.objects.filter(estado='aprobado').count()}")
    print(f"Canjes entregados: {CanjeoBeneficio.objects.filter(estado='entregado').count()}")
    print(f"Canjes con fecha reclamo programada: {CanjeoBeneficio.objects.filter(fecha_reclamo_programada__isnull=False).count()}")

if __name__ == "__main__":
    migrar_fechas()