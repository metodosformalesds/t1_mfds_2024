# routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/verify_identity/<str:user_id>/", consumers.IdentityConsumer.as_asgi()),
]
