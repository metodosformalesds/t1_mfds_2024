# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Modelo para la dirección
class Direccion(models.Model):
    calle = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.calle}, {self.ciudad}, {self.estado}, {self.codigo_postal}"

# Modelo de Arrendador
class Arrendador(models.Model):
    nombre = models.CharField(max_length=100)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # FK al usuario autenticado
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField()
    is_verificado = models.BooleanField(default=True)  # por defecto es True
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} {self.apellidos} (Arrendador)"

# Modelo de Arrendatario
class Arrendatario(models.Model):
    nombre = models.CharField(max_length=100)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # FK al usuario autenticado
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField()
    is_verificado = models.BooleanField(default=True)  # por defecto es True
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} {self.apellidos} (Arrendatario)"

