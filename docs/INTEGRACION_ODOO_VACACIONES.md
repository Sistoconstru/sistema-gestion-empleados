# Integración SIGHU ↔ Odoo — Vacaciones

Este documento cubre el contrato de los endpoints de vacaciones que SIGHU expone
para Odoo. Todos requieren `Authorization: Token <SIGHU_ODOO_TOKEN>`.

## Flujos soportados

Hay dos rutas posibles para que una solicitud de vacaciones llegue a SIGHU:

### A) Origen SIGHU → Odoo (flujo del jefe)

El jefe directo o un rol autorizado crea la solicitud en SIGHU. SIGHU la envía
a Odoo para validación de saldo y aprobación por RRHH. Odoo notifica de vuelta
cuando el estado cambia.

- Push: SIGHU → webhook Odoo (fuera del alcance de este doc).
- Callback: Odoo → `POST /api/v1/odoo/vacaciones/estado/` (endpoint 1).

### B) Origen Odoo → SIGHU (flujo de RRHH)

RRHH crea la solicitud directamente en Odoo. Aplica a dos casos:

- **Vacaciones en tiempo** (días libres) creadas por RRHH sin pasar por el jefe.
- **Compensaciones en dinero** (`tipo="dinero"`), que por naturaleza solo se
  originan en Odoo por RRHH.

Al aprobar/cancelar, Odoo llama a SIGHU. Es el mismo endpoint para ambos casos.

- Callback único: Odoo → `POST /api/v1/odoo/vacaciones/importar/` (endpoint 2).

---

## Endpoint 1 — `POST /api/v1/odoo/vacaciones/estado/`

Actualiza el estado de una solicitud que YA existe en SIGHU (identificada por
`leave_id_odoo`). Si no existe → 404.

### Request

```json
{
  "leave_id": 12345,
  "estado": "aprobada",           // "aprobada" | "rechazada" | "cancelada"
  "motivo": "opcional",
  "aprobada_por": "user@odoo",
  "fecha_estado": "2026-06-30T14:00:00Z",
  "saldo_dias_disponibles": 12.5  // opcional (ver sección Saldo)
}
```

### Respuestas

- `200 { status: "recibido", ... }` — el estado cambió.
- `200 { status: "ya_procesado", ... }` — el estado enviado coincide con el actual (idempotente).
- `400` — payload inválido.
- `404` — `leave_id` no existe en SIGHU.

---

## Endpoint 2 — `POST /api/v1/odoo/vacaciones/importar/`

Importa una solicitud creada directamente en Odoo. Soporta **dos tipos** con
claves de upsert distintas:

| tipo | Clave de upsert | Rango de fechas |
|---|---|---|
| `tiempo` | `leave_id` | Requerido |
| `dinero` (o `pago_dinero`) | `compensacion_id` | No aplica (nulo) |

**Nunca mezclar**: si `tipo="dinero"`, no envíes `leave_id`. Y viceversa.

### Request — tipo=tiempo

```json
{
  "tipo": "tiempo",
  "leave_id": 12345,                // clave de idempotencia
  "sighu_uuid": "uuid-empleado",    // opcional
  "cedula": "1035831455",           // opcional (uno de los dos requerido al CREAR)
  "fecha_inicio": "2026-08-01",
  "fecha_fin": "2026-08-15",
  "dias": 10,                       // informativo
  "estado": "aprobada",             // "aprobada" | "cancelada"
  "motivo": "opcional",
  "aprobada_por": "user@odoo",
  "fecha_estado": "2026-06-30T14:00:00Z",
  "saldo_dias_disponibles": 8.0     // opcional (ver sección Saldo)
}
```

### Request — tipo=dinero (compensación)

```json
{
  "tipo": "dinero",
  "compensacion_id": 1635,          // clave de idempotencia (distinta de leave_id)
  "leave_id": null,                 // debe ir nulo o ausente para tipo=dinero
  "sighu_uuid": "uuid-empleado",    // opcional
  "cedula": "1035831455",           // opcional (uno de los dos requerido al CREAR)
  "dias": 7.0,                      // días compensados (informativo)
  "valor": 408544,                  // valor pagado en pesos (evidencia)
  "fecha": "2026-07-01",            // periodo del lote de nómina
  "fecha_inicio": null,             // NO aplica: no hay disfrute de días
  "fecha_fin": null,                // NO aplica
  "estado": "aprobada",             // "aprobada" (aplicada) | "cancelada" (reversada)
  "motivo": "Compensación de vacaciones en dinero (7 días) aplicada por RRHH.",
  "aprobada_por": "rrhh@empresa.com",
  "saldo_dias_disponibles": 5.0     // opcional (ver sección Saldo)
}
```

### Respuestas

