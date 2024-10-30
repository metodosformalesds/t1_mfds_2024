# rentas/views.py
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from paypalrestsdk import Payment
from .models import Renta
from tools.models import Carrito
from .paypal import paypalrestsdk
from django.http import HttpResponse

def iniciar_pago_view(request):
    # Obtén el usuario y el total del carrito
    arrendatario = getattr(request.user, 'arrendatario', None)
    carrito_items = Carrito.objects.filter(arrendatario=arrendatario)
    monto_total = sum(item.costo_total for item in carrito_items)

    # Crea el pago en PayPal
    pago = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse("pago_exitoso")),
            "cancel_url": request.build_absolute_uri(reverse("pago_cancelado")),
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "Renta de Herramientas",
                    "sku": "001",
                    "price": str(monto_total),
                    "currency": "USD",
                    "quantity": 1,
                }]
            },
            "amount": {
                "total": str(monto_total),
                "currency": "USD"
            },
            "description": "Renta de herramientas a través de PayPal"
        }]
    })

    # Enviar al usuario a PayPal para completar el pago
    if pago.create():
        for link in pago.links:
            if link.method == "REDIRECT":
                return redirect(link.href)  # Redirige al usuario a PayPal
    else:
        messages.error(request, "Error al crear el pago con PayPal")
        return redirect("carrito")

def pago_exitoso_view(request):
    payment_id = request.GET.get("paymentId")
    payer_id = request.GET.get("PayerID")
    
    # Ejecutar el pago en PayPal
    pago = Payment.find(payment_id)
    if pago.execute({"payer_id": payer_id}):
        messages.success(request, "Pago completado con éxito")
        # Aquí puedes crear la instancia de `Renta` y limpiar el carrito
        return redirect("arrendatario_home")
    else:
        messages.error(request, "Error al confirmar el pago")
        return redirect("carrito")

def pago_cancelado_view(request):
    messages.info(request, "El pago fue cancelado.")
    return redirect("carrito")