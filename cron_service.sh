#!/bin/bash
# =============================================================================
# Servicio de Cron para Railway - Actualización Polla Mundial
# Este script se ejecuta continuamente en Railway como un servicio separado
# =============================================================================

# Función para verificar si estamos en horario permitido (1 PM - 1 AM UTC)
# Esto optimiza el uso de la API (solo 3000 requests/mes)
en_horario_permitido() {
    hora_utc=$(date -u +%H)
    # Permitido entre 13:00 y 23:59, y entre 00:00 y 01:59 UTC
    if [ "$hora_utc" -ge 13 ] || [ "$hora_utc" -le 1 ]; then
        return 0  # true
    else
        return 1  # false
    fi
}

echo "========================================"
echo "Servicio Cron Polla Mundial iniciado"
echo "Ejecuta actualizaciones cada 30 minutos"
echo "Horario: 1 PM - 1 AM UTC"
echo "========================================"

# Loop infinito - Railway mantiene el servicio corriendo
while true; do
    if en_horario_permitido; then
        echo ""
        echo "✓ Dentro de horario permitido - Ejecutando actualización..."
        bash cron_actualizar_mundial.sh
        echo ""
        echo "Próxima ejecución en 30 minutos..."
        sleep 1800  # 30 minutos
    else
        hora_actual=$(date -u +"%H:%M")
        echo "⏸ Fuera de horario ($hora_actual UTC) - Esperando hasta 1 PM..."
        sleep 3600  # 1 hora (revisar cada hora si estamos en horario)
    fi
done