- `201 { status: "creado", sighu_uuid, leave_id|compensacion_id, estado_local }` — nueva solicitud creada.
- `200 { status: "actualizado", ... }` — solicitud existente actualizada (cambió estado).
- `200 { status: "ya_procesado", ... }` — el estado enviado coincide (idempotente).
- `400` — payload inválido (clave faltante, fechas inválidas, tipo/estado no permitido).
- `404` — empleado no encontrado por `sighu_uuid` ni por `cedula`.

### Comportamiento clave

- **Identificación del empleado:** primero por `sighu_uuid`; si no matchea, por `cedula`
  (=`numero_documento`). Solo se requiere al CREAR. En un update por reintento se
  puede omitir.
- **Idempotencia:** por `leave_id` cuando `tipo=tiempo`, por `compensacion_id` cuando
  `tipo=dinero`. Reintentos del cron de Odoo NO duplican registros ni notificaciones.
  Nunca colisionan porque son campos distintos.
- **`jefe_solicitante`:** siempre NULL en este flujo (nació en Odoo, no en SIGHU).
- **Cancelación posterior:** llamar al mismo endpoint con `estado="cancelada"`,
  manteniendo la misma clave de upsert (`leave_id` o `compensacion_id`).
- **Notificación al empleado:** cada transición terminal dispara una notificación
  in-app específica para cada tipo (`vacacion_aprobada` vs `vacacion_comp_aprobada`).
  Idempotente: `ya_procesado` no notifica.
- **Estados permitidos:** solo `aprobada` y `cancelada`. Los estados intermedios
  (`borrador`, `enviada_pendiente_rrhh`) no aplican porque las solicitudes creadas
  en Odoo llegan a SIGHU solo cuando ya son un hecho.

---

## Saldo de días disponibles

**Odoo es la fuente autoritativa del saldo.** SIGHU NO calcula saldo — solo lo
muestra tal como lo envía Odoo (que ya considera vacaciones en tiempo + dinero).

Cualquiera de los dos endpoints acepta `saldo_dias_disponibles` como campo
opcional en el payload. Cuando viene:

- SIGHU guarda el valor en `Empleado.saldo_vacaciones_dias` y
  `Empleado.saldo_vacaciones_actualizado = now()`.
- El empleado ve el saldo en su vista **Mis vacaciones**.
- Si no viene, SIGHU mantiene el último valor conocido (o vacío si nunca ha llegado).

**Recomendación:** enviarlo en cada callback (crear, actualizar, cancelar). Es
un decimal (puede tener fracciones, ej: `8.5`).

Si el saldo cambia por razones que NO son un evento de vacaciones (ej: cierre
anual, ajuste manual), el dev de Odoo debe decidir el mecanismo (endpoint
adicional o llamada periódica). Hoy no está definido.

---

## Ejemplos

### Ejemplo 1 — crear vacación en tiempo

```http
POST /api/v1/odoo/vacaciones/importar/
Authorization: Token <SIGHU_ODOO_TOKEN>
Content-Type: application/json

{
  "tipo": "tiempo",
  "leave_id": 8891,
  "cedula": "1035831455",
  "fecha_inicio": "2026-08-01",
  "fecha_fin": "2026-08-10",
  "dias": 10,
  "estado": "aprobada",
  "aprobada_por": "rrhh@empresa.com",
  "saldo_dias_disponibles": 5.0
}
```

Respuesta:
```json
{ "status": "creado", "sighu_uuid": "b1c2...", "leave_id": 8891, "estado_local": "aprobada_rrhh" }
```

### Ejemplo 2 — crear compensación en dinero

```http
POST /api/v1/odoo/vacaciones/importar/
Authorization: Token <SIGHU_ODOO_TOKEN>
Content-Type: application/json

{
  "tipo": "dinero",
  "compensacion_id": 1635,
  "cedula": "1035831455",
  "dias": 7.0,
  "valor": 408544,
  "fecha": "2026-07-01",
  "estado": "aprobada",
  "motivo": "Compensación de vacaciones en dinero (7 días) aplicada por RRHH.",
  "aprobada_por": "rrhh@empresa.com",
  "saldo_dias_disponibles": 8.0
}
```

Respuesta:
```json
{ "status": "creado", "sighu_uuid": "b1c2...", "compensacion_id": 1635, "estado_local": "aprobada_rrhh" }
```

### Ejemplo 3 — reversar la compensación (RRHH la anula)

```http
POST /api/v1/odoo/vacaciones/importar/
Authorization: Token <SIGHU_ODOO_TOKEN>
Content-Type: application/json

{
  "tipo": "dinero",
  "compensacion_id": 1635,
  "estado": "cancelada",
  "motivo": "Reversada por RRHH — error en el lote de nómina.",
  "saldo_dias_disponibles": 15.0
}
```

Respuesta:
```json
{ "status": "actualizado", "sighu_uuid": "b1c2...", "compensacion_id": 1635, "estado_local": "cancelada_rrhh" }
```
