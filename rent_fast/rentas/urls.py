# rentas/urls.py
from django.urls import path
from .views import iniciar_pago_view, pago_exitoso_view, pago_cancelado_view

urlpatterns = [
    path("pago/", iniciar_pago_view, name="iniciar_pago"),
    path("pago/exitoso/", pago_exitoso_view, name="pago_exitoso"),
    path("pago/cancelado/", pago_cancelado_view, name="pago_cancelado"),
]
