from django.db import models
from django.contrib.auth.models import User

class Direccion(models.Model):
    """
    Modelo para almacenar la dirección del usuario.
    """
    calle = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.calle}, {self.ciudad}, {self.estado}, {self.codigo_postal}"

class Arrendador(models.Model):
    """
    Modelo para almacenar la información de un arrendador.
    Incluye campos para el nombre, usuario, apellidos, teléfono, correo,
    estado de verificación, dirección y documentos de identificación (INE y foto de perfil).
    """
    nombre = models.CharField(max_length=100)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='arrendador')
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField()
    is_verificado = models.BooleanField(default=False)
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    ine_image = models.ImageField(
        upload_to="ine_images", 
        null=True, 
        blank=True, 
        verbose_name="INE"
    )  # Guardar la imagen de INE
    profile_picture = models.ImageField(upload_to="profile_pictures", null=True, blank=True, verbose_name="Foto de Perfil")


    def __str__(self):
        return f"{self.nombre} {self.apellidos} (Arrendador)"

class Arrendatario(models.Model):
    """
    Modelo para almacenar la información de un arrendatario.
    Similar al arrendador, este modelo incluye campos para el nombre, usuario, apellidos,
    teléfono, correo, estado de verificación, dirección y documentos de identificación.
    """
    nombre = models.CharField(max_length=100)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='arrendatario')
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField()
    is_verificado = models.BooleanField(default=False)
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    ine_image = models.ImageField(
        upload_to="ine_images", 
        null=True, 
        blank=True, 
        verbose_name="INE"
    )  # Guardar la imagen de INE
    profile_picture = models.ImageField(upload_to="profile_pictures", null=True, blank=True, verbose_name="Foto de Perfil")


    def __str__(self):
        return f"{self.nombre} {self.apellidos} (Arrendatario)"

class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.usuario.username}: {self.mensaje[:30]}..."
    
from tools.models import Tool  # Importa el modelo de herramienta

class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    herramienta = models.ForeignKey(Tool, on_delete=models.CASCADE, null=True, blank=True)  # Relación con Tool
    leido = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.usuario.username}: {self.mensaje[:30]}..."

