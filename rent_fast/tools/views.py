from django.views import generic
from .forms import ToolForm, RentaForm, CarritoForm
from users.models import Arrendador, Arrendatario
from .models import Tool, Carrito, Categoria
from rentas.models import Renta
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rentas.models import Chat
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from datetime import datetime
from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, fields
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from geopy.geocoders import Nominatim
from django.conf import settings
import requests
from rentas.forms import PreguntaForm
from rentas.models import Pregunta
from users.models import Notificacion


def cotizar_envio_view(request, tool_id):
    # Verificar si tenemos un access_token en la sesi n
    access_token = request.session.get("uber_access_token")
    
    if not access_token:
        # Redirigir al flujo de autenticaci n si el token no est  disponible
        return redirect("uber_login")

    # Obtener la herramienta y las direcciones de arrendador y arrendatario
    herramienta = get_object_or_404(Tool, id=tool_id)
    arrendador = herramienta.arrendador
    arrendatario = request.user.arrendatario

    # Crear direcciones basadas en el modelo Direccion
    origen_direccion = f"{arrendador.direccion.calle}, {arrendador.direccion.ciudad}, {arrendador.direccion.estado}, {arrendador.direccion.codigo_postal}"
    destino_direccion = f"{arrendatario.direccion.calle}, {arrendatario.direccion.ciudad}, {arrendatario.direccion.estado}, {arrendatario.direccion.codigo_postal}"

    # Utilizar geopy para obtener las coordenadas de las direcciones
    geolocator = Nominatim(user_agent="tool_rental")
    origen_location = geolocator.geocode(origen_direccion)
    destino_location = geolocator.geocode(destino_direccion)

    # Verificar que se obtuvieron coordenadas
    if not origen_location or not destino_location:
        return render(request, "tools/error.html", {"error": "No se pudo obtener la ubicaci n de una o ambas direcciones."})

    # Asignar coordenadas
    origen_coords = {"lat": origen_location.latitude, "lng": origen_location.longitude}
    destino_coords = {"lat": destino_location.latitude, "lng": destino_location.longitude}

    # Configurar encabezados y par metros de solicitud
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "start_latitude": origen_coords['lat'],
        "start_longitude": origen_coords['lng'],
        "end_latitude": destino_coords['lat'],
        "end_longitude": destino_coords['lng']
    }

    # Solicitar la cotizaci n
    url = "https://api.uber.com/v1.2/estimates/price"
    response = requests.get(url, headers=headers, params=data)

    if response.status_code == 200:
        precios = response.json().get('prices', [])
        return render(request, "tools/cotizacion_envio.html", {
            "precios": precios,
            "origen": origen_direccion,
            "destino": destino_direccion
        })
    else:
        return JsonResponse({"error": "Error en la solicitud de cotizaci n a Uber."})


def uber_login_view(request):
    auth_url = "https://auth.uber.com/oauth/v2/authorize"
    client_id = settings.UBER_CLIENT_ID
    redirect_uri = "https://8000-idx-t1mfds2024git-1729092128078.cluster-3ch54x2epbcnetrm6ivbqqebjk.cloudworkstations.dev/herramientas/uber/callback/"
    scope = "request estimate"  # Reemplaza con los permisos necesarios para tu aplicaci n (debe ser v lido)
    response_type = "code"  # Aseg rate de que response_type sea "code"

    # Construir la URL de autenticaci n
    authorization_url = (
        f"{auth_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type={response_type}"
    )

    return redirect(authorization_url)


def uber_callback_view(request):
    code = request.GET.get("code")

    if not code:
        return JsonResponse({"error": "No se recibi  un c digo de autorizaci n.", "details": request.GET.dict()})

    token_url = "https://auth.uber.com/oauth/v2/token"
    data = {
        "client_id": settings.UBER_CLIENT_ID,
        "client_secret": settings.UBER_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": "https://8000-idx-t1mfds2024git-1729092128078.cluster-3ch54x2epbcnetrm6ivbqqebjk.cloudworkstations.dev/herramientas/uber/callback/",
        "code": code,
    }

    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get("access_token")
        request.session['uber_access_token'] = access_token

        return redirect("cotizacion_envio")
    else:
        # Agrega informaci n de depuraci n
        error_details = response.json()  # Extrae el mensaje de error de la respuesta
        return JsonResponse({"error": "No se pudo obtener el token de acceso de Uber.", "details": error_details})


