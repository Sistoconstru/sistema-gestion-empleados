# Polla Mundialista 2026 - Sistema de Predicciones

## Implementación Completada

Se ha implementado exitosamente un módulo completo de Polla Mundialista integrado en el marketplace de la aplicación SIGHU.

## Características Implementadas

### ✅ Modelos de Base de Datos
- **PartidoMundial**: Gestiona información de partidos (equipos, fecha, fase, resultado)
- **PrediccionMundial**: Almacena predicciones de empleados y puntos obtenidos

### ✅ Sistema de Puntos Personalizado
- **Resultado exacto**: 5 puntos base
- **Ganador correcto**: 3 puntos base
- **Empate acertado**: 3 puntos base
- **Acertar goles de un equipo**: +1 punto adicional
- **Multiplicadores por fase**:
  - Fase de Grupos: x1
  - Octavos de Final: x2
  - Cuartos de Final: x3
  - Semifinal: x4
  - Tercer Lugar: x4
  - Final: x5

### ✅ Sistema de Ranking con Criterios de Desempate

El ranking se ordena utilizando los siguientes criterios en orden de prioridad:

1. **Total de puntos ganados** (descendente) - El indicador principal
2. **Ganadores acertados** (descendente) - Cantidad de predicciones donde acertó el ganador (3+ puntos)
3. **Marcadores exactos** (descendente) - Cantidad de predicciones con resultado exacto (5+ puntos)
4. **Total de predicciones** (descendente) - Participación del empleado
5. **Anticipación promedio** (descendente) - Promedio de tiempo de anticipación al hacer predicciones

**Motivación por participación**: Cuando todos tienen los mismos puntos (especialmente al inicio o antes de que se jueguen partidos), el ranking premia a quien más participe haciendo predicciones.

**Proactividad recompensada**: El criterio de anticipación promedio premia a los empleados que hacen sus predicciones con mayor anticipación (días antes del partido) vs. los que esperan hasta el último minuto. Esto considera todas las fases del mundial de forma equilibrada.

### ✅ Vistas y Templates
- **Lista de partidos** con formularios de predicción en tiempo real
- **Ranking TOP 10** con podio y tabla completa
- **Mis Predicciones** con historial detallado por fase
- **Diseño responsive** reutilizando el estilo del marketplace

### ✅ Panel de Administración
- Gestión completa de partidos (crear, editar, marcar como finalizados)
- Visualización de predicciones de empleados
- Acciones masivas para recalcular puntos

### ✅ Comandos de Django
- **importar_partidos_mundial**: Importa partidos desde TheSportsDB API Premium
- **actualizar_resultados_mundial**: Actualiza resultados y calcula puntos automáticamente
- **actualizar_equipos_tbd**: Actualiza equipos TBD en fase eliminatoria

### ✅ Automatización
- Scripts para Windows y Linux/Mac
- Actualización automática cada 30 minutos
- Manejo de equipos TBD (To Be Determined)
- Logs de sincronización

---

## 📚 Documentación Completa

### 🚀 Rutas de Implementación

Elige según tu caso:

| Opción | Cuándo Usarla | Costo | Documentación |
|--------|---------------|-------|---------------|
| **🧪 Implementación Provisional** | Probar sistema AHORA con datos históricos | **$0 GRATIS** | [IMPLEMENTACION_PROVISIONAL.md](IMPLEMENTACION_PROVISIONAL.md) |
| **⚡ API Premium Optimizada** | Mundial 2026 real con ahorro 50% | $9 (1 mes) | [OPTIMIZACION_API_MUNDIAL.md](OPTIMIZACION_API_MUNDIAL.md) |
| **🏆 API Premium Completa** | Mundial 2026 con cobertura 24/7 | $18 (2 meses) | [GUIA_API_PREMIUM_MUNDIAL.md](GUIA_API_PREMIUM_MUNDIAL.md) |

### 📖 Documentos Disponibles

#### Para Desarrollo Local

1. **[IMPLEMENTACION_PROVISIONAL.md](IMPLEMENTACION_PROVISIONAL.md)** 🧪 **EMPEZAR AQUÍ**
   - Probar sistema gratis con Mundial 2022
   - Capacitar empleados sin costo
   - Migración fácil al Mundial 2026 real

2. **[GUIA_API_PREMIUM_MUNDIAL.md](GUIA_API_PREMIUM_MUNDIAL.md)** ⭐ **Para producción local**
   - Configuración con TheSportsDB Premium
   - Actualización automática de resultados
   - Scripts de automatización completos

3. **[OPTIMIZACION_API_MUNDIAL.md](OPTIMIZACION_API_MUNDIAL.md)** 💰 **Ahorra 50%**
   - Comparativa de costos
   - Horario optimizado 1PM-1AM
   - Reduce de $18 a $9

#### Para Producción (Railway)

4. **[DEPLOYMENT_POLLA_MUNDIAL_RAILWAY.md](DEPLOYMENT_POLLA_MUNDIAL_RAILWAY.md)** 🚀 **DEPLOYMENT PRODUCCIÓN**
   - Implementación en Railway
   - GitHub Actions para automatización
   - Configuración de variables de entorno
   - Webhooks y Cron Jobs
   - Troubleshooting en producción

5. **Este README** - Visión general e instrucciones básicas

---

## 🚀 Pasos para Activar el Módulo

### 1. Crear y Aplicar Migraciones

```bash
# Activar entorno virtual (si aplica)
# En Windows:
.\venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Crear migraciones
python manage.py makemigrations employees

# Aplicar migraciones
python manage.py migrate
```

### 2. Instalar Dependencias Adicionales

```bash
pip install requests
```

### 3. Configurar API de TheSportsDB (Recomendado)

