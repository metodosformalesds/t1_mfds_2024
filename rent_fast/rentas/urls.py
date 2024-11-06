# rentas/urls.py
from django.urls import path
from .views import iniciar_pago_view, pago_exitoso_view, pago_cancelado_view, ver_chat_view, listar_chats_view

urlpatterns = [
    path("pago/", iniciar_pago_view, name="iniciar_pago"),
    path("pago/exitoso/", pago_exitoso_view, name="pago_exitoso"),
    path("pago/cancelado/", pago_cancelado_view, name="pago_cancelado"),
    path('<int:chat_id>/', ver_chat_view, name='ver_chat'),
    path("chats/", listar_chats_view, name="listar_chats"),

]
