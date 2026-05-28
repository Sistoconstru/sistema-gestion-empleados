# 🏆 Guía de Implementación: Polla Mundial con TheSportsDB Premium

## 📋 Índice
1. [Configuración Inicial](#configuración-inicial)
2. [Instalación de Dependencias](#instalación-de-dependencias)
3. [Obtener API Key Premium](#obtener-api-key-premium)
4. [Configurar Variables de Entorno](#configurar-variables-de-entorno)
5. [Importar Fixture del Mundial](#importar-fixture-del-mundial)
6. [Configurar Actualización Automática](#configurar-actualización-automática)
7. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
8. [Costos y Presupuesto](#costos-y-presupuesto)

---

## 🚀 Configuración Inicial

### 1. Instalar Dependencias

```bash
# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar requests (si no está instalado)
pip install requests

# Crear migraciones
python manage.py makemigrations employees

# Aplicar migraciones
python manage.py migrate
```

---

## 🔑 Obtener API Key Premium

### Paso 1: Registrarse en TheSportsDB

1. Ir a: https://www.thesportsdb.com/pricing
2. Seleccionar plan **"Patreon Supporter"** - $9/mes USD
3. Crear cuenta en Patreon
4. Vincular cuenta con TheSportsDB

### Paso 2: Obtener tu API Key

1. Iniciar sesión en: https://www.thesportsdb.com/
2. Ir a **"API Keys"** en tu perfil
3. Copiar tu **API Key Premium** (formato: `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)

### Beneficios del Plan Premium

✅ **3000 requests/mes** para `eventsseason.php` (vs 15 free)
✅ **Sin límite** para `lookupevent.php` (vs 1/mes free)
✅ **100 requests/minuto** (vs 30 free)
✅ **Livescores cada 2 minutos** (tiempo real)
✅ **Acceso a V2 API** (más moderna)
✅ **Video highlights** y metadata adicional

---

## ⚙️ Configurar Variables de Entorno

### Editar archivo `.env`

Abre el archivo [`.env`](.env) en la raíz del proyecto y reemplaza:

```env
# =============================================================================
# POLLA MUNDIAL - TheSportsDB API Premium
# =============================================================================
THESPORTSDB_API_KEY=TU_API_KEY_PREMIUM_AQUI
```

Por tu API key real:

```env
# =============================================================================
# POLLA MUNDIAL - TheSportsDB API Premium
# =============================================================================
THESPORTSDB_API_KEY=123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

**⚠️ IMPORTANTE:** Nunca compartas tu API key públicamente ni la subas a repositorios públicos.

---

## 📥 Importar Fixture del Mundial

### Importación Inicial

```bash
# Importar todos los partidos del Mundial 2026
python manage.py importar_partidos_mundial --season=2026

# Salida esperada:
# Importando partidos del Mundial 2026...
# ✓ Usando API key Premium: 123456...
# Consultando: https://www.thesportsdb.com/api/v1/json/YOUR_KEY/eventsseason.php?id=4429&s=2026
# Se encontraron 104 partidos
# ✓ Creado: Mexico vs South Africa
# ✓ Creado: USA vs Canada
# ...
# === Resumen ===
# Partidos creados: 104
# Partidos actualizados: 0
```

### Actualizar Fixture (si hay cambios)

```bash
# Forzar actualización de partidos existentes
python manage.py importar_partidos_mundial --season=2026 --force
```

### ¿Qué pasa si el Mundial 2026 aún no está disponible en la API?

Si ejecutas el comando y recibes:

```
No se encontraron partidos para esta temporada
Nota: Los partidos del Mundial 2026 pueden no estar disponibles aún en la API
```

**Opciones:**

1. **Esperar** a que TheSportsDB agregue los datos (usualmente 3-6 meses antes del torneo)
2. **Cargar manualmente** los partidos desde el Admin de Django
3. **Usar fixture de prueba** con el Mundial 2022 o 2018 para testing:
   ```bash
   python manage.py importar_partidos_mundial --season=2022
   ```

---

## ⏰ Configurar Actualización Automática

### Opción A: Windows (Programador de Tareas)

#### Paso 1: Crear Tarea Programada

1. Abrir **"Programador de Tareas"** (Task Scheduler)
2. Clic derecho en **"Biblioteca del Programador de Tareas"**
3. Seleccionar **"Crear tarea..."**

#### Paso 2: Configurar Tarea

**Pestaña General:**
- Nombre: `Actualizar Polla Mundial`
- Descripción: `Actualiza resultados cada 30 minutos durante el Mundial`
- Usuario: Tu usuario actual
- ✅ **Ejecutar aunque el usuario no haya iniciado sesión**

**Pestaña Desencadenadores:**
- Clic en **"Nuevo..."**
- Iniciar la tarea: **Una vez**
- Fecha inicio: Día que empieza el Mundial (ej: 11/06/2026)
- Hora: 12:00:00
- ✅ **Repetir cada:** 30 minutos
- **Durante:** 1 día
- ✅ **Habilitado**

**Pestaña Acciones:**
- Acción: **Iniciar un programa**
- Programa/script: `C:\ruta\completa\al\proyecto\actualizar_polla_mundial.bat`
- Iniciar en: `C:\ruta\completa\al\proyecto\`

**Pestaña Condiciones:**
- ❌ Desmarcar **"Iniciar solo si el equipo está conectado a la alimentación de CA"**
- ✅ Marcar **"Activar si la conexión de red está disponible"**

**Pestaña Configuración:**
- ✅ **Permitir que se ejecute a petición**
- ✅ **Ejecutar tarea lo antes posible después de un inicio programado perdido**

#### Paso 3: Probar Ejecución Manual

1. Buscar tu tarea en la lista
2. Clic derecho → **"Ejecutar"**
3. Verificar el log en: `logs/polla_mundial_updates.log`

---

### Opción B: Linux/Mac (Crontab)

#### Paso 1: Editar Crontab

```bash
# Abrir editor de crontab
crontab -e
```

#### Paso 2: Agregar Línea de Ejecución

```bash
# Actualizar Polla Mundial cada 30 minutos durante el torneo
# (Activar solo durante el Mundial - junio/julio 2026)
*/30 * * * * /ruta/completa/al/proyecto/actualizar_polla_mundial.sh >> /ruta/completa/al/proyecto/logs/cron.log 2>&1
```

**Ejemplo real:**

```bash
*/30 * * * * /home/usuario/gestion_empleados/actualizar_polla_mundial.sh >> /home/usuario/gestion_empleados/logs/cron.log 2>&1
```

#### Paso 3: Verificar Crontab

```bash
# Listar tareas programadas
crontab -l

# Verificar log
tail -f /ruta/completa/al/proyecto/logs/cron.log
```

#### Paso 4: Desactivar Después del Mundial

```bash
# Editar crontab
crontab -e

# Comentar la línea con #
# */30 * * * * /ruta/completa/al/proyecto/actualizar_polla_mundial.sh

# O eliminar la línea completamente
```

---

## 🔍 Monitoreo y Mantenimiento

### Comandos Manuales Útiles

```bash
# Actualizar solo resultados (sin importar nuevos partidos)
python manage.py actualizar_resultados_mundial

# Actualizar con información detallada
python manage.py actualizar_resultados_mundial --verbose

# Recalcular puntos de todas las predicciones
python manage.py actualizar_resultados_mundial --recalcular

# Actualizar equipos TBD (fase eliminatoria)
python manage.py actualizar_equipos_tbd

# Importar partidos de otra temporada (para testing)
python manage.py importar_partidos_mundial --season=2022
```

### Verificar Estado de Sincronización

Crear un comando de verificación:

```bash
python manage.py shell

# En el shell de Django:
from apps.employees.models import PartidoMundial, PrediccionMundial

# Total de partidos
print(f"Total partidos: {PartidoMundial.objects.count()}")

# Partidos finalizados
print(f"Finalizados: {PartidoMundial.objects.filter(finalizado=True).count()}")

# Partidos pendientes
print(f"Pendientes: {PartidoMundial.objects.filter(finalizado=False).count()}")

# Predicciones totales
print(f"Predicciones: {PrediccionMundial.objects.count()}")

# Partidos con equipos TBD
print(f"Partidos TBD: {PartidoMundial.objects.filter(equipo_local__icontains='TBD').count()}")
```

### Logs de Actualización

Los scripts generan logs en:

```
logs/polla_mundial_updates.log
logs/cron.log (Linux/Mac)
```

**Ver últimas actualizaciones:**

```bash
# Windows
type logs\polla_mundial_updates.log

# Linux/Mac
tail -f logs/polla_mundial_updates.log
```

---

## 💰 Costos y Presupuesto

### ⚡ Optimización Disponible

💡 **NUEVO:** Puedes reducir costos al 50% limitando actualizaciones a horario 1 PM - 1 AM

📖 **Ver:** [OPTIMIZACION_API_MUNDIAL.md](OPTIMIZACION_API_MUNDIAL.md) para detalles completos

| Opción | Costo | Requests | Scripts |
|--------|-------|----------|---------|
| **Optimizado (1PM-1AM)** ⭐ | **$9 (1 mes)** | 2,808 | `actualizar_polla_mundial_horario.bat/.sh` |
| Sin optimizar (24/7) | $18 (2 meses) | 5,616 | `actualizar_polla_mundial.bat/.sh` |

### Plan Estándar: 2 Meses (Sin Optimización)

**Costo Total: $18 USD**

| Concepto | Costo Mensual | Duración | Total |
|----------|---------------|----------|-------|
| TheSportsDB Premium | $9/mes | 2 meses | $18 |

### Calendario de Suscripción

**Mundial 2026: 11 junio - 19 julio (39 días)**

#### Opción 1: Suscripción Exacta
- **Mes 1:** 1 junio - 30 junio ($9)
- **Mes 2:** 1 julio - 19 julio ($9)
- **Total:** $18 USD
- **Cancelar:** 20 julio 2026

#### Opción 2: Con Margen
- **Mes 1:** 15 mayo - 14 junio ($9) - Para preparar y probar
- **Mes 2:** 15 junio - 14 julio ($9)
- **Mes 3:** 15 julio - 31 julio ($9) - Por si hay repechajes/extra
- **Total:** $27 USD

### Consumo Estimado de API

**Durante todo el Mundial (39 días):**

| Operación | Frecuencia | Total Requests |
|-----------|------------|----------------|
| Importar fixture inicial | 1 vez | 1 |
| Actualizar resultados | Cada 30 min × 48 veces/día × 39 días | ~1,872 |
| Actualizar equipos TBD | Cada 30 min × 48 veces/día × 10 días | ~480 |
| Importar nuevos partidos | Cada 30 min × 48 veces/día × 39 días | ~1,872 |
| **TOTAL** | | **~4,225 requests** |

**Límite Premium:** 3,000 requests/mes

⚠️ **ADVERTENCIA:** Con 4,225 requests totales en 2 meses, estarás dentro del límite si distribuyes bien:
- **Mes 1 (junio):** ~2,500 requests ✅
- **Mes 2 (julio):** ~1,725 requests ✅

### Optimización de Costos

Para reducir consumo de API:

1. **Actualizar solo durante partidos:**
   - Activar tarea programada solo días de partido
   - Desactivar en días sin partidos

2. **Reducir frecuencia:**
   - Cambiar de 30 min a 60 min entre actualizaciones
   - Reduce consumo a ~2,100 requests

3. **Actualización manual post-partidos:**
   - Desactivar tarea automática
   - Ejecutar manualmente después de cada jornada
   - Reduce a ~100-150 requests totales

---

## 📊 Resumen de Archivos Creados

### Scripts de Automatización
- ✅ [`actualizar_polla_mundial.bat`](actualizar_polla_mundial.bat) - Script Windows
- ✅ [`actualizar_polla_mundial.sh`](actualizar_polla_mundial.sh) - Script Linux/Mac

### Comandos Django
- ✅ [`importar_partidos_mundial.py`](apps/employees/management/commands/importar_partidos_mundial.py)
- ✅ [`actualizar_resultados_mundial.py`](apps/employees/management/commands/actualizar_resultados_mundial.py)
- ✅ [`actualizar_equipos_tbd.py`](apps/employees/management/commands/actualizar_equipos_tbd.py)

### Configuración
- ✅ [`.env`](.env) - Variables de entorno (API key)

### Documentación
- ✅ [`POLLA_MUNDIAL_README.md`](POLLA_MUNDIAL_README.md) - Documentación general
- ✅ [`GUIA_API_PREMIUM_MUNDIAL.md`](GUIA_API_PREMIUM_MUNDIAL.md) - Esta guía

---

## ✅ Checklist de Implementación

Antes del Mundial 2026:

- [ ] Contratar plan Premium de TheSportsDB ($9/mes)
- [ ] Configurar `THESPORTSDB_API_KEY` en `.env`
- [ ] Ejecutar migraciones: `python manage.py migrate`
- [ ] Importar fixture: `python manage.py importar_partidos_mundial --season=2026`
- [ ] Configurar tarea programada (Windows o Linux)
- [ ] Probar actualización manual
- [ ] Verificar logs de sincronización
- [ ] Comunicar a empleados que ya pueden hacer predicciones

Durante el Mundial:

- [ ] Monitorear logs diariamente
- [ ] Verificar que se actualicen resultados
- [ ] Revisar ranking después de cada jornada
- [ ] Responder dudas de empleados

Después del Mundial:

- [ ] Cancelar suscripción Premium de TheSportsDB
- [ ] Desactivar tarea programada
- [ ] Exportar ranking final (opcional)
- [ ] Premiar a los ganadores 🏆
- [ ] Archivar o eliminar módulo (ver [POLLA_MUNDIAL_README.md](POLLA_MUNDIAL_README.md))

---

## 🆘 Soporte y Troubleshooting

### Problema: No se importan partidos

**Causas posibles:**
- Mundial 2026 aún no está en la API
- API key incorrecta
- Sin conexión a internet

**Solución:**
```bash
# Verificar API key
echo %THESPORTSDB_API_KEY%  # Windows
echo $THESPORTSDB_API_KEY   # Linux

# Probar con Mundial anterior
python manage.py importar_partidos_mundial --season=2022
```

### Problema: No se actualizan resultados

**Causas posibles:**
- Tarea programada desactivada
- Partidos sin `api_id`
- Límite de requests excedido

**Solución:**
```bash
# Ejecutar manualmente con verbose
python manage.py actualizar_resultados_mundial --verbose

# Verificar logs
type logs\polla_mundial_updates.log  # Windows
tail logs/polla_mundial_updates.log  # Linux
```

### Problema: Equipos TBD no se actualizan

**Causa:**
- Fase eliminatoria aún no se ha jugado

**Solución:**
```bash
# Ejecutar actualización de TBD
python manage.py actualizar_equipos_tbd

# O esperar a que se jueguen los partidos de clasificación
```

---

## 📞 Contacto

Para dudas o problemas, consultar:
- Documentación oficial: https://www.thesportsdb.com/documentation
- Foro de soporte: https://www.thesportsdb.com/forum

---

**¡Listo! Tu Polla Mundial está configurada para actualizarse automáticamente. ⚽🏆**
