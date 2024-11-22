# rentas/paypal.py
import paypalrestsdk
from django.conf import settings

# Configurar PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # sandbox o live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})
"""
Daniel Esqueda
Este archivo contiene la configuración inicial del SDK de PayPal para el sistema de pagos.

El SDK de PayPal se configura con los detalles proporcionados en las configuraciones del proyecto, 
como el modo (sandbox o live), el client_id y el client_secret.

Dependencias:
- paypalrestsdk: Biblioteca de PayPal para interactuar con su API.
- settings: Archivo de configuración de Django que contiene las credenciales de PayPal.

Proceso de configuración:
1. Configura el entorno de PayPal (modo de pruebas o producción).
2. Configura las credenciales de PayPal, como el ID de cliente y el secreto del cliente.
"""