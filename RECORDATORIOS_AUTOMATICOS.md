# 📬 Sistema de Recordatorios Automáticos de Evaluaciones

## 📋 Descripción

Sistema inteligente que envía recordatorios automáticos cuando las evaluaciones llevan varios días en estado **pendiente** sin iniciarse.

## 🎯 Características

- ✅ **No sobrecarga el sistema**: Se ejecuta como comando programado
- ✅ **Inteligente**: Verifica la última notificación antes de enviar
- ✅ **Configurable**: Días de umbral personalizables
- ✅ **Evita spam**: No envía recordatorios duplicados
- ✅ **Modo simulación**: Prueba sin enviar notificaciones reales
- ✅ **Sin costos adicionales**: Usa APScheduler existente en Railway

## 🚀 Comandos Disponibles

### 1. Configurar Tipos de Notificación (Solo una vez)

```bash
python manage.py configurar_notificaciones_evaluaciones
```

Crea 7 tipos de notificación:
- `evaluacion_asignada` - Notificación inicial al asignar evaluación
- `evaluacion_para_evaluar` - Notificación al evaluador
- `plan_mejora_asignado` - Plan de mejora generado
- `seguimiento_pendiente` - Seguimiento bimensual pendiente
- `evaluacion_final_pendiente` - Evaluación final por aceptar
- `evaluacion_final_rechazada` - Rechazada, requiere RRHH
- `recordatorio_evaluacion` - **Recordatorio automático** ⭐

### 2. Generar Notificaciones Retroactivas (Una vez)

```bash
python manage.py generar_notificaciones_evaluaciones_existentes
```

Crea notificaciones para evaluaciones ya asignadas que están pendientes.

### 3. Enviar Recordatorios (Ejecutar automáticamente)

```bash
# Modo normal (3 días de umbral)
python manage.py enviar_recordatorios_evaluaciones

# Modo simulación (ver qué haría sin enviar)
python manage.py enviar_recordatorios_evaluaciones --dry-run

# Umbral personalizado (ejemplo: 5 días)
python manage.py enviar_recordatorios_evaluaciones --dias 5

# Simulación con umbral personalizado
python manage.py enviar_recordatorios_evaluaciones --dry-run --dias 7
```

## ⚙️ Cómo Funciona

1. **Busca evaluaciones pendientes** en estado `pendiente`
2. **Verifica última notificación** del empleado para esa evaluación
3. **Calcula días transcurridos** desde la última notificación
4. **Si >= 3 días**: Envía recordatorio al empleado Y al evaluador
5. **Si < 3 días**: Omite (evita spam)

### Ejemplo de Flujo

```
Día 0:  Evaluación asignada → Notificación inicial ✉️
Día 1:  No hace nada (solo 1 día)
Día 2:  No hace nada (solo 2 días)
Día 3:  Envía recordatorio ✉️ (han pasado 3 días)
Día 4:  No hace nada (último recordatorio hace 1 día)
Día 5:  No hace nada (último recordatorio hace 2 días)
Día 6:  Envía recordatorio ✉️ (han pasado 3 días desde último)
```

## 🕐 Ejecución Automática con APScheduler

### En Producción (Railway)

El sistema **ya está configurado** para ejecutarse automáticamente a las **4:00 AM** todos los días en producción.

**Configuración en `apps/core/scheduler.py`:**
```python
# Tarea 4: Enviar recordatorios de evaluaciones pendientes a las 4:00 AM
scheduler.add_job(
    _enviar_recordatorios_evaluaciones,
    'cron',
    hour=4,
    minute=0,
    id='recordatorios_evaluaciones',
    name='Enviar recordatorios de evaluaciones pendientes',
    replace_existing=True,
    misfire_grace_time=600,
    coalesce=True,
)
```

**El scheduler se inicia automáticamente con:**
```bash
python manage.py start_scheduler --daemon
```

### En Desarrollo Local

El scheduler también funciona localmente. Puedes:

1. **Iniciar el scheduler manualmente:**
```bash
python manage.py start_scheduler
```

2. **O ejecutar el comando manualmente cuando necesites probar:**
```bash
python manage.py enviar_recordatorios_evaluaciones --dias 1
```

## 📊 Monitoreo

### Ver logs del scheduler

Los logs se guardan automáticamente en `logs/scheduler.log`:

```bash
# Ver últimas líneas
tail -f logs/scheduler.log

# Buscar ejecuciones de recordatorios
grep "recordatorios" logs/scheduler.log
```

### Verificar en Django Admin

1. Ir a `/admin/notifications/notificacion/`
2. Filtrar por tipo: "Recordatorio - Evaluación Pendiente"
3. Ver notificaciones enviadas y fechas

