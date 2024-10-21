from django.db import models
from django.contrib.auth.models import User

class Direccion(models.Model):
    calle = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.calle}, {self.ciudad}, {self.estado}, {self.codigo_postal}"

class Arrendador(models.Model):
    nombre = models.CharField(max_length=100)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField()
    is_verificado = models.BooleanField(default=False)
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    ine_image = models.ImageField(upload_to="ine_images", null=True, blank=True, verbose_name="INE")  # Guardar la imagen de INE

    def __str__(self):
        return f"{self.nombre} {self.apellidos} (Arrendador)"

class Arrendatario(models.Model):
    nombre = models.CharField(max_length=100)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField()
    is_verificado = models.BooleanField(default=False)
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    ine_image = models.ImageField(upload_to="ine_images", null=True, blank=True, verbose_name="INE")  # Guardar la imagen de INE

    def __str__(self):
        return f"{self.nombre} {self.apellidos} (Arrendatario)"