⚠️ **IMPORTANTE**: La API gratuita tiene limitaciones severas (15 requests/mes).

**Opción A: API Premium - $9/mes** ⭐ **RECOMENDADO**
1. Contratar plan Premium en https://www.thesportsdb.com/pricing
2. Obtener API Key
3. Agregar a `.env`:
   ```env
   THESPORTSDB_API_KEY=tu_api_key_premium_aqui
   ```
4. Ver [Guía API Premium](GUIA_API_PREMIUM_MUNDIAL.md) para detalles completos

**Opción B: Entrada Manual** (Sin costo)
- Cargar partidos manualmente desde `/admin/employees/partidomundial/`
- Actualizar resultados manualmente después de cada partido

### 4. Importar Partidos del Mundial

**Con API Premium:**
```bash
python manage.py importar_partidos_mundial --season=2026
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

### 5. Configurar Actualización Automática (Opcional - Solo con API Premium)

**Opción Fácil - Usar Scripts Incluidos:**

**Windows:**
```bash
# Configurar tarea programada que ejecute:
C:\ruta\proyecto\actualizar_polla_mundial.bat
# Cada 30 minutos
```

**Linux/Mac:**
```bash
# Agregar a crontab:
*/30 * * * * /ruta/proyecto/actualizar_polla_mundial.sh
```

📖 **Ver instrucciones detalladas en:** [Guía API Premium](GUIA_API_PREMIUM_MUNDIAL.md)

---

## 📋 Uso del Sistema

### Para Empleados

1. **Acceder al Marketplace**
   - Ir a `Marketplace > Polla Mundial 2026`

2. **Hacer Predicciones**
   - Ver lista de partidos disponibles
   - Ingresar marcador predicho para cada partido
   - Guardar antes de que cierre (5 min antes del partido)

3. **Ver Ranking**
   - Consultar TOP 10 en el banner principal
   - Ver posición personal y puntos totales
   - Revisar ranking completo con todos los participantes

4. **Revisar Historial**
   - Ver todas las predicciones realizadas
   - Consultar puntos obtenidos por partido
   - Filtrar por fase del torneo

### Para Administradores

1. **Gestionar Partidos** (`/admin/employees/partidomundial/`)
   - Crear partidos manualmente
   - Editar fechas y horarios
   - Cargar resultados reales
   - Marcar como finalizados

2. **Monitorear Predicciones** (`/admin/employees/prediccionmundial/`)
   - Ver todas las predicciones
   - Recalcular puntos si es necesario
   - Filtrar por fase o empleado

3. **Actualizar Resultados**
   ```bash
   # Automático desde API
   python manage.py actualizar_resultados_mundial

   # Recalcular todos los puntos
   python manage.py actualizar_resultados_mundial --recalcular
   ```

---

## 🔧 Personalización

### Modificar Sistema de Puntos

Editar [`apps/employees/models.py`](apps/employees/models.py) en el método `PrediccionMundial.calcular_puntos()`:

```python
def calcular_puntos(self):
    # Modificar valores aquí
    puntos = 0

    if resultado_exacto:
        puntos = 5  # Cambiar este valor
    elif ganador_correcto:
        puntos = 3  # Cambiar este valor

    # ...
    return puntos
```

### Modificar Multiplicadores

Editar [`apps/employees/models.py`](apps/employees/models.py) en `PartidoMundial.MULTIPLICADORES_PUNTOS`:

```python
MULTIPLICADORES_PUNTOS = {
    'grupos': 1,      # Modificar aquí
    'octavos': 2,
    'cuartos': 3,
    'semifinal': 4,
    'final': 5,
}
```

---

## 📡 API de TheSportsDB

### Endpoints Utilizados

- **Eventos de temporada**: `https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4429&s=2026`
- **Detalle de evento**: `https://www.thesportsdb.com/api/v1/json/3/lookupevent.php?id={event_id}`

### Notas
- API Key gratuita: `3`
- Liga FIFA World Cup ID: `4429`
- Los datos del Mundial 2026 pueden no estar disponibles hasta que se acerque el torneo

---

## 🗑️ Desinstalación (Post-Mundial)

Cuando finalice el Mundial y quieras eliminar el módulo:

1. **Eliminar datos**:
   ```bash
   python manage.py shell
   >>> from apps.employees.models import PartidoMundial, PrediccionMundial
   >>> PrediccionMundial.objects.all().delete()
   >>> PartidoMundial.objects.all().delete()
   ```

2. **Eliminar código** (opcional):
   - Comentar modelos en `models.py`
   - Comentar imports en `admin.py`
   - Comentar URLs en `urls.py`
   - Eliminar archivos de vistas y templates

3. **Crear migración de eliminación**:
   ```bash
   python manage.py makemigrations employees
   python manage.py migrate
   ```

---

## 📊 Estadísticas y Reportes

El sistema calcula automáticamente:
- **Puntos totales** por empleado
- **Número de predicciones** realizadas
- **Resultados exactos** acertados
- **Promedio de puntos** por predicción
- **Ranking en tiempo real**

---

## 🐛 Solución de Problemas

### No aparecen partidos
- Verificar que se hayan importado: `python manage.py importar_partidos_mundial`
- Revisar que `activo=True` en el admin

### No se actualizan puntos
- Ejecutar recálculo manual: `python manage.py actualizar_resultados_mundial --recalcular`
- Verificar que los partidos estén marcados como `finalizado=True`

### Error al guardar predicción
- Verificar que el partido aún acepte predicciones (5 min antes)
- Revisar que el marcador esté en rango 0-20

---

## 📝 Licencia

Este módulo es parte del sistema SIGHU y sigue la misma licencia del proyecto principal.

---

**Desarrollado con Django y amor por el fútbol ⚽**
