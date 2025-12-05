# 🚀 Deployment Automático en Railway

## Cómo funciona

Cuando haces deploy en Railway, se ejecuta automáticamente `start.sh`:

```bash
start.sh ejecuta:
1. python manage.py migrate          → Crea/actualiza tablas de BD
2. python manage.py configurar_evaluaciones_iniciales  → Popula evaluaciones
3. python manage.py collectstatic    → Prepara archivos estáticos
4. gunicorn config.wsgi              → Inicia la aplicación
```

## Qué se popula automáticamente

El comando `configurar_evaluaciones_iniciales` crea:

✅ **3 Tipos de Evaluación:**
- Evaluación Período de Prueba
- Evaluación Anual de Desempeño
- Autoevaluación de Desempeño

✅ **7 Preguntas de Período de Prueba:**
1. Trabajo en equipo
2. Compromiso
3. Comunicación
4. Atención al detalle
5. Cumplimiento de normas y procedimientos
6. Actitud respecto al trabajo
7. Calidad

✅ **21 Opciones** (3 opciones × 7 preguntas)
- Cada opción contiene: Observación + Recomendación + Ejemplo del documento

## Configuración en Railway

1. **Conectar GitHub:**
   - Dashboard de Railway → Settings → Source → GitHub
   - Seleccionar repositorio

2. **Variables de entorno necesarias:**
   ```
   DEBUG=False
   SECRET_KEY=tu-clave-secreta
   ALLOWED_HOSTS=tu-app.railway.app
   DATABASE_URL=postgresql://...
   AWS_ACCESS_KEY_ID=...
   AWS_SECRET_ACCESS_KEY=...
   AWS_STORAGE_BUCKET_NAME=...
   ```

3. **Base de datos:**
   - Agregar PostgreSQL plugin → Railway configura `DATABASE_URL` automáticamente

4. **Deploy automático:**
   - Cada push a `main` o `feature/*` dispara un nuevo deploy
   - Railway ejecuta `start.sh` automáticamente

## Validar que funcionó

Después del deploy:

1. Ver logs de Railway:
   ```
   Buscar: "✅ Configuración de evaluaciones completada exitosamente"
   ```

2. En la app:
   - Ir a `/admin/evaluations/` 
   - Verificar que existen las evaluaciones

3. Via SSH (opcional):
   ```bash
   railway run python manage.py shell
   >>> from apps.evaluations.models import OpcionEvaluacion
   >>> OpcionEvaluacion.objects.count()
   21  # Debe ser 21
   ```

## Notas importantes

- El comando es **idempotente**: Si ya existen los datos, no los vuelve a crear
- Si necesitas resetear los datos, elimina manualmente en railway y redeploy
- Los datos se crean **solo una vez** en cada deploy (no en cada reinicio)
- El comando tardará ~5-10 segundos en ejecutarse

## Archivos involucrados

- **start.sh** - Script que ejecuta Railway en cada deploy
- **apps/evaluations/management/commands/configurar_evaluaciones_iniciales.py** - Comando que popula BD
- **apps/evaluations/management/commands/actualizar_opciones_documento.py** - Comando auxiliar para actualizar opciones
