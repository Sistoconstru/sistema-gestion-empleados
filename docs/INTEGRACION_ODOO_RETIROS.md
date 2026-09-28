# Integración Odoo ↔ SIGHU — Retiros / Inactivación

Endpoint que consume Odoo cuando RRHH registra la fecha de terminación en el
contrato. Sustituye al flujo anterior donde SIGHU informaba a Odoo del cambio
de estado (que no traía `fecha_retiro` y por eso Odoo no podía liquidar).

Contraparte: propuesta del equipo Odoo Construinmuniza del 28/09/2026.

---

## Endpoint

`POST /api/v1/odoo/empleados/inactivar/`

Autenticación: `Authorization: Token <SIGHU_ODOO_TOKEN>` — el mismo token que
usan los endpoints de vacaciones.

### Request

```json
{
  "sighu_uuid": "6114fa94-c620-4b19-ae72-763156ece5ea",
  "numero_documento": "71525952",
  "fecha_retiro": "2026-09-20",
  "motivo": "terminacion_contrato",
  "observacion": "Terminación de contrato a término indefinido.",
  "origen": "odoo"
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `sighu_uuid` | string UUID | uno de los dos | Identificador de Empleado en SIGHU (llave principal). |
| `numero_documento` | string | uno de los dos | Cédula; se usa como respaldo si `sighu_uuid` no matchea (conciliación). |
| `fecha_retiro` | `YYYY-MM-DD` | sí | Último día laborado. Puede ser fecha del pasado. |
| `motivo` | string | sí | Uno de la tabla de abajo. |
| `observacion` | string | no | Texto libre de RRHH. |
| `origen` | string | sí | Siempre `"odoo"`. |

### Valores permitidos de `motivo`

| Código | Descripción |
|---|---|
| `terminacion_contrato` | Contrato a término indefinido, obra o labor, o prestación con fecha de terminación. |
| `vencimiento_termino_fijo` | Contrato a término fijo vencido con preaviso de no prórroga. |
| `fin_aprendizaje` | Terminó el contrato de aprendizaje. |
| `otro` | Cualquier otro caso; el detalle va en `observacion`. |

### Respuestas

| Código | Cuerpo | Significado |
|---|---|---|
| `200` | `{"ok": true, "sighu_uuid": "...", "estado": "RETIRADO", "fecha_retiro": "2026-09-20"}` | Retirado correctamente (o actualizada la fecha/motivo de un retiro previo). |
| `200` | `{"ok": true, "ya_inactivo": true, "sighu_uuid": "...", "estado": "RETIRADO", "fecha_retiro": "2026-09-20"}` | Ya estaba retirado con esa misma fecha y motivo. Odoo puede tratarlo como éxito. |
| `400` | `{"ok": false, "error": "detalle"}` | Payload inválido (motivo no permitido, fecha mal formada, falta `origen`, etc.). No reintentar. |
| `401` | — | Token ausente o inválido. |
| `404` | `{"ok": false, "error": "empleado no encontrado"}` | Ni `sighu_uuid` ni `numero_documento` matchearon. No reintentar; alertar a RRHH. |
| `500` / sin respuesta | — | Error transitorio; Odoo puede reintentar. |

### Idempotencia y correcciones

- Repetir la misma llamada (mismo empleado, misma `fecha_retiro`, mismo `motivo`)
  responde `200` con `ya_inactivo: true` sin duplicar nada.
- Si `fecha_retiro` o `motivo` cambian (RRHH corrigió), la llamada devuelve
  `200` normal y SIGHU sobrescribe con los nuevos valores.

### Comportamiento en SIGHU

- Empleado queda con `estado.codigo = "RETIRADO"` (bloquea acceso al sistema).
- Guarda `Empleado.fecha_retiro`, `Empleado.motivo_retiro`, `Empleado.observacion_retiro`.
- Semánticamente `RETIRADO` reemplaza a `INACTIVO` para retiros laborales:
  `INACTIVO` sigue existiendo pero se reserva para inactivaciones administrativas
  (no laborales) hechas dentro de SIGHU.

### Reactivaciones

No hay endpoint de reactivación desde Odoo. Si un empleado vuelve a entrar, el
alta se hace en SIGHU como empleado nuevo (o el flujo interno de RRHH lo
reactiva). Odoo tratará ese caso como contrato nuevo, según lo acordado.

---

## Ejemplo con `curl`

```bash
curl -X POST https://sighu.construinmuniza.com/api/v1/odoo/empleados/inactivar/ \
  -H "Authorization: Token $SIGHU_ODOO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sighu_uuid": "6114fa94-c620-4b19-ae72-763156ece5ea",
    "numero_documento": "71525952",
    "fecha_retiro": "2026-09-20",
    "motivo": "terminacion_contrato",
    "observacion": "Terminación de contrato a término indefinido.",
    "origen": "odoo"
  }'
```