@login_required
def home_view(request):
    """
    Vista principal que redirige a diferentes p ginas de inicio seg n el rol del usuario.
    """
    try:
        if request.user.is_staff:  # Verifica si el usuario es administrador
            return redirect('admin_home')
        elif Arrendador.objects.filter(usuario=request.user).exists():
            return redirect('arrendador_home')
        elif Arrendatario.objects.filter(usuario=request.user).exists():
            return redirect('arrendatario_home')
        else:
            return render(request, "tools/no_role.html")  # P gina para usuarios sin rol espec fico
    except Exception as e:
        return render(request, "tools/error.html", {'error': str(e)})


@login_required
def arrendador_home(request):
    arrendador = Arrendador.objects.get(usuario=request.user)
    
    # Herramientas por estado
    tools_pendientes = Tool.objects.filter(arrendador=arrendador, estado='Pendiente').order_by('-id')
    tools_rechazadas = Tool.objects.filter(arrendador=arrendador, estado='Rechazado').order_by('-id')
    tools_disponibles = Tool.objects.filter(arrendador=arrendador, estado='Disponible').exclude(
        id__in=Renta.objects.filter(estado='Activa').values_list('herramienta_id', flat=True)
    ).order_by('-id')

    # Herramientas en renta
    herramientas_en_renta = Renta.objects.filter(
        herramienta__arrendador=arrendador, estado='Activa'
    ).select_related('herramienta')

    return render(request, "arrendadores/arrendador_home.html", {
        'tools_pendientes': tools_pendientes,
        'tools_aprobadas': tools_disponibles,
        'tools_rechazadas': tools_rechazadas,
        'herramientas_en_renta': herramientas_en_renta,
    })

    

@login_required
def arrendatario_home(request):
    search_query = request.GET.get('search', '')  # Recoge el valor de b squeda (si existe)

    # Obtener herramientas disponibles agrupadas por categor a
    categorias = Categoria.objects.all()
    herramientas_por_categoria = {
        categoria.nombre: Tool.objects.filter(categoria=categoria, estado="Disponible", nombre__icontains=search_query)[:5]
        for categoria in categorias
    }

    # Herramientas sin categor a (para la secci n "Cerca de ti")
    herramientas_sin_categoria = Tool.objects.filter(categoria__isnull=True, estado="Disponible", nombre__icontains=search_query)

    return render(request, 'arrendatarios/arrendatario_home_new.html', {
        'herramientas_sin_categoria': herramientas_sin_categoria,
        'herramientas_por_categoria': herramientas_por_categoria,
        'search_query': search_query,
    })

class ToolFormView(LoginRequiredMixin, generic.FormView):
    template_name = "tools/add_tool.html"
    form_class = ToolForm
    success_url = reverse_lazy("list_tool")

    def form_valid(self, form):
        # Obtenemos el perfil de arrendador del usuario autenticado
        try:
            arrendador = Arrendador.objects.get(usuario=self.request.user)
            form.save(arrendador=arrendador)  # Guardar la herramienta asociada al arrendador
        except Arrendador.DoesNotExist:
            return redirect('no_role')  # Redirigir a una p gina de error si no es arrendador
        return super().form_valid(form)

