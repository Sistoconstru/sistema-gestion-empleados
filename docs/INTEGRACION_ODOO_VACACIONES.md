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

RRHH crea la solicitud directamente en Odoo (típicamente **vacaciones pagadas
en dinero** u otras solicitudes que no pasan por el jefe de SIGHU). Al aprobar,
Odoo debe llamar al endpoint de importación para que el registro quede en el
historial del empleado. Si luego se cancela, Odoo llama al mismo endpoint con
`estado="cancelada"`.

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
  "aprobada_por": "user@odoo",    // opcional (auditoría)
  "fecha_estado": "2026-06-30T14:00:00Z"  // opcional
}
```

### Respuestas

- `200 { status: "recibido", ... }` — el estado cambió.
- `200 { status: "ya_procesado", ... }` — el estado enviado coincide con el actual (idempotente).
- `400` — payload inválido.
- `404` — `leave_id` no existe en SIGHU.

---

## Endpoint 2 — `POST /api/v1/odoo/vacaciones/importar/`

Importa una solicitud creada directamente en Odoo (upsert por `leave_id`).
**Crea** el registro si no existe; actualiza si ya existe.

### Request

```json
{
  "leave_id": 12345,               // requerido (clave de idempotencia)
  "sighu_uuid": "uuid-empleado",   // opcional
  "cedula": "1035831455",          // opcional (uno de los dos requerido)
  "fecha_inicio": "2026-08-01",
  "fecha_fin": "2026-08-15",
  "dias": 10,                      // informativo (SIGHU no valida)
  "tipo": "tiempo",                // "tiempo" (default) | "pago_dinero"
  "estado": "aprobada",            // "aprobada" | "cancelada"
  "motivo": "opcional",            // texto libre; se usa como motivo_rechazo si cancelada
  "aprobada_por": "user@odoo",     // opcional, se registra en observaciones
  "fecha_estado": "2026-06-30T14:00:00Z"  // opcional
}
```

### Respuestas

- `201 { status: "creado", sighu_uuid, leave_id, estado_local }` — nueva solicitud creada.
- `200 { status: "actualizado", ... }` — solicitud existente actualizada (cambió estado).
- `200 { status: "ya_procesado", ... }` — el estado enviado coincide (idempotente).
- `400` — payload inválido (leave_id faltante, fechas inválidas, estado no permitido).
- `404` — empleado no encontrado por `sighu_uuid` ni por `cedula`.

### Comportamiento clave

- **Identificación del empleado:** primero por `sighu_uuid`; si no matchea, por `cedula`
  (=`numero_documento`). Si ninguno matchea → 404. Debe enviarse al menos uno.
- **Idempotencia por `leave_id`:** reintentos del cron de Odoo (si SIGHU estaba caído)
  NO duplican registros ni notificaciones.
- **`jefe_solicitante`:** siempre NULL en este flujo (nació en Odoo, no en SIGHU).
- **`observaciones`:** se prellena con "Origen: Odoo (RRHH). Aprobada por: <user>."
- **Cancelación posterior:** llamar al mismo endpoint con `estado="cancelada"`.
  El `leave_id_odoo` no cambia, así que el empleado en el payload se ignora
  (mantiene el original).
- **Notificación al empleado:** cada transición terminal (aprobada/cancelada)
  dispara una notificación in-app al empleado. Idempotente: `ya_procesado` no notifica.

### Estados permitidos

Solo `aprobada` y `cancelada` en este endpoint. Los estados intermedios
(`borrador`, `enviada_pendiente_rrhh`) no aplican porque las solicitudes creadas
en Odoo llegan a SIGHU solo cuando ya son un hecho.

### Ejemplo — crear vacación pagada en dinero

```http
POST /api/v1/odoo/vacaciones/importar/
Authorization: Token <SIGHU_ODOO_TOKEN>
Content-Type: application/json

{
  "leave_id": 8891,
  "cedula": "1035831455",
  "fecha_inicio": "2026-08-01",
  "fecha_fin": "2026-08-10",
  "dias": 10,
  "tipo": "pago_dinero",
  "estado": "aprobada",
  "aprobada_por": "rrhh@construinmuniza.com"
}
```

Respuesta:

```json
{
  "status": "creado",
  "sighu_uuid": "b1c2...",
  "leave_id": 8891,
  "estado_local": "aprobada_rrhh"
}
```

### Ejemplo — cancelar la misma solicitud días después

```http
POST /api/v1/odoo/vacaciones/importar/
Authorization: Token <SIGHU_ODOO_TOKEN>
Content-Type: application/json

{
  "leave_id": 8891,
  "estado": "cancelada",
  "motivo": "Empleado renuncia antes de tomarla"
}
```

Respuesta:

```json
{
  "status": "actualizado",
  "sighu_uuid": "b1c2...",
  "leave_id": 8891,
  "estado_local": "cancelada_rrhh"
}
```
