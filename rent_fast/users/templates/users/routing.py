# routing.py
from django.urls import path
from . import consumers
# Define las rutas WebSocket para la aplicación.
# Este archivo mapea las URLs de WebSocket a los consumidores correspondientes.


websocket_urlpatterns = [
# Ruta WebSocket para la verificación de identidad del usuario.
# La URL contiene un parámetro `user_id` que se pasa al consumidor para identificar al usuario.
    path("ws/verify_identity/<str:user_id>/", consumers.IdentityConsumer.as_asgi()),
]
