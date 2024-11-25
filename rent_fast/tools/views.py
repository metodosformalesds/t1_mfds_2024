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
    """
    Vista para obtener una cotización de envío utilizando la API de Uber.

    Requiere que el usuario esté autenticado en Uber y que las direcciones de 
    arrendador y arrendatario estén disponibles.

    Parámetros:
    - tool_id: ID de la herramienta para la que se solicita la cotización.

    Si el token de acceso de Uber está disponible, obtiene las coordenadas de las 
    direcciones de arrendador y arrendatario utilizando geopy, luego realiza una 
    solicitud a la API de Uber para obtener la cotización del envío entre las dos ubicaciones.

    Devuelve:
    - Una respuesta con la cotización si la solicitud es exitosa.
    - Un error si no se pueden obtener las ubicaciones o la cotización de Uber.
    """
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
    """
    Inicia el proceso de autenticación con Uber redirigiendo al usuario a la página de inicio de sesión de Uber.

    Devuelve:
    - Redirección a la página de autenticación de Uber.
    """
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
    """
    Recibe el código de autorización de Uber y obtiene el token de acceso para realizar solicitudes a la API de Uber.

    Parámetros:
    - request: Objeto de la solicitud que contiene el código de autorización.

    Devuelve:
    - Redirección al flujo de cotización o un mensaje de error si la autorización no fue exitosa.
    """
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
    Vista principal que redirige a diferentes páginas de inicio según el rol del usuario.

    Devuelve:
    - Redirección al home del administrador, arrendador o arrendatario, o una página de error si no tiene rol.
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
    """
    Vista principal para los arrendadores, mostrando sus herramientas organizadas por estado.

    Devuelve:
    - Página con las herramientas del arrendador, agrupadas por estado (pendiente, rechazada, disponible).
    """
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

    
from django.db.models import Q

@login_required
def arrendatario_home(request):
    """
    Vista principal para los arrendatarios, con un sistema de búsqueda y filtrado de herramientas disponibles.
    """ 
    search_query = request.GET.get('search', '')  # Captura el texto ingresado en el buscador
    precio_minimo = request.GET.get('precio_minimo', None)
    precio_maximo = request.GET.get('precio_maximo', None)
    categoria_id = request.GET.get('categoria', None)

    # Filtrar herramientas disponibles
    herramientas = Tool.objects.filter(estado="Disponible")

    # Aplicar filtros según lo ingresado
    if search_query:
        herramientas = herramientas.filter(
            Q(nombre__icontains=search_query) |
            Q(categoria__nombre__icontains=search_query) |
            Q(arrendador__direccion__colonia__icontains=search_query)  # Ajusta al campo real
        )

    if precio_minimo:
        herramientas = herramientas.filter(costo_dia__gte=precio_minimo)
    if precio_maximo:
        herramientas = herramientas.filter(costo_dia__lte=precio_maximo)
    if categoria_id:
        herramientas = herramientas.filter(categoria__id=categoria_id)

    # Agrupar herramientas por categoría
    categorias = Categoria.objects.all()
    herramientas_por_categoria = {
        categoria.nombre: herramientas.filter(categoria=categoria)[:5]
        for categoria in categorias
    }

    # Herramientas sin categoría
    herramientas_sin_categoria = herramientas.filter(categoria__isnull=True)

    return render(request, 'arrendatarios/arrendatario_home_new.html', {
        'herramientas_sin_categoria': herramientas_sin_categoria,
        'herramientas_por_categoria': herramientas_por_categoria,
        'search_query': search_query,
    })


