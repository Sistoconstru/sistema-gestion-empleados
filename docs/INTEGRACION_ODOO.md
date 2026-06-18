# Integración SIGHU ↔ Odoo Community — Plan de Implementación

**Estado:** En revisión  
**Última actualización:** 2026-05-21  
**Versión Odoo objetivo:** Community 19.0 (Railway — proyecto `construinmuniza`)  
**Repositorio SIGHU:** rama `mi-rama` (Django 5.2 + DRF)  
**Repositorio Odoo:** rama `main` / desarrollo en `desarrollo-sistoferney`

---

## 1. Objetivo

Conectar SIGHU (Sistema de Gestión de Empleados) con Odoo Community para que Odoo pueda procesar la **nómina** y la **nómina electrónica DIAN**, manteniendo SIGHU como única fuente de verdad para los datos personales y organizacionales de los empleados.

**Principios de diseño:**

- **SIGHU = source of truth** para datos personales, cargo, área, sede, fechas, contacto.
- **Odoo = source of truth** para conceptos de nómina (salarios, deducciones, aportes, conceptos contables, novedades, EPS, AFP, ARL, tipo contrato, cuenta bancaria).
- Comunicación por **red interna de Railway** (sin egress fees, baja latencia) — requiere que ambos servicios estén en el mismo proyecto Railway (ver §9).
- Autenticación por **token estático** servicio-a-servicio (no sesiones, no JWT).
- Sincronización **incremental** (no traer todo en cada corrida).
- Sin bloquear la UI de SIGHU si Odoo está caído.

---

## 2. Arquitectura general

```
┌─────────────────────────────────┐         ┌─────────────────────────────┐
│         SIGHU (Django)          │         │      Odoo Community 19      │
│                                 │         │                             │
│  ┌───────────────────────────┐  │         │  ┌──────────────────────┐   │
│  │ empleados                 │  │         │  │ hr.employee          │   │
│  │ historial_cargos          │  │         │  │ hr.contract          │   │
│  └───────────┬───────────────┘  │         │  │ + x_sighu_uuid       │   │
│              │                  │         │  └──────────▲───────────┘   │
│  ┌───────────▼───────────────┐  │  PULL   │             │               │
│  │ DRF: /api/v1/odoo/...     │◄─┼─────────┼─ cron 1h   ┤               │
│  └───────────┬───────────────┘  │         │             │               │
│              │                  │  PUSH   │  ┌──────────┴───────────┐   │
│  ┌───────────▼───────────────┐  │ ────────┼─►│ Endpoint webhook     │   │
│  │ Signal post_save Empleado │  │         │  │ /sighu_sync/webhook  │   │
│  │ → tarea async → POST Odoo │  │         │  └──────────────────────┘   │
│  └───────────────────────────┘  │         │                             │
│                                 │         │  Módulo: construinmuniza_   │
│  Network: sighu.railway.internal│         │           sync              │
└─────────────────────────────────┘         └─────────────────────────────┘
```

**Modelo híbrido pull + push:**
- **Push (signal SIGHU → async → Odoo):** mecanismo principal. Baja latencia en cambios. Si falla, no afecta a SIGHU.
- **Pull (cron Odoo cada 1 hora):** red de seguridad. Solo entra en juego si el push falló.

**SIGHU es el único origen de empleados.** Odoo NO debe permitir la creación manual de `hr.employee` por la UI estándar (ver §3.10).

---

## 3. Fase 1 — Sincronización de empleados SIGHU → Odoo

### 3.1 Responsabilidades por lado

| Lado | Responsabilidad |
|------|----------------|
| **SIGHU (Django)** | Único origen de empleados. Exponer endpoint REST (read-only). Disparar push asíncrono en cambios. Generar/rotar tokens de servicio. Logging de cada request. |
| **Odoo (`construinmuniza_sync`)** | Cron pull cada 1 hora (red de seguridad). Endpoint webhook para push (principal). Crear/actualizar `hr.employee`. Mantener mapeo `x_sighu_uuid → id Odoo`. Wizard "Sincronizar ahora". Bloquear creación manual de empleados. Logging por sync. |

### 3.2 Autenticación

- SIGHU genera un token estático: `SIGHU_ODOO_TOKEN` (env var en Railway, 64+ chars random).
- Odoo lo envía en cada request: `Authorization: Token <token>`
- DRF en SIGHU lo valida contra la env var.
- `SIGHU_ODOO_WEBHOOK_TOKEN`: Odoo lo valida en el endpoint webhook.
- **Rotación:** cambiar env var en Railway → redeploy. Cero código.