## 🧪 Pruebas

### Prueba inicial (simulación)
```bash
# Ver qué haría sin enviar nada
python manage.py enviar_recordatorios_evaluaciones --dry-run --dias 0
```

### Prueba real con umbral bajo
```bash
# Enviar recordatorios (solo si hay evaluaciones pendientes hace 1+ día)
python manage.py enviar_recordatorios_evaluaciones --dias 1
```

### Verificar en la base de datos
```bash
python manage.py shell
>>> from apps.notifications.models import Notificacion
>>> Notificacion.objects.filter(tipo_notificacion__codigo='recordatorio_evaluacion').count()
4  # Ejemplo: 4 recordatorios enviados
```

## 🛠️ Solución de Problemas

### Problema: No se envían recordatorios

**Verificar que el scheduler está corriendo:**
```bash
# En Railway, verificar logs del servicio web
railway logs

# Buscar: "🔄 Iniciando envío de recordatorios de evaluaciones..."
```

**Verificar que el tipo de notificación existe:**
```bash
python manage.py configurar_notificaciones_evaluaciones
```

**Verificar que hay evaluaciones pendientes:**
```bash
python manage.py shell
>>> from apps.evaluations.models import AsignacionEvaluacion
>>> AsignacionEvaluacion.objects.filter(estado='pendiente').count()
```

### Problema: Se envían demasiados recordatorios

**Modificar el umbral en `apps/core/scheduler.py`:**
```python
# Cambiar de 3 a 7 días
call_command('enviar_recordatorios_evaluaciones', '--dias', '7')
```

### Problema: El scheduler no inicia

**Verificar que start.sh ejecuta el scheduler:**
```bash
cat start.sh | grep scheduler
```

Debería mostrar:
```bash
python manage.py start_scheduler --daemon > /dev/null 2>&1 &
```

## 📈 Recomendaciones

1. **Horario**: **4:00 AM** (madrugada, sin usuarios conectados) ⭐
2. **Umbral**: Usar **3 días** para evitar spam
3. **Monitoreo**: Revisar logs semanalmente en Railway
4. **Testing**: Probar con `--dry-run` antes de modificar configuración
5. **Producción**: APScheduler ya está configurado y funcionando

## 📝 Ejemplo de Salida

```
=== Enviando Recordatorios de Evaluaciones Pendientes ===
Umbral de días sin actividad: 3 días

Evaluaciones en estado PENDIENTE: 5

  [Juan Pérez] - Evaluación Anual 2025
    Última actividad: hace 4 días (inicial)
    [+] Recordatorio enviado al empleado
    [+] Recordatorio enviado al evaluador

  [María García] - Evaluación Trimestral
    Última actividad: hace 7 días (recordatorio)
    [+] Recordatorio enviado al empleado
    [+] Recordatorio enviado al evaluador

=== Proceso Completado ===
  - Evaluaciones pendientes: 5
  - Recordatorios a empleados: 2
  - Recordatorios a evaluadores: 2
  - Omitidas (notificación reciente): 3
  - Omitidas (sin usuario): 0

  TOTAL RECORDATORIOS ENVIADOS: 4
```

## 🔗 Comandos Relacionados

| Comando | Propósito | Frecuencia |
|---------|-----------|------------|
| `configurar_notificaciones_evaluaciones` | Crear tipos de notificación | Una vez |
| `generar_notificaciones_evaluaciones_existentes` | Notificaciones retroactivas | Una vez |
| `enviar_recordatorios_evaluaciones` | Recordatorios automáticos | **Automático (4:00 AM)** ⭐ |

## 💡 Notas Importantes

- ⚠️ Las evaluaciones en estado `en_progreso` o `completada` NO reciben recordatorios
- ⚠️ Solo se envían recordatorios a usuarios que tengan cuenta activa
- ⚠️ El sistema verifica automáticamente la última notificación para evitar spam
- ⚠️ Usar `--dry-run` para probar cambios sin enviar notificaciones reales
- ✅ **Sin costos adicionales**: Usa APScheduler que ya estaba configurado en Railway
- ✅ **Ejecución garantizada**: APScheduler se inicia automáticamente con `start.sh`

## 🎯 Tareas del Scheduler (apps/core/scheduler.py)

El scheduler ejecuta automáticamente estas 4 tareas:

1. **2:00 AM** - Asignar evaluaciones de período de prueba
2. **2:15 AM** - Activar empleados después de período de prueba
3. **3:00 AM** (día 1 del mes) - Limpiar logs de auditoría antiguos
4. **4:00 AM** - Enviar recordatorios de evaluaciones pendientes ⭐ **NUEVO**
