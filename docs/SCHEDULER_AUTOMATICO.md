# Scheduler Automático de Evaluaciones

## Descripción

El scheduler automático ejecuta tareas programadas dentro de la aplicación Django para gestionar las evaluaciones de período de prueba sin necesidad de scripts externos o tareas del sistema operativo.

## Características

- ✅ **Asignación automática** de evaluaciones a los 30 días de servicio
- ✅ **Validación** para evitar duplicados
- ✅ **Activación automática** de empleados después de 60+ días
- ✅ **Ejecución programada** a horas de bajo tráfico (02:00 AM)
- ✅ **Logs detallados** para auditoría y monitoreo
- ✅ **Manejo de errores** robusto y seguro

## Tareas Programadas

### 1. Asignación de Evaluaciones (02:00 AM)

**Nombre:** Asignar evaluaciones de período de prueba

**Lógica:**
1. Busca empleados en estado `p-prue` con 30-60 días de servicio
2. Verifica que no tengan evaluación ya asignada para el período
3. Obtiene el jefe directo desde `HistorialCargo.jefe_directo`
4. Crea la asignación de evaluación con vencimiento de 15 días
5. Registra la acción en logs para auditoría

**Requisitos:**
- Empleado en estado "período de prueba" (`p-prue`)
- 30-60 días desde la fecha de ingreso
- No tener evaluación asignada para ese período
- Tener jefe directo asignado y activo

**Salida esperada:**
```
Encontrados 3 empleados elegibles para evaluación:

- Andres Andes (Doc: 1035212554211)
  Fecha ingreso: 2025-10-22 (33 días transcurridos)
  Sede: CO-0001 - Caldas
  Jefe directo: Bernardo Marin
  [OK] Evaluacion asignada - Vence: 2025-12-09

- Juan Perez (Doc: 12345678)
  [!] Ya tiene evaluacion asignada - NO SE CREARA OTRA

- Maria Garcia (Doc: 87654321)
  [!] No se encontro jefe directo - NO SE ASIGNARA

============================================================
RESUMEN DE ASIGNACIONES:
[OK] Evaluaciones asignadas: 1
[!] Ya tenian evaluacion: 1
[!] Sin jefe directo: 1
============================================================
```

### 2. Activación de Empleados (02:15 AM)

**Nombre:** Activar empleados de período de prueba

**Lógica:**
1. Busca empleados en estado `p-prue` con más de 60 días de servicio
2. Verifica que tengan evaluación de período de prueba completada
3. Valida que el puntaje sea satisfactorio (> 13/21 puntos)
4. Cambia el estado a ACTIVO ("999")
5. Registra la acción en logs

**Requisitos:**
- Empleado en estado "período de prueba" (`p-prue`)
- 60+ días desde la fecha de ingreso
- Evaluación de período de prueba completada
- Puntaje total > 13 puntos (aprobado)

**Salida esperada:**
```
Encontrados 2 empleados para activar:

- Juan Pérez (Doc: 123456789)
  Fecha ingreso: 2025-08-15 (101 días transcurridos)
  Sede: CO-0001 - Caldas
  Evaluación satisfactoria (18/21 puntos) - PROCEDE ACTIVACIÓN
  Activado exitosamente

- María García (Doc: 987654321)
  Fecha ingreso: 2025-08-20 (96 días transcurridos)
  Sede: CO-0002 - Bogotá
  Evaluación insatisfactoria (12/21 puntos) - NO SE ACTIVARÁ

============================================================
RESUMEN DE ACTIVACIONES:
[OK] Empleados activados: 1
[!] Sin evaluación/pendiente: 0
[ERROR] Evaluación insatisfactoria: 1
============================================================
```

## Iniciar el Scheduler

### Opción 1: Iniciar manualmente (una vez)

```bash
python manage.py start_scheduler
```

El scheduler se ejecutará en segundo plano mientras Django esté activo.

### Opción 2: Auto-inicio automático

El scheduler se inicia automáticamente cuando Django inicia (excepto durante migraciones o tests):

1. Django carga el archivo `apps/core/apps.py`
2. Se ejecuta `CoreConfig.ready()`
3. El scheduler se inicia automáticamente en `_iniciar_scheduler_automatico()`

**Nota:** Para evitar inicios duplicados, el auto-inicio se desactiva si:
- Se está ejecutando `manage.py` directamente
- Se están ejecutando migraciones (`migrate`)
- Se están ejecutando tests (`test`)
- Se están creando migraciones (`makemigrations`)

## Ver Estado del Scheduler