class ToolFormView(LoginRequiredMixin, generic.FormView):
    """
    Vista para permitir a los arrendadores agregar nuevas herramientas.

    Este formulario permite que un arrendador agregue una nueva herramienta a la plataforma.
    Después de la validación del formulario, la herramienta se guarda y se asocia con el arrendador autenticado.

    Atributos:
    - template_name (str): La plantilla HTML que se renderiza para mostrar el formulario.
    - form_class (Form): El formulario que se utilizará para la entrada de datos.
    - success_url (str): La URL a la que se redirige después de que el formulario se haya guardado correctamente.

    Métodos:
    - form_valid(form): Guarda la herramienta y redirige a la lista de herramientas después de la validación exitosa del formulario.
    """
    template_name = "tools/add_tool.html"
    form_class = ToolForm
    success_url = reverse_lazy("list_tool")

    def form_valid(self, form):
        """
    Vista para listar todas las herramientas disponibles en la plataforma.

    Esta vista muestra todas las herramientas en un formato de lista.
    Solo las herramientas que estén disponibles o aprobadas serán visibles para los usuarios.

    Atributos:
    - model (Model): El modelo de datos asociado con esta vista (en este caso, Tool).
    - template_name (str): La plantilla que se usará para renderizar la lista de herramientas.
    - context_object_name (str): Nombre de la variable de contexto que contiene las herramientas.
    """  
        # Obtenemos el perfil de arrendador del usuario autenticado
        try:
            arrendador = Arrendador.objects.get(usuario=self.request.user)
            form.save(arrendador=arrendador)  # Guardar la herramienta asociada al arrendador
        except Arrendador.DoesNotExist:
            return redirect('no_role')  # Redirigir a una p gina de error si no es arrendador
        return super().form_valid(form)

class ToolListView(generic.ListView):
    """
    Vista para mostrar los detalles de una herramienta específica.

    Esta vista permite que los usuarios vean detalles de una herramienta, incluidas las reseñas y preguntas.
    Además, si el arrendatario ha alquilado la herramienta, podrá dejar una reseña.

    Atributos:
    - model (Model): El modelo de datos asociado con esta vista (en este caso, Tool).
    - template_name (str): La plantilla que se usará para renderizar los detalles de la herramienta.
    - context_object_name (str): Nombre de la variable de contexto que contiene la herramienta.

    Métodos:
    - get_context_data(): Agrega información adicional al contexto, como reseñas, disponibilidad, preguntas y formularios.
    - post(): Maneja los formularios enviados por el usuario para dejar una reseña o hacer una pregunta sobre la herramienta.
    """
    model = Tool
    template_name = "tools/list_tool.html"
    context_object_name = "tools"

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


from django.db.models import Q

class ToolDetailView(DetailView):
    model = Tool
    template_name = "tools/tool_details.html"
    context_object_name = 'tool'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tool = self.get_object()
        user = self.request.user
        arrendatario = getattr(user, 'arrendatario', None)

        # Indicar si la herramienta está en el carrito del usuario
        if arrendatario:
            context['en_carrito'] = Carrito.objects.filter(
                herramienta=tool,
                arrendatario=arrendatario
            ).exists()
        else:
            context['en_carrito'] = False

        # Información existente (rentas activas, reseñas, etc.)
        context['resenas'] = Resena.objects.filter(herramienta=tool)
        context['ha_alquilado_y_finalizado'] = (
            arrendatario and Renta.objects.filter(
                herramienta=tool,
                arrendatario=arrendatario,
                estado="Finalizada"
            ).exists()
        )
        context['form'] = ResenaForm() if context['ha_alquilado_y_finalizado'] else None

        renta_activa = Renta.objects.filter(herramienta=tool, estado="Activa").first()
        if renta_activa:
            context['renta_activa'] = renta_activa

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

from django.contrib import messages

@login_required
def add_tool_view(request):
    """
    Vista para agregar una herramienta nueva al sistema por parte de un arrendador.

    Esta vista presenta un formulario para que los arrendadores agreguen nuevas herramientas,
    y les permite subir imágenes y establecer el precio de alquiler.

    Devuelve:
    - Un formulario de herramienta si el método es GET.
    - Un mensaje de éxito si la herramienta se guarda correctamente.
    """
    arrendador = Arrendador.objects.get(usuario=request.user)  # Obtener el arrendador
    if request.method == 'POST':
        form = ToolForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(arrendador=arrendador)  # Guardar la herramienta con estado "Pendiente"
            messages.success(request, "¡Tu publicación fue enviada con éxito y está en revisión!")
            return redirect('arrendador_home')  # Redirige después de crear la herramienta
        else:
            messages.error(request, "Hubo un problema con tu publicación. Por favor revisa los campos.")
    else:
        form = ToolForm()
    return render(request, 'arrendadores/add_tool.html', {'form': form})


    
