# rentas/models.py
from django.db import models
from users.models import Arrendador, Arrendatario
from django.contrib.auth.models import User



class Renta(models.Model):
    """
    Daniel Esqueda
    Representa una renta de herramienta realizada por un arrendatario.

    Atributos:
    herramienta (ForeignKey): Referencia a la herramienta que se está rentando.
    arrendatario (ForeignKey): Referencia al arrendatario que alquila la herramienta.
    fecha_inicio (DateField): Fecha de inicio de la renta.
    fecha_fin (DateField): Fecha de finalización de la renta.
    horas (PositiveIntegerField): Número de horas de la renta (opcional).
    costo_total (DecimalField): Costo total de la renta calculado automáticamente.
    estado (CharField): Estado de la renta, ya sea 'Activa' o 'Finalizada'.
    """
    herramienta = models.ForeignKey('tools.Tool', on_delete=models.CASCADE)  # Referencia como cadena
    arrendatario = models.ForeignKey(Arrendatario, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    horas = models.PositiveIntegerField(null=True, blank=True)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=[("Activa", "Activa"), ("Finalizada", "Finalizada")])

    def calcular_costo_total(self):
        """
        Calcula el costo total de la renta basado en los días de alquiler.

        Returns:
        float: El costo total de la renta.
        """
        dias_renta = (self.fecha_fin - self.fecha_inicio).days + 1
        return dias_renta * self.herramienta.costo_dia

    def save(self, *args, **kwargs):
        """
        Guarda la instancia de Renta, asegurándose de que el costo total esté calculado.

        Si no se proporciona un costo_total, se calculará automáticamente usando `calcular_costo_total()`.
        """
        if not self.costo_total:
            self.costo_total = self.calcular_costo_total()
        super().save(*args, **kwargs)

class Chat(models.Model):
    """
    Daniel Esqueda
    Representa una conversación entre un arrendador y un arrendatario.

    Atributos:
    arrendador (ForeignKey): Referencia al arrendador que participa en el chat (opcional).
    arrendatario (ForeignKey): Referencia al arrendatario que participa en el chat (opcional).
    herramienta (ForeignKey): Referencia a la herramienta relacionada al chat (opcional).
    renta (ForeignKey): Referencia a la renta asociada con el chat (opcional).
    creado (DateTimeField): Fecha y hora en que se creó el chat.
    oculto_arrendador (BooleanField): Indica si el chat está oculto para el arrendador.
    oculto_arrendatario (BooleanField): Indica si el chat está oculto para el arrendatario.
    es_soporte (BooleanField): Indica si el chat es para soporte.
    """
    arrendador = models.ForeignKey('users.Arrendador', on_delete=models.CASCADE, null=True, blank=True)
    arrendatario = models.ForeignKey('users.Arrendatario', on_delete=models.CASCADE, null=True, blank=True)
    herramienta = models.ForeignKey('tools.Tool', on_delete=models.CASCADE, null=True, blank=True)
    renta = models.ForeignKey(Renta, on_delete=models.CASCADE, null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    oculto_arrendador = models.BooleanField(default=False)
    oculto_arrendatario = models.BooleanField(default=False)
    es_soporte = models.BooleanField(default=False, null=True, blank=True )

class Mensaje(models.Model):
    """
    Daniel Esqueda
    Representa un mensaje enviado dentro de un chat entre un arrendador y un arrendatario.

    Atributos:
    chat (ForeignKey): Referencia al chat donde se envió el mensaje.
    remitente (ForeignKey): Usuario que envía el mensaje.
    contenido (TextField): Contenido del mensaje.
    enviado (DateTimeField): Fecha y hora en que se envió el mensaje.
    archivo (FileField): Archivo adjunto al mensaje, como imágenes o documentos.
    """
    chat = models.ForeignKey(Chat, related_name='mensajes', on_delete=models.CASCADE)
    remitente = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField(blank=True, null=True) 
    enviado = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to='chat_archivos/', blank=True, null=True)  # Campo para archivos o imágenes


class Pregunta(models.Model):
    """
    Daniel Esqueda
    Representa una pregunta realizada por un arrendatario sobre una herramienta.

    Atributos:
    herramienta (ForeignKey): Herramienta sobre la que se hace la pregunta.
    arrendatario (ForeignKey): El arrendatario que realiza la pregunta.
    pregunta_texto (TextField): El texto de la pregunta.
    fecha_creacion (DateTimeField): Fecha de creación de la pregunta.
    """
    herramienta = models.ForeignKey('tools.Tool', on_delete=models.CASCADE, related_name="preguntas")
    arrendatario = models.ForeignKey(Arrendatario, on_delete=models.CASCADE)
    pregunta_texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pregunta sobre {self.herramienta.nombre} - {self.pregunta_texto[:30]}..."

    @property
    def tiene_respuesta(self):
        """
        Verifica si la pregunta tiene una respuesta asociada.

        Returns:
        bool: True si tiene una respuesta asociada, False en caso contrario.
        """
        return hasattr(self, 'respuesta')  # Devuelve True si tiene una respuesta asociada

class Respuesta(models.Model):
    """
    Daniel Esqueda
    Representa una respuesta dada por un arrendador a una pregunta de un arrendatario.

    Atributos:
    pregunta (OneToOneField): La pregunta que está siendo respondida.
    arrendador (ForeignKey): El arrendador que proporciona la respuesta.
    respuesta_texto (TextField): El texto de la respuesta.
    fecha_creacion (DateTimeField): Fecha en que se creó la respuesta.
    """
    pregunta = models.OneToOneField(Pregunta, on_delete=models.CASCADE, related_name="respuesta")
    arrendador = models.ForeignKey(Arrendador, on_delete=models.CASCADE)
    respuesta_texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Respuesta a pregunta sobre {self.pregunta.herramienta.nombre}"
    
class Resena(models.Model):
    """
    Juan Carlos, Manuel Villareal
    Representa una reseña realizada por un arrendatario sobre una herramienta.

    Atributos:
    arrendatario (ForeignKey): El arrendatario que realiza la reseña.
    herramienta (ForeignKey): Herramienta sobre la cual se realiza la reseña.
    comentario (TextField): Comentarios del arrendatario sobre la herramienta.
    calificacion (IntegerField): Calificación de la herramienta, de 1 a 5.
    fecha_creacion (DateTimeField): Fecha de creación de la reseña.
    """
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