class ToolListView(generic.ListView):
    model = Tool
    template_name = "tools/list_tool.html"
    context_object_name = "tools"

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class ToolDetailView(DetailView):
    model = Tool
    template_name = "tools/tool_details.html"
    context_object_name = 'tool'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tool = self.get_object()
        user = self.request.user
        arrendatario = getattr(user, 'arrendatario', None)

        # Obtener las reseñas de la herramienta
        context['resenas'] = Resena.objects.filter(herramienta=tool)
        
        # Verificar si el usuario ha alquilado y finalizado la herramienta
        context['ha_alquilado_y_finalizado'] = (
            arrendatario and Renta.objects.filter(
                herramienta=tool,
                arrendatario=arrendatario,
                estado="Finalizada"
            ).exists()
        )
        
        # Solo muestra el formulario de reseña si la renta fue finalizada y aún no hay reseña
        if context['ha_alquilado_y_finalizado'] and not Resena.objects.filter(herramienta=tool, arrendatario=arrendatario).exists():
            context['form'] = ResenaForm()
        else:
            context['form'] = None
        
        # Agregar preguntas y respuestas
        context['preguntas'] = tool.preguntas.all()
        context['pregunta_form'] = PreguntaForm()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        arrendatario = getattr(request.user, 'arrendatario', None)

        # Manejar el formulario de reseñas
        if 'comentario' in request.POST:
            ha_alquilado_y_finalizado = (
                arrendatario and Renta.objects.filter(
                    herramienta=self.object,
                    arrendatario=arrendatario,
                    estado="Finalizada"
                ).exists()
            )
            if not ha_alquilado_y_finalizado:
                messages.error(request, "Debes finalizar la renta de esta herramienta para dejar una reseña.")
                return redirect('tool_detail', pk=self.object.pk)
            form = ResenaForm(request.POST)
            if form.is_valid():
                resena = form.save(commit=False)
                resena.arrendatario = arrendatario
                resena.herramienta = self.object
                resena.save()
                messages.success(request, "Tu reseña ha sido enviada con éxito.")
                return redirect('tool_detail', pk=self.object.pk)
            else:
                messages.error(request, "Hubo un error con tu reseña. Inténtalo de nuevo.")
        
        # Manejar el formulario de preguntas
        elif 'pregunta_texto' in request.POST and arrendatario:
            pregunta_form = PreguntaForm(request.POST)
            if pregunta_form.is_valid():
                pregunta = pregunta_form.save(commit=False)
                pregunta.herramienta = self.object
                pregunta.arrendatario = arrendatario
                pregunta.save()
                messages.success(request, "Tu pregunta ha sido enviada.")
                return redirect('tool_detail', pk=self.object.pk)
            else:
                messages.error(request, "Hubo un error con tu pregunta. Inténtalo de nuevo.")

        return self.get(request, *args, **kwargs)

@login_required
def add_tool_view(request):
    arrendador = Arrendador.objects.get(usuario=request.user)  # Obtenemos el arrendador
    if request.method == 'POST':
        form = ToolForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(arrendador=arrendador)  # Guardar la herramienta con estado "Pendiente"
            return redirect('arrendador_home')  # Redirige a la p gina del arrendador despu s de crear la herramienta
    else:
        form = ToolForm()
    return render(request, 'arrendadores/add_tool.html', {'form': form})

    
@login_required
def carrito_view(request):
    arrendatario = request.user.arrendatario
    carrito_items = Carrito.objects.filter(arrendatario=arrendatario)
    
    # Calcular el costo total del carrito
    monto_total = sum(item.costo_total for item in carrito_items)
    
    return render(request, 'tools/carrito.html', {
        'carrito_items': carrito_items,
        'monto_total': monto_total,
    })

from datetime import timedelta

@login_required
def seleccionar_fechas_view(request, tool_id):
    herramienta = get_object_or_404(Tool, id=tool_id)
    
    # Obtener todas las rentas activas de la herramienta y calcular los días ocupados
    rentas = Renta.objects.filter(herramienta=herramienta, estado="Activa")
    fechas_ocupadas = []

    for renta in rentas:
        current_date = renta.fecha_inicio
        while current_date <= renta.fecha_fin:
            fechas_ocupadas.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

    if request.method == 'POST':
        form = RentaForm(request.POST)
        if form.is_valid():
            request.session['fecha_inicio'] = str(form.cleaned_data['fecha_inicio'])
            request.session['fecha_fin'] = str(form.cleaned_data['fecha_fin'])
            return redirect('agregar_al_carrito', tool_id=tool_id)
    else:
        form = RentaForm()
    
    return render(request, 'tools/seleccionar_fechas.html', {
        'form': form,
        'tool': herramienta,
        'fechas_ocupadas': fechas_ocupadas,  # Pasamos las fechas ocupadas al contexto
    })