### 3.3 Endpoints de SIGHU

#### `GET /api/v1/odoo/empleados/`

**Query params:**
- `modified_since` (ISO 8601 con timezone explícito, opcional). Si se omite, devuelve todos los activos.
  - ✅ Válido: `2026-05-22T18:00:22Z`, `2026-05-22T13:00:22-05:00`
  - ❌ Inválido: `2026-05-22T18:00:22` (sin tz) — SIGHU lo interpretará como hora local del servidor y los resultados serán impredecibles. Esto NO se tolera intencionalmente: el contrato exige timezone explícito para evitar bugs sutiles de zona horaria entre los dos servicios.
- `page` (int, default 1). Paginación de 100 registros.
- `incluir_inactivos` (bool, default `false`).

**Headers:** `Authorization: Token <SIGHU_ODOO_TOKEN>`

#### `GET /api/v1/odoo/empleados/<uuid>/`

Detalle de un empleado por su UUID.

#### `GET /api/v1/odoo/healthcheck/`

Sin autenticación. Devuelve `{"status": "ok"}`. Para verificar conectividad antes del cron.

### 3.4 Esquema JSON del empleado (contrato)

```json
{
  "sighu_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "tipo_documento": {
    "codigo_sighu": "CED",
    "codigo_dian": "13",
    "nombre": "Cédula de Ciudadanía"
  },
  "numero_documento": "1020304050",
  "nombres": "Juan Carlos",
  "apellidos": "Pérez Gómez",
  "nombre_completo": "Juan Carlos Pérez Gómez",
  "fecha_nacimiento": "1990-03-15",
  "ciudad_nacimiento": "Bogotá",
  "correo_electronico": "juan.perez@empresa.com",
  "telefono_contacto": "3001234567",
  "direccion": "Carrera 10 # 20 - 30",
  "fecha_ingreso": "2023-08-01",
  "estado": {
    "codigo": "999",
    "nombre": "Activo"
  },
  "sede": {
    "codigo": "BOG",
    "nombre": "Bogotá - Centro"
  },
  "escolaridad": "Profesional Universitario",
  "contacto_emergencia": {
    "nombre": "María Pérez",
    "telefono": "3007654321"
  },
  "cargo_actual": {
    "codigo": "ANL-RH-001",
    "nombre": "Analista de Recursos Humanos",
    "area": "Recursos Humanos",
    "salario": "3500000.00",
    "fecha_inicio_cargo": "2024-02-01",
    "jefe_directo_uuid": "660e8400-e29b-41d4-a716-446655440111"
  },
  "centro_costo": {
    "referencia": "1003",
    "cuenta_analitica": "[1003] RRHH",
    "nombre": "RRHH"
  },
  "fecha_actualizacion": "2026-05-20T14:32:11Z"
}
```

**Notas técnicas del contrato:**

- `sighu_uuid` = `empleados.id` (tipo UUID en PostgreSQL). Es la llave estable. **No usar `numero_documento`** como llave.
- `cargo_actual.salario` proviene de `historial_cargos.salario` donde `activo=True` y `fecha_fin IS NULL`. **No** viene de `cargos.salario_minimo/maximo` (esos son rangos de referencia del cargo, no el salario real del empleado).
- `cargo_actual.jefe_directo_uuid` proviene de `historial_cargos.jefe_directo_id` (UUID de otro empleado).
- `centro_costo` proviene de `empleados.centro_costo_id` → `centros_costo`. La **llave de matching** contra Odoo es `referencia` (= `account.analytic.account.code` ya estandarizado en Odoo del cliente). `cuenta_analitica` es la etiqueta `[CODE] NOMBRE` tal cual aparece en el catálogo Odoo. Puede ser `null` si el empleado aún no tiene centro asignado (los empleados creados desde el form a partir de 2026-06-12 lo llevan obligatorio).
- `tipo_documento.codigo_dian` es el código que Odoo debe usar para nómina electrónica DIAN (ver §3.4.1).
- `fecha_actualizacion` debe ser `MAX(empleados.fecha_actualizacion, historial_cargos.fecha_actualizacion)` donde el historial esté activo. Si solo cambia el cargo (HistorialCargo) pero no el empleado, el `modified_since` debe detectarlo igualmente.
- Fechas: ISO 8601, UTC para timestamps, `YYYY-MM-DD` para fechas simples.
- Campos opcionales nulos vienen como `null`, no se omiten.

