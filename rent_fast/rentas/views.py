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
from .models import Pregunta, Renta
from users.models import Notificacion
from django.contrib.auth.models import User
from django.db.models import Q
 
 
 
 
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
           
            # Crear el chat relacionado con la renta
            chat = Chat.objects.create(
                arrendador=item.herramienta.arrendador,
                arrendatario=arrendatario,
                herramienta=item.herramienta,
                renta=renta
            )
 
            # Notificar al arrendador sobre el nuevo chat
            mensaje = f"Nuevo chat creado para la herramienta '{item.herramienta.nombre}'."
            Notificacion.objects.create(
                usuario=item.herramienta.arrendador.usuario,
                mensaje=mensaje,
                herramienta=item.herramienta
            )
       
        # Eliminar todos los items del carrito después de crear las rentas
        carrito_items.delete()
 
        # Redirigir a la pantalla de pago exitoso
        return redirect("pago_confirmacion")
    else:
        messages.error(request, "Error al confirmar el pago")
        return redirect("carrito")
 
 
def pago_confirmacion_view(request):
    """
    Pantalla de confirmación de pago.
    """
    return render(request, 'rentas/pago_confirmacion.html')
       
def pago_cancelado_view(request):
    messages.info(request, "El pago fue cancelado.")
    return redirect("carrito")
 
from django.shortcuts import redirect
 
