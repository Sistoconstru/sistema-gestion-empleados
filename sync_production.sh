#!/bin/bash
# Script para sincronizar archivos estáticos en producción
# Ejecutar este script en el servidor de producción

echo "🚀 Sincronizando archivos estáticos corporativos..."

# 1. Hacer pull de los últimos cambios
echo "📥 Descargando últimos cambios del repositorio..."
git pull origin mi-rama

# 2. Recopilar archivos estáticos
echo "📦 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# 3. Reiniciar servicios (ajustar según tu configuración)
echo "🔄 Reiniciando servicios web..."

# Para Apache
if command -v apache2 &> /dev/null; then
    sudo systemctl reload apache2
    echo "✅ Apache reiniciado"
fi

# Para Nginx + Gunicorn
if command -v nginx &> /dev/null; then
    sudo systemctl reload nginx
    echo "✅ Nginx reiniciado"
fi

if command -v gunicorn &> /dev/null; then
    sudo systemctl restart gunicorn
    echo "✅ Gunicorn reiniciado"
fi

# 4. Verificar que los archivos CSS estén en su lugar
echo "🔍 Verificando archivos CSS..."
if [ -f "staticfiles/css/corporativo.css" ]; then
    echo "✅ corporativo.css encontrado en staticfiles"
    echo "📄 Tamaño del archivo: $(du -h staticfiles/css/corporativo.css | cut -f1)"
else
    echo "❌ ERROR: corporativo.css no encontrado en staticfiles"
fi

echo ""
echo "🎉 Sincronización completada!"
echo ""
echo "📋 Pasos de verificación:"
echo "   1. Abrir el navegador en modo incógnito"
echo "   2. Ir al dashboard administrativo"
echo "   3. Verificar que las tarjetas tengan colores corporativos"
echo "   4. Si persisten problemas, limpiar caché del navegador (Ctrl+Shift+R)"
echo ""
echo "🌐 URL de verificación: https://tu-dominio.com/recognition/admin/"