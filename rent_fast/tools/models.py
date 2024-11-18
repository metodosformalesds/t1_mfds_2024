from django.db import models
from users.models import Arrendador, Arrendatario
from rentas.models import Renta
from datetime import timedelta  

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre
        
class Tool(models.Model):
    arrendador = models.ForeignKey(Arrendador, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    costo_dia = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=[('Pendiente', 'Pendiente'), ('Disponible', 'Disponible'), ('Rechazado', 'Rechazado')], default='Pendiente')
    imagenes = models.ImageField(upload_to='tools/', null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    mensaje_rechazo = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre

    def is_available(self):
        """
        Verifica si la herramienta está disponible para rentar.
        Retorna False si está en una renta activa, True en caso contrario.
        """
        return not Renta.objects.filter(herramienta=self, estado="Activa").exists()


        
class Carrito(models.Model):
    arrendatario = models.ForeignKey(Arrendatario, on_delete=models.CASCADE)
    herramienta = models.ForeignKey('Tool', on_delete=models.CASCADE)
    fecha_agregada = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)

    def _str_(self):
        return f"{self.herramienta.nombre} en el carrito de {self.arrendatario}"
