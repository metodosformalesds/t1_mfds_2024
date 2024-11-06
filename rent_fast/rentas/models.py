# rentas/models.py
from django.db import models
from users.models import Arrendador, Arrendatario
from django.contrib.auth.models import User

class Renta(models.Model):
    herramienta = models.ForeignKey('tools.Tool', on_delete=models.CASCADE)  # Referencia como cadena
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

class Chat(models.Model):
    arrendador = models.ForeignKey('users.Arrendador', on_delete=models.CASCADE)
    arrendatario = models.ForeignKey('users.Arrendatario', on_delete=models.CASCADE)
    herramienta = models.ForeignKey('tools.Tool', on_delete=models.CASCADE)
    renta = models.ForeignKey(Renta, on_delete=models.CASCADE)  # Add this line to link Chat with Renta
    creado = models.DateTimeField(auto_now_add=True)


class Mensaje(models.Model):
    chat = models.ForeignKey(Chat, related_name='mensajes', on_delete=models.CASCADE)
    remitente = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    enviado = models.DateTimeField(auto_now_add=True)