```bash
python manage.py start_scheduler --status
```

Muestra:
- Estado actual (EJECUTÁNDOSE o DETENIDO)
- Próximas ejecuciones programadas
- Hora exacta de la siguiente ejecución

**Ejemplo de salida:**
```
============================================================
ESTADO DEL SCHEDULER
============================================================
[OK] Estado: EJECUTANDOSE

Proximas ejecuciones:
  - Asignar evaluaciones de período de prueba
    Proxima ejecucion: 2025-11-27 02:00:00
  - Activar empleados de período de prueba
    Proxima ejecucion: 2025-11-27 02:15:00
============================================================
```

## Monitoreo y Logs

### Ubicación de Logs

Todos los eventos del scheduler se registran en: **`logs/django.log`**

### Qué se registra

**Asignación de Evaluaciones:**
- Inicio de la tarea
- Empleados encontrados y procesados
- Asignaciones exitosas
- Empleados sin jefe directo
- Empleados con evaluación duplicada
- Errores técnicos

**Activación de Empleados:**
- Inicio de la tarea
- Empleados procesados
- Activaciones exitosas
- Empleados sin evaluación/pendientes
- Empleados con evaluación insatisfactoria
- Errores técnicos

### Ejemplos de Logs

```
INFO 2025-11-26 02:00:01,041 scheduler Iniciando asignación de evaluaciones de período de prueba...
INFO 2025-11-26 02:00:15,523 evaluations Evaluación de período de prueba asignada a 1035212554211 (Andres Andes)
INFO 2025-11-26 02:00:18,892 scheduler Asignación de evaluaciones completada
INFO 2025-11-26 02:15:01,041 scheduler Iniciando activación de empleados de período de prueba...
INFO 2025-11-26 02:15:22,156 evaluations Empleado 123456789 (Juan Pérez) activado automáticamente
INFO 2025-11-26 02:15:25,789 scheduler Activación de empleados completada
```

## Arquitectura

### Archivos Relacionados

```
apps/
├── core/
│   ├── apps.py                          # Auto-inicio del scheduler
│   ├── scheduler.py                     # Configuración principal
│   └── management/
│       └── commands/
│           └── start_scheduler.py       # Command para iniciar/ver estado
├── employees/
│   └── management/
│       └── commands/
│           └── activar_empleados_prueba.py    # Lógica de activación
└── evaluations/
    └── management/
        └── commands/
            └── asignar_evaluaciones_periodo_prueba.py  # Lógica de asignación
```

### Flujo de Ejecución

```
Django Inicia
    ↓
CoreConfig.ready() se ejecuta
    ↓
_iniciar_scheduler_automatico()
    ↓
Verifica si es un comando de manage.py que debe saltar
    ↓
start_scheduler() - Crea BackgroundScheduler de APScheduler
    ↓
Añade dos tareas cron:
    ├─ 02:00 AM: _asignar_evaluaciones_periodo_prueba()
    │   └─ Ejecuta: asignar_evaluaciones_periodo_prueba command
    │
    └─ 02:15 AM: _activar_empleados_prueba()
        └─ Ejecuta: activar_empleados_prueba command

Scheduler se ejecuta en background
    ↓
En las horas programadas, ejecuta las tareas
    ↓
Los resultados se registran en logs/django.log
```

## Configuración

### Cambiar Horario de Ejecución

Edita `apps/core/scheduler.py` en la función `start_scheduler()`:

```python
# Para cambiar la hora de asignación de evaluaciones (actualmente 02:00 AM)
scheduler.add_job(
    _asignar_evaluaciones_periodo_prueba,
    'cron',
    hour=6,          # Cambiar a 6:00 AM
    minute=0,
    id='asignar_evaluaciones',
    # ... resto de parámetros
)

# Para cambiar la hora de activación (actualmente 02:15 AM)
scheduler.add_job(
    _activar_empleados_prueba,
    'cron',
    hour=6,          # Cambiar a 6:15 AM
    minute=15,
    id='activar_empleados',
    # ... resto de parámetros
)
```

### Cambiar Rango de Días para Asignación

La asignación actualmente busca empleados con **30-60 días**. Para cambiar esto, edita `apps/core/scheduler.py`:

```python
def _asignar_evaluaciones_periodo_prueba():
    call_command(
        'asignar_evaluaciones_periodo_prueba',
        '--dias-minimos', '25',    # Cambiar a 25 días mínimo
        '--dias-maximos', '65'     # Cambiar a 65 días máximo
    )
```

### Cambiar Umbral de Días para Activación

