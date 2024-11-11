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


def cotizar_envio_view(request, tool_id):
    # Verificar si tenemos un access_token en la sesión
    access_token = request.session.get("uber_access_token")
    
    if not access_token:
        # Redirigir al flujo de autenticación si el token no está disponible
        return redirect("uber_login")

    # Obtener la herramienta y las direcciones de arrendador y arrendatario
    herramienta = get_object_or_404(Tool, id=tool_id)
    arrendador = herramienta.arrendador
    arrendatario = request.user.arrendatario

    # Crear direcciones basadas en el modelo `Direccion`
    origen_direccion = f"{arrendador.direccion.calle}, {arrendador.direccion.ciudad}, {arrendador.direccion.estado}, {arrendador.direccion.codigo_postal}"
    destino_direccion = f"{arrendatario.direccion.calle}, {arrendatario.direccion.ciudad}, {arrendatario.direccion.estado}, {arrendatario.direccion.codigo_postal}"

    # Utilizar geopy para obtener las coordenadas de las direcciones
    geolocator = Nominatim(user_agent="tool_rental")
    origen_location = geolocator.geocode(origen_direccion)
    destino_location = geolocator.geocode(destino_direccion)

    # Verificar que se obtuvieron coordenadas
    if not origen_location or not destino_location:
        return render(request, "tools/error.html", {"error": "No se pudo obtener la ubicación de una o ambas direcciones."})

    # Asignar coordenadas
    origen_coords = {"lat": origen_location.latitude, "lng": origen_location.longitude}
    destino_coords = {"lat": destino_location.latitude, "lng": destino_location.longitude}

    # Configurar encabezados y parámetros de solicitud
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

    # Solicitar la cotización
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
        return JsonResponse({"error": "Error en la solicitud de cotización a Uber."})


def uber_login_view(request):
    auth_url = "https://auth.uber.com/oauth/v2/authorize"
    client_id = settings.UBER_CLIENT_ID
    redirect_uri = "https://8000-idx-t1mfds2024git-1729092128078.cluster-3ch54x2epbcnetrm6ivbqqebjk.cloudworkstations.dev/herramientas/uber/callback/"
    scope = "request estimate"  # Reemplaza con los permisos necesarios para tu aplicación (debe ser válido)
    response_type = "code"  # Asegúrate de que `response_type` sea "code"

    # Construir la URL de autenticación
    authorization_url = (
        f"{auth_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type={response_type}"
    )

    return redirect(authorization_url)


def uber_callback_view(request):
    code = request.GET.get("code")

    if not code:
        return JsonResponse({"error": "No se recibió un código de autorización.", "details": request.GET.dict()})

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
        # Agrega información de depuración
        error_details = response.json()  # Extrae el mensaje de error de la respuesta
        return JsonResponse({"error": "No se pudo obtener el token de acceso de Uber.", "details": error_details})


@login_required
def home_view(request):
    """
    Vista principal que redirige a diferentes páginas de inicio según el rol del usuario.
    """
    try:
        if request.user.is_staff:  # Verifica si el usuario es administrador
            return redirect('admin_home')
        elif Arrendador.objects.filter(usuario=request.user).exists():
            return redirect('arrendador_home')
        elif Arrendatario.objects.filter(usuario=request.user).exists():
            return redirect('arrendatario_home')
        else:
            return render(request, "tools/no_role.html")  # Página para usuarios sin rol específico
    except Exception as e:
        return render(request, "tools/error.html", {'error': str(e)})


@login_required
def arrendador_home(request):
    """
    Vista para el home del Arrendador.
    """
    arrendador = Arrendador.objects.get(usuario=request.user)
    tools = Tool.objects.filter(arrendador=arrendador)
    
    # Obtener las rentas asociadas a las herramientas del arrendador
    rentas = Renta.objects.filter(herramienta__in=tools)

    # Calcular los días de renta en Python
    for renta in rentas:
        renta.dias_renta = (renta.fecha_fin - renta.fecha_inicio).days + 1

    return render(request, "arrendadores/arrendador_home.html", {
        'tools': tools,
        'rentas': rentas,
    })

@login_required
def arrendatario_home(request):
    search_query = request.GET.get('search', '')  # Recoge el valor de búsqueda (si existe)

    # Obtener herramientas disponibles agrupadas por categoría
    categorias = Categoria.objects.all()
    herramientas_por_categoria = {
        categoria.nombre: Tool.objects.filter(categoria=categoria, estado="Disponible", nombre__icontains=search_query)[:5]
        for categoria in categorias
    }

    # Herramientas sin categoría (para la sección "Cerca de ti")
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
            return redirect('no_role')  # Redirigir a una página de error si no es arrendador
        return super().form_valid(form)

class ToolListView(generic.ListView):
    model = Tool
    template_name = "tools/list_tool.html"
    context_object_name = "tools"

