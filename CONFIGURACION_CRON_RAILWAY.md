# Configuración de Actualización Automática - Polla Mundial

## Método Definitivo: Railway Cron Service

Este documento explica cómo configurar la actualización automática de partidos del Mundial usando un servicio dedicado en Railway.

## Archivos creados

- `cron_actualizar_mundial.sh` - Script que ejecuta las actualizaciones
- `cron_service.sh` - Servicio que ejecuta el script cada 30 minutos

## Paso 1: Push de archivos a Railway

```bash
git add cron_actualizar_mundial.sh cron_service.sh
git commit -m "Agregar servicio cron para actualización automática Polla Mundial"
git push sistoconstru mi-rama
```

## Paso 2: Importar partidos iniciales (UNA VEZ)

Ejecuta esto desde tu máquina local para importar los 72 partidos iniciales:

```bash
railway shell --service sighu-web
```

Dentro del shell:
```bash
python manage.py importar_partidos_mundial --season=2026
```

Deberías ver: `Partidos creados: 72`

## Paso 3: Crear servicio Cron en Railway (Opcional - Solo para automatización)

**Opción A: Desde Railway Dashboard**

1. Ve a tu proyecto: https://railway.app/project/construinmuniza
2. Click en "+ New Service"
3. Selecciona el mismo repositorio: `Sistoconstru/sistema-gestion-empleados`
4. Configura:
   - Name: `cron-polla-mundial`
   - Branch: `mi-rama`
   - Start Command: `bash cron_service.sh`
5. En Variables: Asegúrate que tenga las mismas variables que `sighu-web`:
   - `THESPORTSDB_API_KEY`
   - Todas las variables de base de datos (se comparten automáticamente)
6. Deploy

**Opción B: Ejecutar manualmente cuando sea necesario**

Puedes ejecutar las actualizaciones manualmente cuando quieras:

```bash
railway shell --service sighu-web
bash cron_actualizar_mundial.sh
```

## ¿Qué hace el servicio cron?

1. ✅ **Actualiza equipos TBD** - Reemplaza "TBD" por equipos clasificados
2. ✅ **Actualiza resultados** - Obtiene marcadores finales y calcula puntos
3. ✅ **Importa nuevos partidos** - Agrega partidos que se creen durante el torneo

## Horario optimizado

- Se ejecuta **cada 30 minutos**
- Solo entre **1 PM y 1 AM UTC**
- Optimiza uso de API (3000 requests/mes)

## Monitoreo

Ver logs del servicio cron en Railway Dashboard → cron-polla-mundial → Deployments → View Logs

## Para el lanzamiento del 1 de Junio 2026

1. ✅ Partidos importados (Paso 2)
2. ✅ Sistema funcionando en producción
3. ✅ Actualizaciones automáticas configuradas (Paso 3, opcional)
