"""
Configuración ASGI para el proyecto rent_fast.

Este archivo expone el callable ASGI como una variable a nivel de módulo llamada ``application``. 

ASGI (Asynchronous Server Gateway Interface) es el estándar para manejar conexiones asíncronas, como WebSockets, en aplicaciones Django modernas. La configuración de ASGI permite que Django maneje tanto solicitudes HTTP tradicionales como WebSockets para comunicación en tiempo real.

Para más información sobre cómo configurar y desplegar aplicaciones con ASGI, consulta la documentación oficial de Django:
    https://docs.djangoproject.com/es/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rent_fast.settings')

application = get_asgi_application()


# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import users.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rent_fast.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            users.routing.websocket_urlpatterns
        )
    ),
})