@login_required
def ver_chat_view(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
 
    # Verificar si el usuario está autorizado para ver el chat
    if not (
        (chat.arrendador and request.user == chat.arrendador.usuario) or
        (chat.arrendatario and request.user == chat.arrendatario.usuario) or
        request.user.is_staff
    ):
        return redirect('home')
 
    # Identificar si es un chat de soporte (sin herramienta asociada)
    es_soporte = chat.herramienta is None
 
    # Preparar información de contacto si es un chat de soporte
    contacto_info = None
    if es_soporte:
        if chat.arrendador:
            contacto_info = {
                'nombre': chat.arrendador.usuario.get_full_name(),
                'email': chat.arrendador.usuario.email,
                'foto': getattr(chat.arrendador, 'foto', None),  # Reemplaza 'foto' si tienes un campo explícito en `Arrendador`
            }
        elif chat.arrendatario:
            contacto_info = {
                'nombre': chat.arrendatario.usuario.get_full_name(),
                'email': chat.arrendatario.usuario.email,
                'foto': getattr(chat.arrendatario, 'foto', None),  # Reemplaza 'foto' si tienes un campo explícito en `Arrendatario`
            }
 
    if request.method == 'POST':
        contenido = request.POST.get('contenido', '').strip()
        archivo = request.FILES.get('archivo', None)
 
        if contenido or archivo:  # Crear el mensaje solo si hay contenido o archivo
            Mensaje.objects.create(
                chat=chat,
                remitente=request.user,
                contenido=contenido if contenido else None,
                archivo=archivo if archivo else None
            )
            return redirect('ver_chat', chat_id=chat.id)
 
    return render(request, 'ver_chat.html', {
        'chat': chat,
        'mensajes': chat.mensajes.all().order_by('enviado'),
        'herramienta': chat.herramienta,  # Solo será relevante si no es un chat de soporte
        'es_soporte': es_soporte,
        'contacto_info': contacto_info,  # Información del contacto si es un chat de soporte
    })
 
@login_required
def listar_chats_view(request):
    user = request.user
    chats_admin = []
 
    # Verificar si el usuario es un administrador
    if user.is_staff:
        chats_no_ocultos = Chat.objects.filter(es_soporte=True).order_by('-creado')  # Chats de soporte
        chats_ocultos = []  # Admins no ocultan chats
        url_redireccion = reverse('admin:index')  # Redirigir al panel admin
    elif hasattr(user, 'arrendador'):
        chats_no_ocultos = Chat.objects.filter(arrendador__usuario=user, oculto_arrendador=False).order_by('-creado')
        chats_ocultos = Chat.objects.filter(arrendador__usuario=user, oculto_arrendador=True).order_by('-creado')
        url_redireccion = reverse('arrendador_home')
    elif hasattr(user, 'arrendatario'):
        chats_no_ocultos = Chat.objects.filter(arrendatario__usuario=user, oculto_arrendatario=False).order_by('-creado')
        chats_ocultos = Chat.objects.filter(arrendatario__usuario=user, oculto_arrendatario=True).order_by('-creado')
        url_redireccion = reverse('arrendatario_home')
    else:
        chats_no_ocultos = chats_ocultos = []
        url_redireccion = reverse('home')
 
    return render(request, 'rentas/listar_chats.html', {
        'chats_no_ocultos': chats_no_ocultos,
        'chats_ocultos': chats_ocultos,
        'url_redireccion': url_redireccion,
    })
 
 
 
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
 
@login_required
def ocultar_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    user = request.user
 
    if hasattr(user, 'arrendador') and chat.arrendador.usuario == user:
        chat.oculto_arrendador = True
    elif hasattr(user, 'arrendatario') and chat.arrendatario.usuario == user:
        chat.oculto_arrendatario = True
 
    chat.save()
    return redirect('listar_chats')
 
@login_required
def mostrar_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    user = request.user
 
    if hasattr(user, 'arrendador') and chat.arrendador.usuario == user:
        chat.oculto_arrendador = False
    elif hasattr(user, 'arrendatario') and chat.arrendatario.usuario == user:
        chat.oculto_arrendatario = False
 
    chat.save()
    return redirect('listar_chats')
 
@login_required
def restaurar_chat_view(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
 
    # Verificar que el usuario sea parte del chat
    if not (request.user == chat.arrendador.usuario or request.user == chat.arrendatario.usuario):
        return redirect('listar_chats')
 
    # Restaurar el chat oculto
    if chat.oculto:
        chat.oculto = False
        chat.save()
        messages.success(request, "El chat ha sido restaurado.")
    else:
        messages.error(request, "Este chat no está oculto.")
 
    return redirect('listar_chats')
 
 
 
 
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
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
 
@login_required
def preguntas_sin_responder_view(request):
    arrendador = Arrendador.objects.get(usuario=request.user)
 
    # Ordenar preguntas más nuevas primero
    preguntas = Pregunta.objects.filter(
        herramienta__arrendador=arrendador, respuesta=None
    ).order_by('-fecha_creacion')
 
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
 
from users.models import Notificacion
 
@login_required
def finalizar_renta_view(request, renta_id):
    renta = get_object_or_404(Renta, id=renta_id, arrendatario__usuario=request.user)
 
    if renta.estado != "Activa":
        messages.error(request, "Esta renta ya ha sido finalizada o no se puede modificar.")
        return redirect("rentas_arrendatario")  # Cambia al nombre de la URL de tus rentas del arrendatario si es diferente
 
    renta.estado = "Finalizada"
    renta.save()
 
    # Crear notificación para el arrendatario indicando que puede dejar una reseña
    mensaje = f"Has finalizado la renta de '{renta.herramienta.nombre}'. Ahora puedes dejar una reseña sobre esta herramienta."
    Notificacion.objects.create(
        usuario=request.user,
        mensaje=mensaje,
        herramienta=renta.herramienta,
    )
 
    messages.success(request, "La renta ha sido finalizada exitosamente.")
    return redirect("ver_chat", chat_id=renta.chat_set.first().id)  # Redirige al chat relacionado
 
@login_required
def soporte_view(request):
    if request.method == 'POST':
        # Buscar o crear un chat de soporte para el usuario actual
        if hasattr(request.user, 'arrendatario'):
            arrendatario = request.user.arrendatario
            chat, created = Chat.objects.get_or_create(
                arrendatario=arrendatario,
                herramienta=None,
                es_soporte=True
            )
        elif hasattr(request.user, 'arrendador'):
            arrendador = request.user.arrendador
            chat, created = Chat.objects.get_or_create(
                arrendador=arrendador,
                herramienta=None,
                es_soporte=True
            )
        else:
            return render(request, 'rentas/soporte.html', {'error': 'No tienes un perfil asociado.'})
 
        return redirect('ver_chat', chat_id=chat.id)
 
    return render(request, 'rentas/soporte.html', {
        'preguntas_frecuentes': [
            "¿Cómo alquilo una herramienta?",
            "¿Cómo publico una herramienta?",
            "¿Qué métodos de pago aceptan?"
        ]
    })
 
from users.models import Balance
 
@login_required
def finalizar_renta(request, renta_id):
    print("Inicio del proceso para finalizar renta.")  # Log inicial
   
    # Obtener la renta
    renta = get_object_or_404(Renta, id=renta_id)
    print(f"Renta obtenida: ID {renta.id}, Estado: {renta.estado}")  # Verifica los datos de la renta
 
    # Verificar que el usuario tiene permiso para finalizar la renta
    if request.user != renta.arrendatario.usuario:
        print("Permiso denegado: Usuario no es el arrendatario.")  # Log de permiso denegado
        messages.error(request, "No tienes permiso para finalizar esta renta.")
        return redirect("listar_chats")
 
    # Cambiar el estado de la renta a 'Finalizada'
    renta.estado = "Finalizada"
    renta.save()
    print(f"Renta actualizada a estado: {renta.estado}")  # Log del cambio de estado
 
    # Actualizar el balance del arrendador
    balance, created = Balance.objects.get_or_create(arrendador=renta.arrendador)
    print(f"Balance obtenido para arrendador {renta.arrendador.id}. Creado: {created}")  # Verifica si el balance existía o se creó
 
    monto_previo = balance.monto
    balance.monto += renta.total_pago  # Suma el costo de la renta al balance
    balance.save()
    print(f"Balance actualizado. Monto previo: {monto_previo}, Monto agregado: {renta.total_pago}, Nuevo monto: {balance.monto}")  # Log del balance
 
    messages.success(request, "La renta ha sido finalizada correctamente.")
    print("Proceso de finalización de renta completado exitosamente.")  # Log final
    return redirect("arrendador_home")