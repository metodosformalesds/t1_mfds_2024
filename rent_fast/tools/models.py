from django.db import models
from users.models import Arrendador, Arrendatario
from datetime import timedelta  

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