@login_required
def carrito_view(request):
    """
    Vista para mostrar el carrito de compras de un arrendatario.

    Muestra las herramientas que el arrendatario ha agregado a su carrito y calcula el costo total de la renta.

    Devuelve:
    - Una vista con los elementos del carrito y el costo total de la renta.
    """
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
    """
    Vista para seleccionar las fechas de inicio y fin para alquilar una herramienta.

    Esta vista muestra un formulario para que el arrendatario seleccione las fechas 
    de inicio y fin de la renta de una herramienta. También verifica la disponibilidad 
    de la herramienta en las fechas seleccionadas.

    Parámetros:
    - tool_id: ID de la herramienta para la que se seleccionan las fechas de alquiler.

    Devuelve:
    - Un formulario para seleccionar fechas y una lista de fechas ocupadas si la herramienta está 
      ya alquilada en algún período.
    """
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
    """
    Vista para agregar una herramienta al carrito de un arrendatario.

    Esta vista permite que un arrendatario agregue una herramienta seleccionada a su carrito 
    después de haber elegido las fechas de renta. También verifica la disponibilidad de la herramienta 
    y si ya está en el carrito.

    Parámetros:
    - tool_id: ID de la herramienta que se va a agregar al carrito.

    Devuelve:
    - Redirige al carrito después de agregar la herramienta si la operación es exitosa.
    - Muestra un mensaje de error si la herramienta no está disponible o si ya está en el carrito.
    """
    herramienta = get_object_or_404(Tool, id=tool_id)
    arrendatario = getattr(request.user, 'arrendatario', None)

    if not arrendatario:
        return render(request, 'tools/no_role.html', {'error': "Necesitas un perfil de arrendatario para alquilar herramientas."})

    # Verificar disponibilidad de la herramienta
    if not herramienta.is_available():
        messages.error(request, "Esta herramienta ya está en renta y no está disponible.")
        return redirect('tool_detail', pk=tool_id)

    # Verificar si la herramienta ya está en el carrito
    if Carrito.objects.filter(arrendatario=arrendatario, herramienta=herramienta).exists():
        messages.error(request, "Esta herramienta ya está en tu carrito.")
        return redirect('tool_detail', pk=tool_id)

    # Obtener fechas y calcular costo
    fecha_inicio = request.session.get('fecha_inicio')
    fecha_fin = request.session.get('fecha_fin')

    if fecha_inicio and fecha_fin:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        dias_renta = (fecha_fin - fecha_inicio).days + 1
        costo_total = dias_renta * herramienta.costo_dia

        # Agregar herramienta al carrito
        Carrito.objects.create(
            arrendatario=arrendatario,
            herramienta=herramienta,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            costo_total=costo_total
        )
        messages.success(request, "Herramienta agregada al carrito correctamente.")
        return redirect('carrito')

    messages.error(request, "Debes seleccionar las fechas antes de agregar la herramienta al carrito.")
    return redirect('seleccionar_fechas', tool_id=tool_id)