@login_required
def agregar_al_carrito_view(request, tool_id):
    herramienta = get_object_or_404(Tool, id=tool_id)
    arrendatario = getattr(request.user, 'arrendatario', None)

    # Verificar si el usuario tiene perfil de arrendatario
    if not arrendatario:
        return render(request, 'tools/no_role.html', {'error': "Necesitas un perfil de arrendatario para alquilar herramientas."})

    # Obtener las fechas desde la sesi n
    fecha_inicio = request.session.get('fecha_inicio')
    fecha_fin = request.session.get('fecha_fin')
    
    if fecha_inicio and fecha_fin:
        # Convertir las fechas a objetos de fecha y calcular el costo total
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        dias_renta = (fecha_fin - fecha_inicio).days + 1
        costo_total = dias_renta * herramienta.costo_dia

        # Guardar en el carrito
        carrito_item = Carrito.objects.create(
            arrendatario=arrendatario,
            herramienta=herramienta,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            costo_total=costo_total
        )
        
        # Limpiar las fechas de la sesi n
        del request.session['fecha_inicio']
        del request.session['fecha_fin']

        return redirect('carrito')  # Redirige al carrito despu s de agregar el producto
    
    # Si las fechas no est n en la sesi n, redirigir a seleccionar fechas
    return redirect('seleccionar_fechas', tool_id=tool_id)

@login_required
def rent_tool_view(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id)
    if request.method == 'POST':
        form = RentaForm(request.POST)
        if form.is_valid():
            renta = form.save(commit=False)
            renta.herramienta = tool
            renta.arrendatario = request.user.arrendatario  # Suponiendo que tienes un perfil de arrendatario
            renta.costo_total = renta.calcular_costo_total()
            renta.save()
            # Redirigir al carrito o a la vista del carrito
            return redirect('carrito')
    else:
        form = RentaForm()
    return render(request, 'tools/rent_tool.html', {'form': form, 'tool': tool})

@login_required
def resumen_view(request):
    arrendatario = getattr(request.user, 'arrendatario', None)
    if not arrendatario:
        return render(request, 'tools/no_role.html', {'error': "Necesitas un perfil de arrendatario para ver el resumen."})
    
    # Obtener los elementos del carrito para este usuario
    carrito_items = Carrito.objects.filter(arrendatario=arrendatario)
    
    # Calcular el monto total
    monto_total = sum(item.costo_total for item in carrito_items)
    
    return render(request, 'tools/resumen.html', {
        'carrito_items': carrito_items,
        'monto_total': monto_total,
    })


@login_required
def confirmar_renta_view(request):
    arrendatario = getattr(request.user, 'arrendatario', None)
    if not arrendatario:
        return render(request, 'tools/no_role.html', {'error': "Necesitas un perfil de arrendatario para confirmar la renta."})

    carrito_items = Carrito.objects.filter(arrendatario=arrendatario)

    if not carrito_items:
        messages.error(request, "No tienes herramientas en el carrito.")
        return redirect('carrito')

    for item in carrito_items:
        renta = Renta.objects.create(
            herramienta=item.herramienta,
            arrendatario=arrendatario,
            fecha_inicio=item.fecha_inicio,
            fecha_fin=item.fecha_fin,
            costo_total=item.costo_total,
            estado="Activa"
        )

        # Crear notificaci n para el arrendador
        mensaje = f"Una nueva renta ha sido generada para tu herramienta '{item.herramienta.nombre}'"
        Notificacion.objects.create(usuario=item.herramienta.arrendador.usuario, mensaje=mensaje)

    carrito_items.delete()
    messages.success(request, " La renta se ha confirmado correctamente!")
    return redirect('arrendatario_home')

@staff_member_required
def admin_home(request):
    """
    Vista del administrador para ver herramientas pendientes y decidir su aprobaci n o rechazo.
    """
    pending_tools = Tool.objects.filter(estado='Pendiente')  # Obtener solo las herramientas en estado "Pendiente"
    return render(request, 'admin/admin_home.html', {'pending_tools': pending_tools})


@staff_member_required
@require_POST
def approve_tool(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id)
    tool.estado = 'Disponible'
    tool.save()
    
    # Crear notificaci n para el arrendador
    mensaje = f"Tu herramienta '{tool.nombre}' ha sido aprobada y ahora est  disponible."
    Notificacion.objects.create(usuario=tool.arrendador.usuario, mensaje=mensaje)

    return redirect('admin_home')


