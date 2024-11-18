# rentas/urls.py
from django.urls import path
from .views import soporte_view,iniciar_pago_view,preguntas_sin_responder_view, pago_confirmacion_view, pago_exitoso_view, pago_cancelado_view, ver_chat_view, listar_chats_view, rentas_arrendador_view, rentas_arrendatario_view, finalizar_renta_view, ocultar_chat, restaurar_chat_view, mostrar_chat
from django.conf import settings
from django.conf.urls.static import static

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
    path('ocultar_chat/<int:chat_id>/', ocultar_chat, name='ocultar_chat'),
    path('restaurar_chat/<int:chat_id>/', restaurar_chat_view, name='restaurar_chat'),
    path('chats/mostrar/<int:chat_id>/', mostrar_chat, name='mostrar_chat'),
    path("pago/confirmacion/", pago_confirmacion_view, name="pago_confirmacion"),
    path("soporte/", soporte_view, name="soporte"),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