@login_required
def rent_tool_view(request, tool_id):
    """
    Vista para procesar el alquiler de una herramienta.

    Esta vista crea una nueva renta para la herramienta seleccionada por el arrendatario. 
    Se obtiene el formulario de renta, se calcula el costo total y se guarda la renta.

    Parámetros:
    - tool_id: ID de la herramienta que se va a alquilar.

    Devuelve:
    - Redirige al carrito después de que se confirma el alquiler.
    """ 
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
    """
    Vista para mostrar el resumen de las herramientas en el carrito del arrendatario.

    Esta vista muestra el resumen de las herramientas que el arrendatario ha agregado a su carrito, 
    así como el monto total de la renta.

    Devuelve:
    - Una vista con los elementos del carrito y el costo total de la renta.
    """ 
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
    """
    Vista para confirmar la renta de las herramientas en el carrito.

    Esta vista procesa las herramientas que un arrendatario tiene en su carrito. Si el arrendatario 
    tiene herramientas en el carrito, se crean las rentas correspondientes, se actualiza su estado 
    a "Activa" y se genera una notificación para el arrendador.

    Devuelve:
    - Redirige al inicio del arrendatario con un mensaje de éxito si la renta se confirma correctamente.
    - Redirige al carrito si no hay herramientas en el carrito.
    """
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
    Vista del administrador para ver herramientas pendientes y decidir su aprobación o rechazo.

    Esta vista muestra las herramientas que están en estado 'Pendiente'. El administrador puede decidir 
    aprobar o rechazar estas herramientas.

    Devuelve:
    - Una lista de herramientas pendientes para su aprobación o rechazo.
    """
    pending_tools = Tool.objects.filter(estado='Pendiente')  # Obtener solo las herramientas en estado "Pendiente"
    return render(request, 'admin/admin_home.html', {'pending_tools': pending_tools})


@staff_member_required
@require_POST
def approve_tool(request, tool_id):
    """
    Vista para aprobar una herramienta y cambiar su estado a 'Disponible'.

    El administrador puede aprobar una herramienta que está en estado 'Pendiente', 
    lo que cambia su estado a 'Disponible' y genera una notificación para el arrendador.

    Parámetros:
    - tool_id: ID de la herramienta a aprobar.

    Devuelve:
    - Redirige al home del administrador después de aprobar la herramienta.
    """
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
    """
    Vista para rechazar una herramienta y cambiar su estado a 'Rechazado'.

    El administrador puede rechazar una herramienta en estado 'Pendiente', lo que cambia su estado 
    a 'Rechazado' y envía una notificación al arrendador con el motivo del rechazo.

    Parámetros:
    - tool_id: ID de la herramienta a rechazar.

    Devuelve:
    - Redirige al home del administrador después de rechazar la herramienta.
    """
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

    Esta vista muestra todas las herramientas que están pendientes de aprobación, es decir, en estado 'Pendiente'.

    Devuelve:
    - Una lista de herramientas pendientes.
    """
    """
    Vista para que el administrador vea todas las herramientas pendientes.
    """
    pending_tools = Tool.objects.filter(estado='Pendiente')
    return render(request, 'admin/admin_pending_tools.html', {'pending_tools': pending_tools})
    
def pagar_sin_paypal_view(request):
    """
    Vista para procesar el pago sin PayPal y crear las rentas y chats.

    Esta vista permite que el arrendatario confirme la renta de las herramientas en el carrito sin usar PayPal. 
    Crea las rentas, los chats entre el arrendatario y el arrendador, y vacía el carrito.

    Devuelve:
    - Redirige al chat creado después de la renta exitosa o al inicio si hubo un error.
    """
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
    """
    Inicia el proceso de autenticación con Uber.

    Redirige al usuario a la página de autorización de Uber para permitir que la aplicación 
    acceda a su cuenta y reciba un token de acceso para futuras solicitudes.

    Devuelve:
    - Redirige a la página de autenticación de Uber.
    """
    auth_url = (
        "https://login.uber.com/oauth/v2/authorize"
        f"?client_id={settings.UBER_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={settings.UBER_REDIRECT_URI}"
        "&scope=delivery"  # Ajusta el scope si es necesario
    )
    return redirect(auth_url)