> ⚠️ **Fase 3 — Nombres separados para DIAN:** DIAN exige primer nombre, segundo nombre, primer apellido y segundo apellido por separado. SIGHU almacena `nombres` y `apellidos` como cadenas únicas. El split automático es frágil (ej. "María Fernanda"). **Decisión pendiente para Fase 3:** el operador de nómina captura los nombres separados directamente en Odoo al activar el empleado (consistente con §4.2).

#### 3.4.1 Mapeo de tipos de documento SIGHU ↔ DIAN

| Código SIGHU | Nombre | Código DIAN | Código Odoo (`l10n_co`) |
|---|---|---|---|
| `CED` | Cédula | `13` | `CC` |
| `TI` | Tarjeta de Identidad | `12` | `TI` |
| `CEX` | Cédula de Extranjería | `22` | `CE` |
| `PASP` | Pasaporte | `41` | `PASP` |

### 3.5 Mapeo SIGHU → Odoo `hr.employee`

| Campo SIGHU | Fuente BD SIGHU | Campo Odoo | Notas |
|---|---|---|---|
| `sighu_uuid` | `empleados.id` | `x_sighu_uuid` (Char, indexed, unique) | **Llave de sincronización.** |
| `nombre_completo` | `empleados.nombres + apellidos` | `name` | Requerido en Odoo. |
| `nombres` | `empleados.nombres` | `x_first_name` | Para nómina electrónica DIAN. |
| `apellidos` | `empleados.apellidos` | `x_last_name` | Para nómina electrónica DIAN. |
| `numero_documento` | `empleados.numero_documento` | `identification_id` | |
| `tipo_documento.codigo_dian` | `tipos_documento.codigo` → mapeo | `x_tipo_documento` | Usar código DIAN (§3.4.1). |
| `fecha_nacimiento` | `empleados.fecha_nacimiento` | `birthday` | |
| `ciudad_nacimiento` | `employees_ciudad.nombre` | `place_of_birth` | |
| `correo_electronico` | `empleados.correo_electronico` | `work_email` | |
| `telefono_contacto` | `empleados.telefono_contacto` | `mobile_phone` | |
| `direccion` | `empleados.direccion` | `private_street` | |
| `fecha_ingreso` | `empleados.fecha_ingreso` | `x_fecha_ingreso` + `hr.contract.date_start` | |
| `cargo_actual.nombre` | `cargos.nombre` | `job_title` + `job_id` | Crear `hr.job` si no existe. |
| `cargo_actual.area` | `areas_empresa.nombre` | `department_id` | Crear `hr.department` si no existe. |
| `cargo_actual.salario` | `historial_cargos.salario` (activo) | `hr.contract.wage` | Crear/actualizar contrato. |
| `cargo_actual.fecha_inicio_cargo` | `historial_cargos.fecha_inicio` | `hr.contract.date_start` | |
| `cargo_actual.jefe_directo_uuid` | `historial_cargos.jefe_directo_id` | `parent_id` | Resolver vía `x_sighu_uuid`. |
| `centro_costo.referencia` | `centros_costo.referencia` | `account.analytic.account.code` → `hr.contract.analytic_account_id` (o equivalente del cliente) | Matching por `code`. Si no existe, registrar en `OdooSyncFalla` (los 31 centros ya están estandarizados en Odoo, no se deben crear). |
| `estado.codigo` | `estados_empleado.codigo` | `active` + `x_estado_sighu` | `999` → active=True; `INACTIVO` → active=False. |
| `contacto_emergencia.nombre` | `empleados.contacto_emergencia_nombre` | `emergency_contact` | |
| `contacto_emergencia.telefono` | `empleados.contacto_emergencia_telefono` | `emergency_phone` | |
| `sede.nombre` | `sedes.nombre` | `x_sede_sighu` | |
| `escolaridad` | `escolaridad.nombre` | `study_field` | |

### 3.6 Push de cambios (SIGHU → Odoo)

**Endpoint en Odoo:** `POST /sighu_sync/webhook/empleado`

**Payload:**
```json
{
  "evento": "created" | "updated" | "deleted",
  "timestamp": "2026-05-21T10:15:00Z",
  "empleado": { }
}
```

**Disparador en SIGHU — Push síncrono con timeout (Opción A, aprobada):**

Celery NO está instalado en SIGHU. Se usa push síncrono con timeout corto dentro del signal:

