# Integración SIGHU ↔ Odoo — Beneficios de retención en la fuente

Estado en SIGHU: **listo**. Módulo desplegado con la Fase 1 (soportes de vivienda,
medicina prepagada y dependientes). Aportes voluntarios y AFC quedan para una
segunda entrega cuando aclaremos el punto §8.1 del contrato de Odoo (si la
empresa los descuenta por nómina o si el empleado los paga por su cuenta).

Pendiente en Odoo: implementar el endpoint `POST /sighu_sync/webhook/beneficio_retencion`.

## Cómo llama SIGHU

Contrato tal como fue propuesto por Odoo (30/09/2026), sin cambios de estructura.

- URL: `POST <ODOO_BASE_URL>/sighu_sync/webhook/beneficio_retencion`.
- Auth: `Authorization: Token <SIGHU_ODOO_TOKEN>` (el mismo del endpoint de
  empleados y vacaciones).
- `Content-Type: application/json`.
- Soportes embebidos en base64, máximo 10 MB por archivo (SIGHU valida en la
  carga del empleado).

### Payload — trámite común

```json
{
  "tramite_uuid": "9f1c8ad2-5b6e-4a11-9c33-7d0a2f4e8b10",
  "sighu_uuid": "6114fa94-c620-4b19-ae72-763156ece5ea",
  "numero_documento": "1017190664",
  "tipo": "intereses_vivienda",
  "anio_aplicacion": 2026,
  "periodo_certificado": 2025,
  "valor": 12480000,
  "periodicidad": "anual",
  "estado": "validado",
  "validado_por": "Yuliana Restrepo",
  "validado_el": "2026-01-20",
  "observacion": "Certificado Bancolombia, crédito 4400-123456.",
  "soportes": [
    {
      "nombre": "Certificado intereses 2025 - Bancolombia.pdf",
      "tipo_mime": "application/pdf",
      "contenido_base64": "JVBERi0xLjQK..."
    }
  ]
}
```

### Payload — dependientes

Cuando `tipo="dependientes"`, se omiten `valor` y `periodicidad`. Se envía la
lista de dependientes con sus soportes específicos:

```json
{
  "tramite_uuid": "...",
  "sighu_uuid": "...",
  "numero_documento": "43105870",
  "tipo": "dependientes",
  "anio_aplicacion": 2026,
  "periodo_certificado": 2026,
  "estado": "validado",
  "validado_por": "Yuliana Restrepo",
  "validado_el": "2026-02-03",
  "observacion": "",
  "dependientes": [
    {
      "nombre": "Juan Pablo Orrego Henao",
      "numero_documento": "1042771560",
      "parentesco": "hijo",
      "causal": "hijo_18_23_estudiando",
      "soportes": [{"nombre": "Certif estudio 2026.pdf",
                    "tipo_mime": "application/pdf",
                    "contenido_base64": "..."}]
    }
  ],
  "soportes": [
    {"nombre": "Carta juramentada.pdf",
     "tipo_mime": "application/pdf",
     "contenido_base64": "..."}
  ]
}
```

### Payload — revocación

Con el mismo `tramite_uuid` del beneficio que se revoca:

```json
{
  "tramite_uuid": "9f1c8ad2-5b6e-4a11-9c33-7d0a2f4e8b10",
  "sighu_uuid": "6114fa94-c620-4b19-ae72-763156ece5ea",
  "numero_documento": "1017190664",
  "tipo": "medicina_prepagada",
  "anio_aplicacion": 2026,
  "periodo_certificado": 2025,
  "estado": "revocado",
  "validado_por": "Yuliana Restrepo",
  "validado_el": "2026-07-15",
  "observacion": "El empleado canceló la póliza en junio.",
  "soportes": []
}
```

## Cómo SIGHU maneja la respuesta

- `200 OK` con `odoo_id`, `aplica_desde`, `vence_el` → SIGHU guarda esos tres
  campos en el trámite y notifica al empleado para que firme la carta
  juramentada.
- `200 OK` con `repetido: true` → SIGHU trata idéntico al caso anterior. Nada
  se duplica en SIGHU tampoco.
- `4xx` con `error` y `detalle` → SIGHU deja el trámite en estado
  `error_envio_odoo` y muestra el detalle al usuario de RRHH. Se puede
  reintentar manualmente desde el panel una vez corregido lo que sea.
- `5xx` o timeout → mismo estado `error_envio_odoo`. RRHH reintenta desde el
  panel. La operación es idempotente por `tramite_uuid`.

## Configuración

En el servicio Railway (`sighu-web`) hay que setear:

- `SIGHU_ODOO_TOKEN`: token compartido con Odoo (ya existe).
- `ODOO_BASE_URL`: URL base del servicio Odoo (ej. `https://odoo.construinmuniza.com`).
- `ODOO_HTTP_TIMEOUT`: opcional, default 30s.

## Flujo del lado SIGHU

1. Empleado entra a su perfil y ve el botón "¿Eres declarante?". Confirma → se
   marca `Empleado.es_declarante=True`.
2. Empleado entra al módulo Beneficios de retención y carga un trámite con
   sus soportes (vivienda / medicina / dependientes).
3. Estado inicial: `pendiente_rrhh`.
4. RRHH revisa desde `/beneficios-retencion/rrhh/`:
   - **Validar** → SIGHU llama a Odoo con `estado=validado` y todos los
     soportes en base64. Si Odoo responde 200 → estado `validado`, se
     notifica al empleado para que firme la carta.
   - **Rechazar** → estado `rechazado`. NO se llama a Odoo (según §8.4 del
     contrato). Se notifica al empleado con el motivo.
   - **Revocar** (solo para trámites ya validados) → SIGHU llama a Odoo con
     `estado=revocado` y mismo `tramite_uuid`.
5. Botón "Imprimir carta juramentada" genera el PDF (formato genérico
   ajustable). RRHH lo imprime y marca "carta firmada" cuando el empleado la
   firma físicamente.

## Casos de prueba corridos (SIGHU, Fase 1)

10 checks locales en verde:
- URLs resuelven.
- Modal marca `es_declarante` y redirige.
- Empleado no-declarante queda bloqueado del módulo.
- Alta de trámite vivienda con soporte único.
- Alta de trámite dependientes con 2 dependientes y sus soportes.
- Cancelación de trámite pendiente.
- Bandeja RRHH y detalle responden 200.
- Rechazo con motivo obligatorio.
- Generación del PDF de la carta juramentada.
- Armado del payload Odoo con soportes en base64.

## Pendientes coordinados con Odoo

Del §8 del contrato Odoo:

1. **Aportes voluntarios (AFP + AFC)**: pendiente confirmar si la empresa los
   descuenta por nómina. Mientras tanto, esos dos tipos existen en el modelo
   pero no se ofrecen en el formulario del empleado.
2. **1% por facturas electrónicas**: no aplica en nómina. No se implementa en
   SIGHU.
3. **Campaña de carga**: pendiente definir fecha y recordatorios (Fase 4).
4. **Rechazados**: SIGHU no los envía a Odoo, quedan solo en SIGHU con
   observación (según §8.4).