from .forms import RechazarToolForm
@staff_member_required
@require_POST
def reject_tool(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id)
    if request.method == 'POST':
        form = RechazarToolForm(request.POST, instance=tool)
        if form.is_valid():
            tool.estado = 'Rechazado'
            form.save()

            # Crear notificación para el arrendador con el motivo del rechazo
            mensaje = f"Tu herramienta '{tool.nombre}' ha sido rechazada. Motivo: {tool.mensaje_rechazo}"
            Notificacion.objects.create(usuario=tool.arrendador.usuario, mensaje=mensaje)

            return redirect('admin_home')
    else:
        form = RechazarToolForm(instance=tool)

    return render(request, 'admin/reject_tool.html', {'form': form, 'tool': tool})


@staff_member_required
def admin_pending_tools(request):
    """
    Vista para que el administrador vea todas las herramientas pendientes.
    """
    pending_tools = Tool.objects.filter(estado='Pendiente')
    return render(request, 'admin/admin_pending_tools.html', {'pending_tools': pending_tools})
    
def pagar_sin_paypal_view(request):
    arrendatario = getattr(request.user, 'arrendatario', None)
    if not arrendatario:
        messages.error(request, "No se encontr  un perfil de arrendatario.")
        return redirect("carrito")

    carrito_items = Carrito.objects.filter(arrendatario=arrendatario)
    if not carrito_items:
        messages.error(request, "No tienes herramientas en el carrito.")
        return redirect("carrito")

    ultimo_chat_id = None  # Variable para guardar el ID del  ltimo chat creado

    # Crear una instancia de Renta y Chat para cada elemento en el carrito
    for item in carrito_items:
        renta = Renta.objects.create(
            herramienta=item.herramienta,
            arrendatario=arrendatario,
            fecha_inicio=item.fecha_inicio,
            fecha_fin=item.fecha_fin,
            costo_total=item.costo_total,
            estado="Activa"
        )
        
        # Crear el chat entre el arrendatario y el arrendador de la herramienta
        chat = Chat.objects.create(
            arrendador=item.herramienta.arrendador,
            arrendatario=arrendatario,
            herramienta=item.herramienta,
            renta=renta
        )

        # Guardar el ID del  ltimo chat creado
        ultimo_chat_id = chat.id

    # Vaciar el carrito
    carrito_items.delete()

    # Redirigir al chat reci n creado
    if ultimo_chat_id:
        messages.success(request, "Renta completada exitosamente y chat creado.")
        return redirect(reverse("ver_chat", args=[ultimo_chat_id]))

    # Si no se cre  ning n chat, redirigir al home del arrendatario
    messages.error(request, "No se pudo crear el chat. Redirigiendo al inicio.")
    return redirect("arrendatario_home")
    
    
    # views.py
from django.conf import settings
import requests
from django.http import JsonResponse

def uber_auth(request):
    auth_url = (
        "https://login.uber.com/oauth/v2/authorize"
        f"?client_id={settings.UBER_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={settings.UBER_REDIRECT_URI}"
        "&scope=delivery"  # Ajusta el scope si es necesario
    )
    return redirect(auth_url)

