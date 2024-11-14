# rentas/views.py
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from paypalrestsdk import Payment
from .models import Renta, Chat, Mensaje
from django.contrib.auth.decorators import login_required
from tools.models import Carrito
from .paypal import paypalrestsdk
from django.http import HttpResponse
from .forms import MensajeForm
from users.models import Arrendatario, Arrendador
from .forms import RespuestaForm, PreguntaForm
from .models import Pregunta



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
        
        # Crear rentas y vaciar el carrito
        arrendatario = getattr(request.user, 'arrendatario', None)
        carrito_items = Carrito.objects.filter(arrendatario=arrendatario)

        for item in carrito_items:
            # Crear una nueva renta
            renta = Renta.objects.create(
                herramienta=item.herramienta,
                arrendatario=arrendatario,
                fecha_inicio=item.fecha_inicio,
                fecha_fin=item.fecha_fin,
                costo_total=item.costo_total,
                estado="Activa",
            )
            
            # Opcional: Crear un chat relacionado con la renta
            Chat.objects.create(
                arrendador=item.herramienta.arrendador,
                arrendatario=arrendatario,
                herramienta=item.herramienta,
                renta=renta
            )
        
        # Eliminar todos los items del carrito después de crear las rentas
        carrito_items.delete()
        
        return redirect("arrendatario_home")
    else:
        messages.error(request, "Error al confirmar el pago")
        return redirect("carrito")
        
def pago_cancelado_view(request):
    messages.info(request, "El pago fue cancelado.")
    return redirect("carrito")

@login_required
def ver_chat_view(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    # Verificar si el usuario es parte del chat
    if not (request.user == chat.arrendador.usuario or request.user == chat.arrendatario.usuario):
        return redirect('home')  # Redirige si el usuario no es parte del chat

    if request.method == 'POST':
        form = MensajeForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.chat = chat
            mensaje.remitente = request.user
            mensaje.save()
            return redirect('ver_chat', chat_id=chat.id)
    else:
        form = MensajeForm()

    # Agrega la herramienta al contexto
    herramienta = chat.herramienta  # Obtener la herramienta asociada al chat

    return render(request, 'ver_chat.html', {
        'chat': chat,
        'form': form,
        'mensajes': chat.mensajes.all().order_by('enviado'),
        'herramienta': herramienta  # Incluye la herramienta en el contexto
    })
    
@login_required
def listar_chats_view(request):
    # Obtener los chats donde el usuario sea arrendador o arrendatario
    chats = Chat.objects.filter(
        arrendador__usuario=request.user
    ) | Chat.objects.filter(
        arrendatario__usuario=request.user
    )

    # Determinar la URL de redirección según el tipo de usuario
    if hasattr(request.user, 'arrendador'):
        url_redireccion = reverse('arrendador_home')
    else:
        url_redireccion = reverse('arrendatario_home')

    return render(request, 'rentas/listar_chats.html', {
        'chats': chats,
        'url_redireccion': url_redireccion
    })


@login_required
def rentas_arrendador_view(request):
    # Verificamos que el usuario sea un arrendador
    arrendador = Arrendador.objects.filter(usuario=request.user).first()
    if not arrendador:
        return render(request, "tools/no_role.html", {'error': "Solo los arrendadores pueden ver esta página."})

    # Obtenemos las rentas de las herramientas del arrendador, filtradas por estado si se solicita
    estado_filtro = request.GET.get("estado", "Activa")  # Por defecto, muestra las rentas activas
    rentas = Renta.objects.filter(herramienta__arrendador=arrendador, estado=estado_filtro)

    return render(request, "rentas/rentas_arrendador.html", {
        "rentas": rentas,
        "estado_filtro": estado_filtro,
        "estados": Renta._meta.get_field("estado").choices,  # Opciones de estado para el filtro
    })


@login_required
def rentas_arrendatario_view(request):
    # Verificamos que el usuario sea un arrendatario
    arrendatario = Arrendatario.objects.filter(usuario=request.user).first()
    if not arrendatario:
        return render(request, "tools/no_role.html", {'error': "Solo los arrendatarios pueden ver esta página."})

    # Obtenemos las rentas del arrendatario, con opción de filtro por estado
    estado_filtro = request.GET.get("estado", "Activa")  # Muestra rentas activas por defecto
    rentas = Renta.objects.filter(arrendatario=arrendatario, estado=estado_filtro)

    return render(request, "rentas/rentas_arrendatario.html", {
        "rentas": rentas,
        "estado_filtro": estado_filtro,
        "estados": Renta._meta.get_field("estado").choices,
    })

from .models import Respuesta
@login_required
def preguntas_sin_responder_view(request):
    arrendador = Arrendador.objects.get(usuario=request.user)
    preguntas = Pregunta.objects.filter(herramienta__arrendador=arrendador, respuesta=None)

    if request.method == 'POST':
        form = RespuestaForm(request.POST)
        if form.is_valid():
            pregunta_id = request.POST.get('pregunta_id')
            pregunta = get_object_or_404(Pregunta, id=pregunta_id)
            respuesta_texto = form.cleaned_data['respuesta_texto']
            respuesta = Respuesta.objects.create(
                pregunta=pregunta,
                arrendador=arrendador,
                respuesta_texto=respuesta_texto
            )
            messages.success(request, "Respuesta enviada correctamente.")
            return redirect('preguntas_sin_responder')

    else:
        form = RespuestaForm()

    return render(request, 'rentas/preguntas_sin_responder.html', {'preguntas': preguntas, 'form': form})

@login_required
def finalizar_renta_view(request, renta_id):
    renta = get_object_or_404(Renta, id=renta_id, arrendatario__usuario=request.user)

    if renta.estado != "Activa":
        messages.error(request, "Esta renta ya ha sido finalizada o no se puede modificar.")
        return redirect("rentas_arrendatario")  # Cambia al nombre de la URL de tus rentas del arrendatario si es diferente

    renta.estado = "Finalizada"
    renta.save()

    messages.success(request, "La renta ha sido finalizada exitosamente.")
    return redirect("ver_chat", chat_id=renta.chat_set.first().id)  # Redirige al chat relacionado
