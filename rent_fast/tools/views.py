from django.views import generic
from .forms import ToolForm
from users.models import Arrendador, Arrendatario
from .models import Tool
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def home_view(request):
    """
    Vista que redirige al home correspondiente según el rol del usuario.
    """
    try:
        if Arrendador.objects.filter(usuario=request.user).exists():
            return redirect('arrendador_home')
        elif Arrendatario.objects.filter(usuario=request.user).exists():
            return redirect('arrendatario_home')
        else:
            # Si el usuario no tiene un perfil de arrendador o arrendatario
            return render(request, "tools/no_role.html")  # Una página que indica que no tiene rol asignado
    except:
        return render(request, "tools/error.html")  # Página de error en caso de fallo inesperado



@login_required
def arrendador_home(request):
    """
    Vista para el home del Arrendador.
    """
    return render(request, "arrendadores/arrendador_home.html")

@login_required
def arrendatario_home(request):
    """
    Vista para el home del Arrendatario.
    """
    search_query = request.GET.get('search', '') # para buscar 
    tools = Tool.objects.all()  # valor de la busqueda
    if search_query:
        tools = tools.filter(nombre__icontains=search_query)# filtrar por buscar
    return render(request, "arrendatarios/arrendatario_home.html", {'tools': tools, 'search_query': search_query})

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
