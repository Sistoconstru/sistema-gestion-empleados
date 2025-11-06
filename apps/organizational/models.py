from django.db import models

# =============================================================================
# apps/organizational/models.py
# =============================================================================

from django.db import models

class Sede(models.Model):
    """Modelo para sedes de la empresa"""
    codigo = models.CharField(max_length=10, unique=True)  # Código único de la sede
    nombre = models.CharField(max_length=100)  # Nombre de la sede
    direccion = models.TextField()  # Dirección física
    ciudad = models.CharField(max_length=50)  # Ciudad donde está ubicada
    departamento = models.CharField(max_length=50)  # Departamento
    telefono = models.CharField(max_length=15)  # Teléfono de contacto
    activa = models.BooleanField(default=True)  # Estado activo/inactivo
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    
    class Meta:
        db_table = 'sedes'
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class AreaEmpresa(models.Model):
    """Modelo para áreas de la empresa"""
    codigo = models.CharField(max_length=20, unique=True)  # Código único del área
    nombre = models.CharField(max_length=100, unique=True)  # Nombre del área
    descripcion = models.TextField(blank=True)  # Descripción opcional
    area_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)  # Área superior (jerarquía)
    responsable = models.ForeignKey('employees.Empleado', on_delete=models.SET_NULL, null=True, blank=True)  # Empleado responsable
    activa = models.BooleanField(default=True)  # Estado activo/inactivo
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    
    class Meta:
        db_table = 'areas_empresa'
        verbose_name = 'Área de Empresa'
        verbose_name_plural = 'Áreas de Empresa'
    
    def __str__(self):
        return self.nombre

class Cargo(models.Model):
    """Modelo para cargos dentro de la empresa"""
    codigo = models.CharField(max_length=20, unique=True)  # Código único del cargo
    nombre = models.CharField(max_length=100)  # Nombre del cargo
    descripcion = models.TextField(blank=True)  # Descripción opcional
    area = models.ForeignKey(AreaEmpresa, on_delete=models.CASCADE)  # Área a la que pertenece el cargo
    cargo_jefe = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)  # Cargo jefe (jerarquía)
    nivel_jerarquico = models.IntegerField(default=1)  # Nivel jerárquico
    salario_minimo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Salario mínimo
    salario_maximo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Salario máximo
    requiere_licencia_conducir = models.BooleanField(default=False)  # Si requiere licencia de conducir
    requiere_certificado_alturas = models.BooleanField(default=False)  # Si requiere certificado de alturas
    activo = models.BooleanField(default=True)  # Estado activo/inactivo
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    
    # NUEVO CAMPO: Rol automático
    rol_automatico = models.ForeignKey(
        'authentication.Rol', 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        verbose_name="Rol del Sistema",
        help_text="Rol que se asigna automáticamente a empleados con este cargo"
    )
    
    class Meta:
        db_table = 'cargos'
        unique_together = ['nombre', 'area']
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
    
    def __str__(self):
        rol_info = f" → {self.rol_automatico.nombre}" if self.rol_automatico else ""
        return f"{self.nombre} - {self.area.nombre}{rol_info}"
