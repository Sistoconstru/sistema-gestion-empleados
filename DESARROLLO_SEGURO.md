# DESARROLLO - NUEVAS FUNCIONALIDADES

## ⚠️ REGLAS CRÍTICAS PARA NO AFECTAR PRODUCCIÓN:

### ✅ QUE PUEDES HACER:
1. **Crear nuevas apps** en `apps/nuevas_funciones/`
2. **Agregar nuevos modelos** (creará nuevas tablas)
3. **Crear nuevas vistas y URLs** 
4. **Agregar nuevos templates**
5. **Instalar nuevas dependencias** (agregar a requirements.txt)
6. **Crear nuevas migraciones** para TUS nuevos modelos

### ❌ QUE NO DEBES HACER:
1. **NO modificar modelos existentes** (employees, documents, etc.)
2. **NO cambiar migraciones existentes**
3. **NO modificar URLs existentes**
4. **NO cambiar templates existentes** sin crear copia
5. **NO modificar settings de producción** directamente

### 🔄 FLUJO DE DESARROLLO SEGURO:

1. **Desarrollo local**: Rama `desarrollo-nuevas-funciones`
2. **Nuevas funciones**: Solo en `apps/nuevas_funciones/`
3. **Testing local**: Con tu BD restaurada
4. **Commit por funcionalidad**: Commits atómicos y descriptivos
5. **Push a rama específica**: NO a main/producción
6. **Deploy selectivo**: Solo los archivos nuevos

### 📁 ESTRUCTURA RECOMENDADA:
```
apps/nuevas_funciones/
├── __init__.py
├── modulo_inventario/     # Ejemplo: nueva funcionalidad
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── modulo_reportes/       # Ejemplo: otra funcionalidad
│   ├── models.py
│   └── ...
└── utils/                 # Utilidades compartidas
    └── helpers.py
```

### 🚀 COMANDOS SEGUROS:
```bash
# Solo nuevos modelos/apps
python manage.py makemigrations nuevas_funciones

# Aplicar solo TUS migraciones
python manage.py migrate nuevas_funciones

# Ver qué va a subir (antes de push)
git diff --name-only
```

### 📝 ANTES DE CADA COMMIT:
1. Verificar que no modificaste archivos existentes
2. Probar que no rompe funcionalidad actual
3. Documentar qué agrega la nueva funcionalidad