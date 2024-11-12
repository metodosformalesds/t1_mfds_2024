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
# rentas/urls.py
from django.urls import path
from .views import iniciar_pago_view,preguntas_sin_responder_view, pago_exitoso_view, pago_cancelado_view, ver_chat_view, listar_chats_view, rentas_arrendador_view, rentas_arrendatario_view, finalizar_renta_view

urlpatterns = [
    path("pago/", iniciar_pago_view, name="iniciar_pago"),
    path("pago/exitoso/", pago_exitoso_view, name="pago_exitoso"),
    path("pago/cancelado/", pago_cancelado_view, name="pago_cancelado"),
    path('<int:chat_id>/', ver_chat_view, name='ver_chat'),
    path("chats/", listar_chats_view, name="listar_chats"),
    path('rentas_arrendador/', rentas_arrendador_view, name='rentas_arrendador'),
    path('rentas_arrendatario/', rentas_arrendatario_view, name='rentas_arrendatario'),
    path('preguntas-sin-responder/', preguntas_sin_responder_view, name='preguntas_sin_responder'),
    path("finalizar-renta/<int:renta_id>/", finalizar_renta_view, name="finalizar_renta"),

]