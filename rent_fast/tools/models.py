from django.db import models
from users.models import Arrendador  

class Tool(models.Model):
    arrendador = models.ForeignKey(Arrendador, on_delete=models.CASCADE)  # Relación con Arrendador
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    costo_hora = models.DecimalField(max_digits=10, decimal_places=2)
    costo_dia = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=100)  # Ej: "Disponible", "No disponible", etc.
    imagenes = models.ImageField(upload_to='tools/', null=True, blank=True)

    def __str__(self):
        return self.nombre

    @property
    def direccion(self):
        # Devolver la dirección del arrendador asociado
        return self.arrendador.direccion
class Renta(models.Model):
    herramienta = models.ForeignKey('Tool', on_delete=models.CASCADE)
    arrendatario = models.ForeignKey(Arrendatario, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    horas = models.PositiveIntegerField(null=True, blank=True)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=[("Activa", "Activa"), ("Finalizada", "Finalizada")])

    def calcular_costo_total(self):
        dias_renta = (self.fecha_fin - self.fecha_inicio).days + 1
        return dias_renta * self.herramienta.costo_dia

    def save(self, *args, **kwargs):
        if not self.costo_total:
            self.costo_total = self.calcular_costo_total()
        super().save(*args, **kwargs)