La activación actualmente requiere **60+ días**. Para cambiar esto, edita `apps/core/scheduler.py`:

```python
def _activar_empleados_prueba():
    call_command(
        'activar_empleados_prueba',
        '--dias-periodo', '45'     # Cambiar a 45 días
    )
```

## Solución de Problemas

### El scheduler no se inicia automáticamente

**Causa probable:** Está desactivado por ser un comando de `manage.py`

**Solución:** Ejecuta manualmente:
```bash
python manage.py start_scheduler
```

O verifica que Django esté corriendo como servidor web (gunicorn, uwsgi, etc.), no como `manage.py runserver`

### No se asignan evaluaciones aunque hay empleados elegibles

**Checklist:**

1. ✅ Verificar que empleados estén en estado `p-prue`
   ```bash
   python manage.py shell
   >>> from apps.employees.models import Empleado
   >>> Empleado.objects.filter(estado__codigo='p-prue')
   ```

2. ✅ Verificar que tengan 30-60 días
   ```bash
   >>> from django.utils import timezone
   >>> from datetime import timedelta
   >>> fecha_hoy = timezone.now().date()
   >>> empleados = Empleado.objects.filter(
   ...     estado__codigo='p-prue',
   ...     fecha_ingreso__gte=fecha_hoy - timedelta(days=60),
   ...     fecha_ingreso__lte=fecha_hoy - timedelta(days=30)
   ... )
   >>> empleados.count()
   ```

3. ✅ Verificar que tengan jefe directo
   ```bash
   >>> for emp in empleados:
   ...     print(f"{emp.nombre_completo}: {emp.historialcargo_set.filter(activo=True).first().jefe_directo}")
   ```

4. ✅ Revisar logs para errores
   ```bash
   tail -f logs/django.log | grep -i evaluacion
   ```

### No se activan empleados aunque cumplen 60 días

**Checklist:**

1. ✅ Verificar que evaluación esté completada
   ```bash
   >>> from apps.evaluations.models import AsignacionEvaluacion
   >>> AsignacionEvaluacion.objects.filter(
   ...     empleado_evaluado=empleado,
   ...     estado='completada'
   ... ).exists()
   ```

2. ✅ Verificar puntaje
   ```bash
   >>> asignacion = AsignacionEvaluacion.objects.filter(
   ...     empleado_evaluado=empleado,
   ...     estado='completada'
   ... ).first()
   >>> asignacion.puntaje_total
   ```

3. ✅ Revisar logs
   ```bash
   tail -f logs/django.log | grep -i "activacion\|activada"
   ```

## Mejoras Futuras

### Posibles optimizaciones:

1. **Celery + Redis** - Para entornos con múltiples servidores
2. **Dashboard en Admin** - Ver estado y logs desde Django admin
3. **Notificaciones por email** - Alertar cuando se asignan/activan empleados
4. **Configuración por admin** - Cambiar horarios sin editar código
5. **Retry automático** - Reintentar si falla una tarea

## Preguntas Frecuentes (FAQ)

**P: ¿Qué pasa si Django se reinicia a las 2:00 AM?**
R: La tarea se pierde. El scheduler solo funciona mientras Django esté activo. Para garantizar ejecución incluso durante reinicios, usa Celery o Windows Task Scheduler.

**P: ¿Puedo tener múltiples servidores corriendo el scheduler?**
R: No es recomendado. Ejecutarías la asignación de evaluaciones múltiples veces. Si tienes múltiples servidores, migra a Celery con Redis.

**P: ¿Los logs se guardan en el archivo django.log?**
R: Sí, todos los eventos se registran en `logs/django.log`. Puedes tener logs separados configurando `LOGGING` en `settings.py`.

**P: ¿Cómo fuerzo una ejecución manual de las tareas?**
R: Ejecuta los comandos directamente:
```bash
python manage.py asignar_evaluaciones_periodo_prueba
python manage.py activar_empleados_prueba
```

**P: ¿Puedo cambiar los horarios de ejecución?**
R: Sí, edita `apps/core/scheduler.py` en la función `start_scheduler()` y cambia los parámetros `hour` y `minute`.

## Contacto y Soporte

Para problemas o dudas:
1. Revisar logs en `logs/django.log`
2. Ejecutar `python manage.py start_scheduler --status` para ver estado
3. Ejecutar comandos manualmente para probar
4. Consultar la documentación de APScheduler: https://apscheduler.readthedocs.io/

---

**Última actualización:** 2025-11-26
**Versión:** 1.0
