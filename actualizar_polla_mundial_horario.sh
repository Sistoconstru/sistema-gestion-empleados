#!/bin/bash
# =============================================================================
# Script de Linux/Mac para actualizar la Polla Mundial (HORARIO LIMITADO)
# =============================================================================
# Este script solo ejecuta entre 1 PM (13:00) y 1 AM (01:00)
# REDUCE CONSUMO DE API EN 50%
# Configurar en crontab: */30 * * * * /ruta/proyecto/actualizar_polla_mundial_horario.sh

# Cambiar al directorio del proyecto
cd "$(dirname "$0")"

# Obtener hora actual (formato 24h: 0-23)
hora_actual=$(date +%H | sed 's/^0//')

# Verificar si estamos en el horario permitido (13:00 - 01:00)
# Horario: 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1
if [ "$hora_actual" -ge 13 ] || [ "$hora_actual" -le 1 ]; then
    # Dentro del horario permitido - Ejecutar
    echo "========================================"
    echo "Actualización Polla Mundial - $(date)"
    echo "Horario permitido: 1 PM - 1 AM"
    echo "========================================"

    # Activar entorno virtual (ajusta la ruta si es diferente)
    if [ -f venv/bin/activate ]; then
        source venv/bin/activate
    elif [ -f .venv/bin/activate ]; then
        source .venv/bin/activate
    else
        echo "ADVERTENCIA: No se encontró entorno virtual"
    fi

    # 1. Actualizar equipos TBD (por si se definieron nuevos clasificados)
    echo ""
    echo "[1/3] Actualizando equipos TBD..."
    python manage.py actualizar_equipos_tbd

    # 2. Actualizar resultados de partidos finalizados
    echo ""
    echo "[2/3] Actualizando resultados de partidos..."
    python manage.py actualizar_resultados_mundial --verbose

    # 3. Importar nuevos partidos (por si se agregaron partidos de fases siguientes)
    echo ""
    echo "[3/3] Verificando nuevos partidos..."
    python manage.py importar_partidos_mundial --force

    echo ""
    echo "========================================"
    echo "Actualización completada - $(date)"
    echo "========================================"

    # Registrar en log
    mkdir -p logs
    echo "$(date) - Actualización completada" >> logs/polla_mundial_updates.log
else
    # Fuera del horario permitido - Omitir
    mkdir -p logs
    echo "$(date) - Fuera de horario permitido (1 PM - 1 AM). Omitiendo actualización..." >> logs/polla_mundial_updates.log
fi

exit 0
