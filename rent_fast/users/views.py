from django.views import generic
from .forms import ProductForm
from django.urls import reverse_lazy
from products.models import Product

# Create your views here.
class LoginFormView(generic.FormView):
    template_name="login/login.html"
    form_class = ProductForm
    success_url = reverse_lazy("add_product")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class RegisterFormView(generic.ListView):
    model = Product
    template_name = "login/register.html"
    context_object_name = "products"