```python
# Signal post_save en Empleado / HistorialCargo
def _push_a_odoo(empleado, evento):
    try:
        requests.post(
            settings.ODOO_WEBHOOK_URL,
            json={"evento": evento, "empleado": serializar(empleado)},
            headers={"Authorization": f"Token {settings.SIGHU_ODOO_WEBHOOK_TOKEN}"},
            timeout=2
        )
    except (Timeout, ConnectionError, RequestException):
        OdooSyncFalla.objects.create(empleado=empleado, evento=evento)
        # El cron pull de Odoo recupera el cambio en máximo 1 hora
```

- SIGHU no se bloquea: si Odoo no responde en 2s, continúa sin error visible al usuario.
- `OdooSyncFalla` registra el intento fallido para diagnóstico.
- El pull horario de Odoo es la red de seguridad — no se espera que actúe normalmente.
- Migración futura a Celery/Django-Q no requiere cambiar el contrato JSON.

**Respuestas esperadas de Odoo:**
- `200 {"status": "ok", "odoo_employee_id": 42}` → éxito.
- `4xx` → error de contrato, registrar en `OdooSyncFalla`, no reintentar.
- `5xx` / timeout → registrar en `OdooSyncFalla`, el pull lo recupera.

### 3.7 Estados SIGHU → comportamiento Odoo

**Estados actuales en BD producción SIGHU** (verificado 2026-05-21):

| `id` | `codigo` | `nombre` | `permite_acceso` |
|---|---|---|---|
| 1 | `999` | Activo | ✅ |
| 2 | `INACTIVO` | Inactivo | ❌ |
| 3 | `VACACIONES` | Vacaciones | ✅ |
| 4 | `p-prue` | Periodo de prueba | ✅ |
| 5 | `ACTIVO` | ACTIVO | ✅ |
| 6 | `periodo_prueba` | periodo_prueba | ✅ |
| 7 | `PRUEBA` | Per. de prueba | ✅ |

> ⚠️ **Deuda técnica bloqueante:** "Activo" tiene 2 códigos (`999` y `ACTIVO`). "Período de prueba" tiene 3 (`p-prue`, `periodo_prueba`, `PRUEBA`). Faltan estados para Licencia, Suspendido y Retirado.

**Mapeo canónico propuesto:**

| Código canónico | Nombre | Duplicados a migrar | `hr.employee.active` | Acción Odoo |
|---|---|---|---|---|
| `999` | Activo | `ACTIVO` → `999` | True | Contrato vigente |
| `p-prue` | Período de prueba | `periodo_prueba`, `PRUEBA` → `p-prue` | True | `x_periodo_prueba=True` |
| `VACACIONES` | Vacaciones | — | True | `x_en_vacaciones=True` |
| `INACTIVO` | Inactivo | — | False | Cerrar contrato |
| `LICENCIA` *(crear)* | Licencia/Incapacidad | — | True | `x_en_licencia=True` |
| `SUSPENDIDO` *(crear)* | Suspendido | — | True | `x_suspendido=True` |
| `RETIRADO` *(crear)* | Retirado | — | False | Cerrar contrato definitivo |

**Acción requerida (SIGHU, previo a Fase 1):**
1. Migración Django que consolide duplicados y cree los 3 estados faltantes.
2. Actualizar queries del codebase que usan `['999', 'ACTIVO']` → solo `['999']`.

### 3.8 Logging

**SIGHU loguea:** requests entrantes de Odoo, pushes salientes, fallas tras reintentos → `OdooSyncFalla`.

**Odoo loguea:** cada corrida del cron (creados/actualizados/errores), cada webhook recibido. Vista "Bitácora de sincronización SIGHU" en backend.

### 3.9 Migración inicial (primer sync)

1. Desplegar `construinmuniza_sync` en Odoo.
2. Configurar env vars: `SIGHU_API_URL`, `SIGHU_ODOO_TOKEN`, `SIGHU_ODOO_WEBHOOK_TOKEN`.
3. Ejecutar wizard "Sincronización inicial" → trae los **338 empleados activos** (volumen confirmado).
4. Validar manualmente 10 empleados (mapeo, contrato, jefe directo resuelto).
5. Activar cron y signals.

> **Estado actual Odoo:** solo 1 `hr.employee` (admin). Sin conciliación requerida — la sync inicial crea todos desde cero.

### 3.10 Bloqueo de creación manual en Odoo

