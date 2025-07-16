from django.db import models

# Create your models here.
# =============================================================================
# apps/organizational/models.py
# =============================================================================

from django.db import models

class Sede(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=50)
    departamento = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sedes'
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class AreaEmpresa(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    area_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    responsable = models.ForeignKey('employees.Empleado', on_delete=models.SET_NULL, null=True, blank=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'areas_empresa'
        verbose_name = 'Área de Empresa'
        verbose_name_plural = 'Áreas de Empresa'
    
    def __str__(self):
        return self.nombre

class Cargo(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    area = models.ForeignKey(AreaEmpresa, on_delete=models.CASCADE)
    cargo_jefe = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    nivel_jerarquico = models.IntegerField(default=1)
    salario_minimo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salario_maximo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    requiere_licencia_conducir = models.BooleanField(default=False)
    requiere_certificado_alturas = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
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
