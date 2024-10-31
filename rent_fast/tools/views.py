from django.views import generic
from .forms import ToolForm, RentaForm, CarritoForm
from users.models import Arrendador, Arrendatario
from .models import Tool, Carrito
from rentas.models import Renta
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from datetime import datetime
from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, fields
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST

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
    """
    Vista para el home del Arrendatario.
    """
    search_query = request.GET.get('search', '')  # Recoge el valor de búsqueda (si existe)
    
    # Filtrar las herramientas con estado "Disponible" y aplicar el filtro de búsqueda si está presente
    tools = Tool.objects.filter(
        estado="Disponible",
        nombre__icontains=search_query  # Aplica el filtro de búsqueda por nombre
    )
    
    return render(request, "arrendatarios/arrendatario_home_new.html", {
        'tools': tools,
        'search_query': search_query
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
    
