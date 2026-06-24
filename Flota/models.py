from django.db import models
from django.contrib.auth.models import User

class Vehiculo(models.Model):
    id = models.AutoField(primary_key=True)
    foto = models.ImageField(upload_to='vehiculos/', blank=True, null=True)
    placa = models.CharField(max_length=20)
    tipo_vehiculo = models.CharField(max_length=20)
    tipo_combustible = models.CharField(max_length=20)
    seguro_vigente = models.BooleanField(default=False)
    anio_modelo = models.IntegerField()
    
    # alertas de vencimiento
    fecha_vencimiento_seguro = models.DateField(null=True, blank=True)
    fecha_vencimiento_soat = models.DateField(null=True, blank=True)
    
    #  asignar a chofer
    asignado_a = models.ForeignKey('PerfilUsuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehiculos_asignados')

    def __str__(self):
        return f"{self.placa} - {self.tipo_vehiculo}"

class Mantenimiento(models.Model):
    id = models.AutoField(primary_key=True)
    vehiculo = models.ForeignKey('Vehiculo', on_delete=models.CASCADE, null=True, blank=True)
    pdf = models.FileField(upload_to='mantenimientos/')
    fecha_servicio = models.DateField()
    costo_taller = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_mantenimiento = models.CharField(max_length=20)
    repuestos_cambiados = models.TextField()
    
    # estado de aprobación
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Aprobación'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('completado', 'Completado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    aprobado_por = models.ForeignKey('PerfilUsuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='mantenimientos_aprobados')
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.vehiculo.placa} - {self.tipo_mantenimiento} - {self.fecha_servicio}"

# Perfil de Usuario
class PerfilUsuario(models.Model):
    TIPO_PERFIL = [
        ('gerente', 'Gerente de Operaciones'),
        ('chofer', 'Chofer'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_perfil = models.CharField(max_length=20, choices=TIPO_PERFIL)
    telefono = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_perfil_display()}"

# Reporte de Fallas (para choferes)
class ReporteFalla(models.Model):
    GRAVEDAD_CHOICES = [
        ('leve', 'Leve'),
        ('moderada', 'Moderada'),
        ('grave', 'Grave'),
        ('critica', 'Crítica'),
    ]
    
    vehiculo = models.ForeignKey('Vehiculo', on_delete=models.CASCADE)
    chofer = models.ForeignKey('PerfilUsuario', on_delete=models.CASCADE)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    gravedad = models.CharField(max_length=20, choices=GRAVEDAD_CHOICES, default='moderada')
    foto = models.ImageField(upload_to='reportes_fallas/', blank=True, null=True)
    archivo_adjunto = models.FileField(upload_to='reportes_fallas/archivos/', blank=True, null=True)
    estado = models.CharField(max_length=20, default='registrado')
    
    def __str__(self):
        return f"{self.titulo} - {self.vehiculo.placa}"