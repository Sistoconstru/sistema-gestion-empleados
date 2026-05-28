# 🚀 Deployment Polla Mundial en Railway (Producción)

## 📋 Índice
1. [Visión General](#visión-general)
2. [Implementación Provisional (Gratis)](#implementación-provisional-gratis)
3. [Implementación Producción (Mundial 2026)](#implementación-producción-mundial-2026)
4. [Configuración de Cron Jobs en Railway](#configuración-de-cron-jobs-en-railway)
5. [Monitoreo y Logs](#monitoreo-y-logs)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Visión General

### Opciones de Deployment

| Opción | Cuándo | Costo Railway | Costo API | Total |
|--------|--------|---------------|-----------|-------|
| **🧪 Provisional** | Ahora (pruebas) | $0-5/mes | $0 | $0-5/mes |
| **⚡ Optimizado** | Mundial 2026 | $0-5/mes | $9/mes | $9-14/mes |
| **🏆 Completo** | Mundial 2026 | $5-20/mes | $18/mes | $23-38/mes |

**Notas:**
- Railway: $0 si está bajo uso del plan gratuito, o $5-20/mes según uso
- API: TheSportsDB Premium ($9/mes)

---

## 🧪 Implementación Provisional (Gratis)

### Probar sistema AHORA con datos del Mundial 2022

#### Paso 1: Hacer Deploy del Código

```bash
# En tu máquina local
git add .
git commit -m "Agregar módulo Polla Mundial 2026"
git push origin main
```

Railway detectará el push y desplegará automáticamente.

#### Paso 2: Ejecutar Migraciones

**Opción A: SSH a Railway (Recomendado)**

```bash
# Instalar CLI de Railway (si no lo tienes)
npm install -g @railway/cli

# Login
railway login

# Conectar a tu proyecto
railway link

# Ejecutar migraciones
railway run python manage.py makemigrations employees
railway run python manage.py migrate
```

**Opción B: Agregar a `start.sh`**

El archivo [`start.sh`](start.sh) ya ejecuta migraciones automáticamente:

```bash
#!/bin/bash
# Ya existente - no modificar
python manage.py migrate
python manage.py configurar_evaluaciones_iniciales
python manage.py collectstatic --noinput

# Agregar al final (antes de gunicorn):
echo "🏆 Importando datos de Polla Mundial..."
python manage.py importar_partidos_mundial --season=2022 || echo "Partidos ya importados"
python manage.py actualizar_resultados_mundial || echo "Resultados ya actualizados"

# Iniciar servidor
exec gunicorn config.wsgi --bind 0.0.0.0:$PORT
```

**⚠️ IMPORTANTE:** Con la API gratuita, solo puedes hacer esto **UNA VEZ** debido al límite de 15 requests/mes.

#### Paso 3: Verificar en Producción

1. Abrir tu app: `https://tu-app.railway.app/empleados/polla-mundial/`
2. Ver admin: `https://tu-app.railway.app/admin/employees/partidomundial/`
3. Verificar que aparezcan los 64 partidos del Mundial 2022

---

## 🏆 Implementación Producción (Mundial 2026)

### Para cuando llegue el Mundial 2026 real

#### Paso 1: Configurar Variables de Entorno en Railway

1. **Dashboard Railway** → Tu servicio → **Variables**
2. Agregar nueva variable:
   ```
   Nombre: THESPORTSDB_API_KEY
   Valor: tu_api_key_premium_aqui
   ```
3. Click en **Add** y **Deploy**

#### Paso 2: Limpiar Datos de Prueba

**Opción A: Via Railway CLI**

```bash
# Conectar a shell de Django en producción
railway run python manage.py shell

# En el shell de Django:
from apps.employees.models import PartidoMundial, PrediccionMundial
PrediccionMundial.objects.all().delete()
PartidoMundial.objects.all().delete()
print("✅ Datos de prueba eliminados")
exit()
```

**Opción B: Via Admin de Django**

1. Ir a: `https://tu-app.railway.app/admin/employees/prediccionmundial/`
2. Seleccionar todas → Acción: Eliminar → Confirmar
3. Repetir con partidos en `/admin/employees/partidomundial/`

#### Paso 3: Importar Mundial 2026

```bash
# Via Railway CLI
railway run python manage.py importar_partidos_mundial --season=2026
```

**Salida esperada:**
```
Importando partidos del Mundial 2026...
✓ Usando API key Premium: 123456...
Se encontraron 104 partidos
✓ Creado: Mexico vs South Africa
...
=== Resumen ===
Partidos creados: 104
```

---

## ⏰ Configuración de Cron Jobs en Railway

Railway soporta **Cron Jobs nativos** para ejecutar tareas programadas.

### Opción 1: Servicio Cron Separado (Recomendado)

#### Paso 1: Crear archivo `railway.json`

Crear en la raíz del proyecto:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn config.wsgi --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### Paso 2: Crear servicio Cron en Railway

1. **Dashboard Railway** → **New Service** → **Empty Service**
2. Nombrar: `polla-mundial-cron`
3. **Settings** → **Start Command**:
   ```bash
   while true; do
     python manage.py actualizar_equipos_tbd
     python manage.py actualizar_resultados_mundial --verbose
     python manage.py importar_partidos_mundial --force
     sleep 1800  # 30 minutos = 1800 segundos
   done
   ```

4. **Variables**: Referenciar las mismas del servicio principal
   - `DATABASE_URL` → Referencia de Postgres
   - `THESPORTSDB_API_KEY` → Tu API key
   - Todas las demás variables necesarias

5. **Desplegar**

**Limitaciones:**
- ❌ Corre 24/7 (no puedes limitar horario fácilmente)
- ❌ Consume recursos continuamente

---

### Opción 2: GitHub Actions + Railway CLI (Mejor Control)

#### Paso 1: Crear workflow de GitHub

Crear `.github/workflows/actualizar-polla-mundial.yml`:

```yaml
name: Actualizar Polla Mundial

on:
  schedule:
    # Ejecutar cada 30 minutos entre 1 PM y 1 AM UTC-5
    # Ajustar según tu zona horaria
    - cron: '0,30 13-23 * * *'  # 1 PM - 11:59 PM
    - cron: '0,30 0-1 * * *'    # 12 AM - 1 AM
  workflow_dispatch:  # Permitir ejecución manual

jobs:
  actualizar:
    runs-on: ubuntu-latest

    # Solo ejecutar durante el Mundial (11 jun - 19 jul 2026)
    # Descomentar cuando llegue el momento:
    # if: ${{ github.event.schedule }} && ${{ github.event_name == 'schedule' }}

    steps:
      - name: Checkout código
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Railway CLI
        run: npm install -g @railway/cli

      - name: Actualizar equipos TBD
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          railway run python manage.py actualizar_equipos_tbd

      - name: Actualizar resultados
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          railway run python manage.py actualizar_resultados_mundial --verbose

      - name: Importar nuevos partidos
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          railway run python manage.py importar_partidos_mundial --force

      - name: Notificar resultado
        if: always()
        run: echo "Actualización completada - $(date)"
```

#### Paso 2: Configurar Secrets en GitHub

1. **GitHub** → Tu repositorio → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**:
   - Nombre: `RAILWAY_TOKEN`
   - Valor: Tu token de Railway (obtenerlo en Railway Dashboard → Account Settings → Tokens)
3. **Add secret**

#### Paso 3: Activar Workflow

```bash
# Hacer commit del workflow
git add .github/workflows/actualizar-polla-mundial.yml
git commit -m "Agregar workflow de actualización automática Polla Mundial"
git push origin main
```

**Verificar:**
- GitHub → Actions → Ver el workflow
- Puede ejecutarse manualmente con "Run workflow"

**Ventajas:**
- ✅ **Horario personalizable** (1 PM - 1 AM)
- ✅ **Ahorro del 50%** en API requests
- ✅ **Gratis** (GitHub Actions tiene minutos gratis)
- ✅ **No consume recursos de Railway** cuando no corre
- ✅ **Logs en GitHub** fáciles de revisar

---

### Opción 3: Servicio Externo de Cron (EasyCron, cron-job.org)

#### Paso 1: Crear endpoint web para actualización

Agregar a [`apps/employees/views_polla_mundial.py`](apps/employees/views_polla_mundial.py):

```python
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import os

@csrf_exempt
def webhook_actualizar_polla(request):
    """
    Webhook para actualización externa vía cron jobs
    URL: /empleados/polla-mundial/webhook/actualizar/
    """
    # Verificar token de seguridad
    token = request.GET.get('token') or request.POST.get('token')
    expected_token = os.getenv('POLLA_WEBHOOK_TOKEN', 'secreto_cambiar_esto')

    if token != expected_token:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        # Importar aquí para evitar circular imports
        from django.core.management import call_command

        # Ejecutar comandos
        call_command('actualizar_equipos_tbd')
        call_command('actualizar_resultados_mundial', '--verbose')
        call_command('importar_partidos_mundial', '--force')

        return JsonResponse({
            'success': True,
            'message': 'Actualización completada',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
```

Agregar ruta en [`apps/employees/urls.py`](apps/employees/urls.py):

```python
# Dentro de urlpatterns, en la sección de POLLA MUNDIALISTA
path('polla-mundial/webhook/actualizar/', views_polla_mundial.webhook_actualizar_polla, name='webhook_actualizar_polla'),
```

#### Paso 2: Configurar variable de entorno

Railway → Variables → Agregar:
```
POLLA_WEBHOOK_TOKEN=token_secreto_aleatorio_aqui_12345
```

#### Paso 3: Configurar cron externo

**EasyCron (Gratis hasta 100 jobs/mes):**

1. Registrarse: https://www.easycron.com/
2. Create Cron Job:
   - URL: `https://tu-app.railway.app/empleados/polla-mundial/webhook/actualizar/?token=token_secreto_aleatorio_aqui_12345`
   - Cron Expression: `0,30 13-23,0-1 * * *` (cada 30 min, 1 PM - 1 AM)
   - HTTP Method: GET
3. Save

**cron-job.org (Gratis, sin registro):**

1. Ir a: https://cron-job.org/
2. Create cronjob:
   - Title: Polla Mundial Actualización
   - URL: Tu URL con token
   - Schedule: Every 30 minutes
   - Timezone: Tu zona horaria
   - Active hours: 13:00 - 01:00
3. Create

---

## 📊 Comparativa de Opciones para Railway

| Opción | Complejidad | Costo | Control Horario | Logs | Recomendado |
|--------|-------------|-------|-----------------|------|-------------|
| **Servicio Cron Railway** | Baja | +$5/mes Railway | ❌ | Railway | ❌ |
| **GitHub Actions** | Media | $0 | ✅ | GitHub | ⭐ **SÍ** |
| **Webhook + EasyCron** | Media | $0 | ✅ | EasyCron | ✅ |
| **Manual via CLI** | Baja | $0 | ✅ Manual | Railway | Solo testing |

**Recomendación:** **GitHub Actions** por ser gratis, flexible y no consumir recursos de Railway.

---

## 📡 Monitoreo y Logs

### Ver Logs en Railway

```bash
# Via Railway CLI
railway logs --follow

# Filtrar por palabra clave
railway logs | grep "Polla Mundial"
railway logs | grep "Actualización"
```

### Ver Logs en GitHub Actions

1. GitHub → Actions → Workflow: "Actualizar Polla Mundial"
2. Click en última ejecución
3. Ver detalles de cada step

### Verificar Estado

```bash
# Via Railway CLI
railway run python manage.py shell

# En shell de Django:
from apps.employees.models import PartidoMundial, PrediccionMundial
from django.db.models import Sum

print(f"Total partidos: {PartidoMundial.objects.count()}")
print(f"Finalizados: {PartidoMundial.objects.filter(finalizado=True).count()}")
print(f"Predicciones: {PrediccionMundial.objects.count()}")
print(f"Puntos distribuidos: {PrediccionMundial.objects.aggregate(Sum('puntos_ganados'))['puntos_ganados__sum']}")
```

---

## 🐛 Troubleshooting

### Problema: Migraciones no se aplican automáticamente

**Solución:**
```bash
# Forzar migraciones via CLI
railway run python manage.py migrate --noinput
```

O agregar a `start.sh`:
```bash
python manage.py migrate --noinput --run-syncdb
```

### Problema: No se importan partidos (límite API)

**Causa:** API key gratuita (15 requests/mes)

**Solución:**
1. Configurar `THESPORTSDB_API_KEY` Premium en Railway Variables
2. Re-ejecutar: `railway run python manage.py importar_partidos_mundial --season=2026`

### Problema: GitHub Actions falla con "Not authenticated"

**Solución:**
1. Verificar que `RAILWAY_TOKEN` esté en GitHub Secrets
2. Obtener nuevo token: Railway → Account Settings → Tokens → Create Token
3. Actualizar secret en GitHub

### Problema: Webhook retorna 401 Unauthorized

**Solución:**
1. Verificar que `POLLA_WEBHOOK_TOKEN` esté configurado en Railway
2. Verificar que el token en la URL coincida
3. Revisar logs: `railway logs | grep "Unauthorized"`

### Problema: Comando tarda mucho y se timeout

**Solución:**
Ejecutar comandos de forma asincrónica:

```python
# En views_polla_mundial.py
from threading import Thread

def actualizar_async():
    call_command('actualizar_resultados_mundial')

@csrf_exempt
def webhook_actualizar_polla(request):
    # ... validaciones ...
    Thread(target=actualizar_async, daemon=True).start()
    return JsonResponse({'success': True, 'message': 'Actualizando en background'})
```

---

## ✅ Checklist de Deployment

### Implementación Provisional (Ahora)

- [ ] Hacer push del código
- [ ] Ejecutar migraciones: `railway run python manage.py migrate`
- [ ] Importar Mundial 2022: `railway run python manage.py importar_partidos_mundial --season=2022`
- [ ] Verificar en web: `https://tu-app.railway.app/empleados/polla-mundial/`
- [ ] Comunicar a empleados

### Implementación Producción (Mundial 2026)

- [ ] Contratar TheSportsDB Premium
- [ ] Configurar `THESPORTSDB_API_KEY` en Railway Variables
- [ ] Limpiar datos de prueba
- [ ] Importar Mundial 2026: `railway run python manage.py importar_partidos_mundial --season=2026`
- [ ] Configurar GitHub Actions (o alternativa de cron)
- [ ] Probar ejecución manual del workflow
- [ ] Activar schedule para junio 2026
- [ ] Monitorear logs primeros días

---

## 📖 Documentación Relacionada

- [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Deployment general en Railway
- [GUIA_API_PREMIUM_MUNDIAL.md](GUIA_API_PREMIUM_MUNDIAL.md) - Configuración API Premium
- [IMPLEMENTACION_PROVISIONAL.md](IMPLEMENTACION_PROVISIONAL.md) - Pruebas con Mundial 2022
- [OPTIMIZACION_API_MUNDIAL.md](OPTIMIZACION_API_MUNDIAL.md) - Ahorro del 50%

---

**¿Listo para deployment? Empieza con la implementación provisional para probar todo sin costo! 🚀⚽**