- Override `create()` en `hr.employee`: rechazar si no trae `x_sighu_uuid`.
- Campos sincronizados son readonly (excepto si el caller es el módulo sync).
- Grupo "Operador Nómina": acceso a `hr.contract` y conceptos, sin crear/editar `hr.employee`.
- Wizard admin "Crear empleado fuera de SIGHU" oculto detrás de permisos elevados.

---

## 4. Fase 2 — Motor de nómina en Odoo

### 4.1 Componentes

- **OCA `payroll` rama 19.0** — motor base (rama 19.0 confirmada activa al 2026-05-21).

> ⚠️ `hr_contract` no existe aún en Odoo — instalar OCA payroll es prerequisito de Fase 2.

- **`construinmuniza_nomina`** con reglas colombianas:

| Concepto | Detalle |
|---|---|
| PILA Salud | 8.5% empleador + 4% empleado |
| PILA Pensión | 12% empleador + 4% empleado |
| ARL | Variable según clase de riesgo (0.522% – 6.96%) |
| Parafiscales | SENA 2%, ICBF 3%, CCF 4% |
| Cesantías | 8.33% mensual |
| Intereses cesantías | 1% anual sobre saldo |
| Prima de servicios | 8.33% semestral |
| Vacaciones | 4.17% mensual |
| Dotación | Para salarios ≤ 2 SMMLV |
| Retención en fuente | Art. 383 ET — reutilizar `construinmuniza_retenciones` |

### 4.2 Campos de nómina que viven en Odoo (no en SIGHU)

Estos datos son responsabilidad de Odoo — se completan al hacer la sincronización inicial del empleado:

| Campo | Necesario para | Responsable |
|---|---|---|
| Género | PILA, nómina electrónica DIAN | Operador nómina en Odoo al activar empleado |
| EPS | PILA salud | Operador nómina en Odoo |
| Fondo de pensión | PILA pensión | Operador nómina en Odoo |
| Fondo de cesantías | Cesantías | Operador nómina en Odoo |
| CCF | Parafiscales | Operador nómina en Odoo |
| Clase de riesgo ARL | PILA ARL | Operador nómina en Odoo (según cargo) |
| Tipo de contrato | Liquidaciones | Operador nómina en Odoo |
| Cuenta bancaria | Pago nómina | Operador nómina en Odoo al activar empleado |
| Primer/segundo nombre y apellido | Nómina electrónica DIAN (Fase 3) | Operador nómina en Odoo — no hacer split automático |

### 4.3 Decisiones pendientes

- ¿Periodicidad: mensual, quincenal, o ambas?
- ¿Novedades (incapacidades, horas extra, comisiones): desde SIGHU o capturadas en Odoo?
- ¿Integración contable con `account.move` desde el inicio o nómina pura primero?

---

## 5. Fase 3 — Nómina electrónica DIAN

### 5.1 Componentes

- Generación XML conforme al Anexo Técnico DIAN para nómina electrónica (DSN).
- Firma digital y envío.
- Almacenamiento de CUNE por registro.

### 5.2 Decisiones pendientes

- **Proveedor tecnológico DIAN** — en negociación (Carvajal Digital opción probable).
- Ambiente de habilitación DIAN antes de producción.
- Almacenamiento XMLs firmados (Railway Volume + S3 o similar).

---

## 6. Preguntas abiertas resueltas

| # | Pregunta | Respuesta |
|---|---|---|
| 1 | Hostname SIGHU en Railway | `sighu.railway.internal` — **requiere migrar SIGHU al proyecto `construinmuniza`** (ver §9) |
| 2 | Hostname Odoo en Railway | `sistemaconstruinmuniza.railway.internal` |
| 3 | VPN / IP whitelist | No requerido — token + red privada Railway es suficiente |
| 4 | Volumen empleados | **338 empleados**, 71 cargos, 8 sedes, 9 áreas |
| 5 | Quién opera Odoo post go-live | Por definir |
| 6 | `hr.employee` pre-existentes en Odoo | Solo 1 (admin). Sin conciliación requerida |
| 7 | Campos faltantes para nómina | Confirmado: género, EPS, AFP, ARL, tipo contrato, banco → gestionados en Odoo (§4.2) |
| 8 | Consolidar `EstadoEmpleado` | Aprobado — migración requerida antes de Fase 1 (§3.7) |

---

## 7. Entregables por lado

### Lado SIGHU (Django)