class ToolDetailView(DetailView):
    model = Tool
    template_name = "tools/tool_details.html"
    context_object_name = 'tool'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PreguntaForm()  # Añadimos el formulario de pregunta al contexto
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = PreguntaForm(request.POST)
        arrendatario = getattr(request.user, 'arrendatario', None)

        if not arrendatario:
            # Redirecciona si el usuario no es un arrendatario
            return redirect('login')

        if form.is_valid():
            pregunta = form.save(commit=False)
            pregunta.herramienta = self.object  # Asocia la pregunta con la herramienta actual
            pregunta.arrendatario = arrendatario
            pregunta.save()
            return redirect('tool_detail', pk=self.object.pk)  # Redirige a la misma página para actualizar el contenido

        return self.get(request, *args, **kwargs)

@login_required
def add_tool_view(request):
    arrendador = Arrendador.objects.get(usuario=request.user)  # Obtenemos el arrendador
    if request.method == 'POST':
        form = ToolForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(arrendador=arrendador)  # Guardar la herramienta con estado "Pendiente"
            return redirect('arrendador_home')  # Redirige a la página del arrendador después de crear la herramienta
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


@login_required
def seleccionar_fechas_view(request, tool_id):
    herramienta = get_object_or_404(Tool, id=tool_id)
    
    if request.method == 'POST':
        form = RentaForm(request.POST)
        if form.is_valid():
            # Guardamos las fechas en la sesión para usarlas en el carrito
            request.session['fecha_inicio'] = str(form.cleaned_data['fecha_inicio'])
            request.session['fecha_fin'] = str(form.cleaned_data['fecha_fin'])
            return redirect('agregar_al_carrito', tool_id=tool_id)
    else:
        form = RentaForm()
    
    return render(request, 'tools/seleccionar_fechas.html', {'form': form, 'tool': herramienta})

@login_required
def agregar_al_carrito_view(request, tool_id):
    herramienta = get_object_or_404(Tool, id=tool_id)
    arrendatario = getattr(request.user, 'arrendatario', None)

    # Verificar si el usuario tiene perfil de arrendatario
    if not arrendatario:
        return render(request, 'tools/no_role.html', {'error': "Necesitas un perfil de arrendatario para alquilar herramientas."})

    # Obtener las fechas desde la sesión
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
        
        # Limpiar las fechas de la sesión
        del request.session['fecha_inicio']
        del request.session['fecha_fin']

        return redirect('carrito')  # Redirige al carrito después de agregar el producto
    
    # Si las fechas no están en la sesión, redirigir a seleccionar fechas
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

    # Obtener los elementos del carrito
    carrito_items = Carrito.objects.filter(arrendatario=arrendatario)

    if not carrito_items:
        messages.error(request, "No tienes herramientas en el carrito.")
        return redirect('carrito')

    # Crear una renta para cada herramienta en el carrito
    for item in carrito_items:
        Renta.objects.create(
            herramienta=item.herramienta,
            arrendatario=arrendatario,
            fecha_inicio=item.fecha_inicio,
            fecha_fin=item.fecha_fin,
            costo_total=item.costo_total,
            estado="Activa"
        )

    # Limpiar el carrito después de confirmar la renta
    carrito_items.delete()

    messages.success(request, "¡La renta se ha confirmado correctamente!")
    return redirect('arrendatario_home')  # Redirige a la página del arrendatario

@staff_member_required
def admin_home(request):
    """
    Vista del administrador para ver herramientas pendientes y decidir su aprobación o rechazo.
    """
    pending_tools = Tool.objects.filter(estado='Pendiente')  # Obtener solo las herramientas en estado "Pendiente"
    return render(request, 'admin/admin_home.html', {'pending_tools': pending_tools})

@staff_member_required
@require_POST
def approve_tool(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id)
    tool.estado = 'Disponible'
    tool.save()
    return redirect('admin_home')  # Redirige al home del administrador después de aprobar

@staff_member_required
@require_POST
def reject_tool(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id)
    tool.estado = 'Rechazado'
    tool.save()
    return redirect('admin_home')  # Redirige al home del administrador después de rechazar
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
        messages.error(request, "No se encontró un perfil de arrendatario.")
        return redirect("carrito")

    carrito_items = Carrito.objects.filter(arrendatario=arrendatario)
    if not carrito_items:
        messages.error(request, "No tienes herramientas en el carrito.")
        return redirect("carrito")

    ultimo_chat_id = None  # Variable para guardar el ID del último chat creado

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

        # Guardar el ID del último chat creado
        ultimo_chat_id = chat.id

    # Vaciar el carrito
    carrito_items.delete()

    # Redirigir al chat recién creado
    if ultimo_chat_id:
        messages.success(request, "Renta completada exitosamente y chat creado.")
        return redirect(reverse("ver_chat", args=[ultimo_chat_id]))

    # Si no se creó ningún chat, redirigir al home del arrendatario
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

    # Guarda el access_token en la sesión para usarlo después
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
        'pickup_address': '123 Calle Falsa, Ciudad',  # Cambia estos datos según sea necesario
        'dropoff_address': '456 Avenida Verdadera, Ciudad',
    }
    response = requests.post(url, headers=headers, json=data)

    return JsonResponse(response.json())