def uber_callback(request):
    """
    Recibe el código de autorización de Uber y obtiene el token de acceso.

    Este proceso intercambia el código de autorización por un token de acceso que se utiliza 
    para hacer solicitudes a la API de Uber.

    Devuelve:
    - Un JSON con el token de acceso si la autenticación es exitosa.
    """
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
    """
    Obtiene una cotización de Uber para el envío entre el arrendador y el arrendatario.

    Utiliza el token de acceso de Uber para hacer una solicitud a la API de Uber y obtener 
    una estimación del costo del envío entre el arrendador y el arrendatario.

    Devuelve:
    - Un JSON con la cotización de Uber si la solicitud es exitosa.
    - Un mensaje de error si el usuario no está autenticado con Uber o si ocurre algún error en la solicitud.
    """
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
    """
    Muestra los detalles de una herramienta, incluyendo reseñas y la opción de dejar una nueva reseña.

    Esta vista también verifica si el arrendatario ha alquilado y finalizado la herramienta, 
    permitiendo dejar una reseña solo si es así. Además, se calcula el promedio de las calificaciones.

    Parámetros:
    - herramienta_id: ID de la herramienta a mostrar.

    Devuelve:
    - Una vista con los detalles de la herramienta, las reseñas y el formulario para agregar una reseña.
    """ 
    herramienta = get_object_or_404(Tool, id=herramienta_id)
    resenas = Resena.objects.filter(herramienta=herramienta)
    promedio_calificacion = resenas.aggregate(Avg('calificacion'))['calificacion__avg']

    ha_alquilado_y_finalizado = Renta.objects.filter(
        herramienta=herramienta,
        arrendatario=request.user.arrendatario,
        estado="Finalizada"
    ).exists()

    ha_dejado_resena = Resena.objects.filter(
        herramienta=herramienta,
        arrendatario=request.user.arrendatario
    ).exists()

    if request.method == 'POST' and ha_alquilado_y_finalizado and not ha_dejado_resena:
        form = ResenaForm(request.POST)
        if form.is_valid():
            resena = form.save(commit=False)
            resena.arrendatario = request.user.arrendatario
            resena.herramienta = herramienta
            resena.save()
            messages.success(request, "¡Reseña enviada exitosamente!")
            return redirect('tool_detail', herramienta_id=herramienta.id)
        else:
            messages.error(request, "Hubo un error al enviar tu reseña. Por favor intenta nuevamente.")
    else:
        form = ResenaForm()

    context = {
        'herramienta': herramienta,
        'resenas': resenas,
        'promedio_calificacion': promedio_calificacion,
        'ha_alquilado_y_finalizado': ha_alquilado_y_finalizado,
        'ha_dejado_resena': ha_dejado_resena,
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
    """
    Permite a un arrendador editar los detalles de una herramienta.

    Esta vista permite al arrendador modificar los detalles de una herramienta que no esté en renta activa. 
    Si la herramienta está en renta activa, no se puede editar.

    Parámetros:
    - tool_id: ID de la herramienta que se desea editar.

    Devuelve:
    - Redirige al home del arrendador después de editar la herramienta si la operación es exitosa.
    - Muestra un mensaje de error si la herramienta está en renta activa.
    """
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
    """
    Permite a un arrendador eliminar una herramienta de su inventario.

    Esta vista permite al arrendador eliminar una herramienta solo si no está en renta activa. Si la herramienta 
    está en renta activa, no se podrá eliminar.

    Parámetros:
    - tool_id: ID de la herramienta que se desea eliminar.

    Devuelve:
    - Redirige al home del arrendador después de eliminar la herramienta si la operación es exitosa.
    - Muestra un mensaje de error si la herramienta está en renta activa.
    """
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
    """
    Vista para que el administrador revise los detalles de una herramienta.

    Esta vista permite al administrador ver los detalles completos de una herramienta antes de tomar 
    una decisión sobre su aprobación o rechazo.

    Parámetros:
    - tool_id: ID de la herramienta a revisar.

    Devuelve:
    - Una vista con los detalles de la herramienta.
    """
    herramienta = get_object_or_404(Tool, id=tool_id)  # Obtener la herramienta específica
    return render(request, 'admin/revision_tool.html', {'herramienta': herramienta})


@login_required
def eliminar_del_carrito_view(request, item_id):
    """
    Elimina una herramienta del carrito del arrendatario.

    Esta vista permite al arrendatario eliminar una herramienta específica de su carrito de compras.

    Parámetros:
    - item_id: ID del artículo en el carrito que se desea eliminar.

    Devuelve:
    - Redirige a la página del carrito después de eliminar el artículo.
    """
    item = get_object_or_404(Carrito, id=item_id, arrendatario=request.user.arrendatario)
    
    item.delete()
    messages.success(request, "El artículo ha sido eliminado del carrito.")
    return redirect("carrito")  # Redirige a la página del carrito después de eliminar