1. Migración de estados (§3.7) — **prerequisito bloqueante**.
2. Módulo `apps/integraciones/odoo/`.
3. `OdooEmpleadoSerializer` con contrato del §3.4.
4. `OdooEmpleadoViewSet` (read-only, paginado).
5. `TokenAuthentication` contra env var.
6. Signal `post_save` en `Empleado` y `HistorialCargo` → tarea async.
7. Modelo `OdooSyncFalla`.
8. Vista admin bitácora syncs salientes.
9. Tests de contrato JSON.

### Lado Odoo

1. Módulo `construinmuniza_sync`.
2. Extender `hr.employee` con campos custom del §3.5.
3. Cron `ir.cron` cada 1 hora.
4. Controller webhook `/sighu_sync/webhook/empleado`.
5. Wizard "Sincronizar ahora" + "Sincronización inicial".
6. Modelo `sighu.sync.log` con bitácora.
7. Override `create()` para bloquear creación manual.

### Orden de trabajo sugerido

| Semana | Actividad |
|---|---|
| **-1** | Staging: preparar nuevo servicio SIGHU en proyecto `construinmuniza` (sin cortar producción). |
| **0** | Ventana de mantenimiento: migrar SIGHU al proyecto Railway `construinmuniza`. Consolidar estados SIGHU. |
| **1** | SIGHU implementa endpoint read-only. Odoo arranca módulo base `construinmuniza_sync`. |
| **2** | Odoo pull cron + wizard inicial. Primer sync de prueba con `sighu_produccion` local. |
| **3** | SIGHU push síncrono (Opción A). Odoo webhook. Tests end-to-end con datos reales. |
| **4** | Logging completo, alertas, deploy a producción Fase 1. Monitorear 48h. |
| **5-8** | Fase 2: instalar OCA payroll + `construinmuniza_nomina`. |

---

## 8. Criterios de aceptación Fase 1

- ✅ Empleado nuevo en SIGHU aparece en Odoo en menos de 1 minuto (push).
- ✅ Cambio de cargo/salario en SIGHU se refleja en contrato Odoo en menos de 1 minuto.
- ✅ Si Odoo está caído, el cambio se reconcilia en máximo 1 hora (pull).
- ✅ `modified_since` devuelve solo registros modificados desde esa fecha.
- ✅ Bitácora permite identificar cualquier fallo en menos de 5 minutos.
- ✅ Rotar token no requiere despliegue de código.
- ✅ Crear empleado manualmente en Odoo es rechazado con mensaje claro.
- ✅ 338 empleados sincronizados y validados en sincronización inicial.

---

## 9. Prerequisito de infraestructura — Migración SIGHU a proyecto Railway `construinmuniza`

**Por qué:** Railway's private networking (`*.railway.internal`) solo funciona dentro del mismo proyecto. SIGHU y Odoo están actualmente en proyectos separados.

**Plan de migración (ventana de mantenimiento de ~30 min):**

> ⚠️ Entre el dump y el cambio de DNS existe una ventana donde escrituras en la BD vieja se perderían. Para evitar pérdida de datos se anuncia mantenimiento y se pone SIGHU en modo lectura durante el corte.

1. **Preparación (días antes, sin afectar usuarios):**
   - Crear servicio SIGHU en proyecto `construinmuniza` (mismo repo, mismas env vars).
   - Crear nuevo Postgres SIGHU en proyecto `construinmuniza`.
   - Verificar que SIGHU arranca correctamente en el nuevo servicio (URL temporal Railway).

2. **Ventana de mantenimiento (~30 min, coordinar con usuarios):**
   - Anunciar mantenimiento.
   - Activar flag read-only en SIGHU actual (o apagarlo directamente).
   - Dump final del Postgres SIGHU actual → restore en nuevo Postgres.
   - Apuntar nuevo servicio SIGHU a nuevo Postgres interno.
   - Verificar datos en nuevo servicio.
   - Agregar dominio personalizado al nuevo servicio en Railway.
   - Cambiar DNS → nuevo servicio (propagación: segundos con TTL bajo).
   - Verificar dominio resuelve al nuevo servicio.

3. **Post-migración:**
   - Apagar proyecto SIGHU antiguo (conservar backup BD por 30 días por seguridad).
   - Confirmar red interna: `sighu.railway.internal` ↔ `sistemaconstruinmuniza.railway.internal`.

**Resultado:**
```
Proyecto construinmuniza (Railway)
├── Postgres Odoo     → postgres.railway.internal:5432
├── Postgres SIGHU    → sighu-db.railway.internal:5432
├── Odoo              → sistemaconstruinmuniza.railway.internal
└── SIGHU             → sighu.railway.internal (dominio personalizado igual)
```
