from django.views import generic
from .forms import ToolForm
from .models import Tool
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class ToolFormView(LoginRequiredMixin, generic.FormView):
    template_name = "tools/add_tool.html"
    form_class = ToolForm
    success_url = reverse_lazy("list_tool")

    def form_valid(self, form):
        arrendador = self.request.user.arrendador
        form.save(arrendador=arrendador)  
        return super().form_valid(form)

class ToolListView(generic.ListView):
    model = Tool
    template_name = "tools/list_tool.html"
    context_object_name = "tools"
