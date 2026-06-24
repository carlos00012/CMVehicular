from django.db import models

# Create your models here.

class Vehiculo(models.Model):
    id = models.AutoField(primary_key=True)
    foto = models.ImageField(upload_to='vehiculos/')
    placa = models.CharField(max_length=20)
    tipo_vehiculo = models.CharField(max_length=20)
    tipo_combustible = models.CharField(max_length=20)
    seguro_vigente = models.BooleanField()
    anio_modelo = models.IntegerField()

    def __str__(self):return f"{self.placa} - {self.tipo_vehiculo} - {self.tipo_combustible} - Seguro vigente: {self.seguro_vigente} - Año modelo: {self.anio_modelo}"


class Mantenimiento(models.Model):
    id = models.AutoField(primary_key=True)
    vehiculo = models.ForeignKey('Vehiculo',on_delete=models.CASCADE,null=True, blank=True)
    pdf = models.FileField(upload_to='mantenimientos/')
    fecha_servicio = models.DateField()
    costo_taller = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    tipo_mantenimiento = models.CharField(
        max_length=20
    )
    repuestos_cambiados = models.TextField()
    def __str__(self):
        return f"{self.vehiculo.placa} - {self.tipo_mantenimiento} - {self.fecha_servicio} - Costo: {self.costo_taller} - Repuestos: {self.repuestos_cambiados}"

