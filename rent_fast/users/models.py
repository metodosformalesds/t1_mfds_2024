from django.db import models

# Create your models here.
class Users(models.Model):
username = models.CharField(max_length=150, unique=True)
email = models.EmailField(unique=True)
first_name = models.CharField(max_length=30)
last_name = models.CharField(max_length=30)= models.DateTimeField(auto_now_add=True)
def __str__(self):
return self.username

# Usuario Arrendador

from django.db import models
from django.contrib.auth.models import User 
# Importa el modelo base de usuario
class Arrendador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
#Relación con el modelo User
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False) 
# Verificación del arrendador
    def __str__(self):
         return f"{self.user.username} - Verificado:
{self.is_verified}"


 from django.db import models
 from django.contrib.auth.models import User # Importa el modelo
 base de usuario
 class Arrendatario(models.Model):
 user = models.OneToOneField(User, on_delete=models.CASCADE)
 telefono = models.CharField(max_length=15)
 direccion = models.CharField(max_length=255)
 is_verified = models.BooleanField(default=False) # Verificación
 del arrendatario
 def __str__(self):
 return f"{self.user.username}- Verificado:
 {self.is_verified}"