def uber_callback(request):
    code = request.GET.get('code')
    token_url = 'https://login.uber.com/oauth/v2/token'
    data = {
        'client_id': settings.UBER_CLIENT_ID,
        'client_secret': settings.UBER_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.UBER_REDIRECT_URI,
        'code': code,
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get('access_token')

    # Guarda el access_token en la sesi n para usarlo despu s
    request.session['uber_access_token'] = access_token

    # Devuelve el token para pruebas
    return JsonResponse({'access_token': access_token})

def obtener_cotizacion(request):
    access_token = request.session.get('uber_access_token')
    if not access_token:
        return JsonResponse({'error': 'No se ha autenticado con Uber.'}, status=401)

    url = f"https://api.uber.com/v1/customers/{settings.UBER_CUSTOMER_ID}/delivery_quotes"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    data = {
        'pickup_address': '123 Calle Falsa, Ciudad',  # Cambia estos datos seg n sea necesario
        'dropoff_address': '456 Avenida Verdadera, Ciudad',
    }
    response = requests.post(url, headers=headers, json=data)

    return JsonResponse(response.json())

# Resenas
from rentas.models import Resena
from rentas.forms import ResenaForm
from django.db.models import Avg
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from tools.models import Tool
from rentas.models import Renta

@login_required
def detalles_herramienta(request, herramienta_id):
    herramienta = get_object_or_404(Tool, id=herramienta_id)
    resenas = Resena.objects.filter(herramienta=herramienta)

    # Calcular el promedio de las calificaciones
    promedio_calificacion = resenas.aggregate(Avg('calificacion'))['calificacion__avg']

    # Verificar si el usuario ha alquilado y finalizado la herramienta
    ha_alquilado_y_finalizado = Renta.objects.filter(
        herramienta=herramienta,
        arrendatario=request.user.arrendatario,
        estado="Finalizada"
    ).exists()

    # Verificar si ya existe una rese a para este arrendatario y herramienta
    resena_existente = Resena.objects.filter(
        herramienta=herramienta,
        arrendatario=request.user.arrendatario
    ).exists()

    if request.method == 'POST' and ha_alquilado_y_finalizado and not resena_existente:
        form = ResenaForm(request.POST)
        if form.is_valid():
            resena = form.save(commit=False)
            resena.arrendatario = request.user.arrendatario
            resena.herramienta = herramienta
            resena.save()
            messages.success(request, "Tu rese a ha sido enviada con  xito.")
            return redirect('tool_detail', herramienta_id=herramienta.id)
        else:
            messages.error(request, "Hubo un error con tu rese a. Int ntalo de nuevo.")
    else:
        form = ResenaForm()

    context = {
        'herramienta': herramienta,
        'resenas': resenas,
        'promedio_calificacion': promedio_calificacion,
        'ha_alquilado_y_finalizado': ha_alquilado_y_finalizado and not resena_existente,
        'form': form,
    }
    return render(request, 'tools/tool_details.html', context)

# tools/views.py
from django.shortcuts import get_object_or_404, redirect, render
from .models import Tool
from .forms import ToolForm

from django.http import HttpResponseForbidden

@login_required
def editar_herramienta_view(request, tool_id):
    herramienta = get_object_or_404(Tool, id=tool_id, arrendador=request.user.arrendador)
    
    # Verificar si la herramienta está en renta activa
    if Renta.objects.filter(herramienta=herramienta, estado="Activa").exists():
        return HttpResponseForbidden("No puedes editar una herramienta que está en renta activa.")

    if request.method == 'POST':
        form = ToolForm(request.POST, request.FILES, instance=herramienta)
        if form.is_valid():
            form.save(arrendador=request.user.arrendador)
            return redirect('arrendador_home')
    else:
        form = ToolForm(instance=herramienta)

    return render(request, 'tools/editar_herramienta.html', {'form': form})


@login_required
def eliminar_herramienta_view(request, tool_id):
    herramienta = get_object_or_404(Tool, id=tool_id, arrendador=request.user.arrendador)

    # Verificar si la herramienta está en renta activa
    if Renta.objects.filter(herramienta=herramienta, estado="Activa").exists():
        return HttpResponseForbidden("No puedes eliminar una herramienta que está en renta activa.")

    if request.method == 'POST':
        herramienta.delete()
        return redirect('arrendador_home')

    return render(request, 'tools/eliminar_herramienta.html', {'herramienta': herramienta})

from django.shortcuts import render, get_object_or_404
from .models import Tool

@staff_member_required
def revisar_tool_view(request, tool_id):
    herramienta = get_object_or_404(Tool, id=tool_id)  # Obtener la herramienta específica
    return render(request, 'admin/revision_tool.html', {'herramienta': herramienta})


@login_required
def eliminar_del_carrito_view(request, item_id):
    item = get_object_or_404(Carrito, id=item_id, arrendatario=request.user.arrendatario)
    
    item.delete()
    messages.success(request, "El artículo ha sido eliminado del carrito.")
    return redirect("carrito")  # Redirige a la página del carrito después de eliminar