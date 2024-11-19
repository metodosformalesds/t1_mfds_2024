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
    arrendador = models.ForeignKey('users.Arrendador', on_delete=models.CASCADE, null=True, blank=True)
    arrendatario = models.ForeignKey('users.Arrendatario', on_delete=models.CASCADE, null=True, blank=True)
    herramienta = models.ForeignKey('tools.Tool', on_delete=models.CASCADE, null=True, blank=True)
    renta = models.ForeignKey(Renta, on_delete=models.CASCADE, null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    oculto_arrendador = models.BooleanField(default=False)
    oculto_arrendatario = models.BooleanField(default=False)
    es_soporte = models.BooleanField(default=False)

class Mensaje(models.Model):
    chat = models.ForeignKey(Chat, related_name='mensajes', on_delete=models.CASCADE)
    remitente = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField(blank=True, null=True) 
    enviado = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to='chat_archivos/', blank=True, null=True)  # Campo para archivos o imágenes


class Pregunta(models.Model):
    herramienta = models.ForeignKey('tools.Tool', on_delete=models.CASCADE, related_name="preguntas")
    arrendatario = models.ForeignKey(Arrendatario, on_delete=models.CASCADE)
    pregunta_texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pregunta sobre {self.herramienta.nombre} - {self.pregunta_texto[:30]}..."

    @property
    def tiene_respuesta(self):
        return hasattr(self, 'respuesta')  # Devuelve True si tiene una respuesta asociada

class Respuesta(models.Model):
    pregunta = models.OneToOneField(Pregunta, on_delete=models.CASCADE, related_name="respuesta")
    arrendador = models.ForeignKey(Arrendador, on_delete=models.CASCADE)
    respuesta_texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Respuesta a pregunta sobre {self.pregunta.herramienta.nombre}"
    
class Resena(models.Model):
    CALIFICACIONES = [(i, str(i)) for i in range(1, 6)]  # Calificación del 1 al 5
    arrendatario = models.ForeignKey(Arrendatario, on_delete=models.CASCADE)
    herramienta = models.ForeignKey('tools.Tool', on_delete=models.CASCADE)
    comentario = models.TextField()
    calificacion = models.IntegerField(choices=CALIFICACIONES, default=0)  # Cambia aquí
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('arrendatario', 'herramienta')

    def __str__(self):
        return f"Reseña de {self.arrendatario} para {self.herramienta.nombre}"