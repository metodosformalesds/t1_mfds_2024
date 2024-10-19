from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from .models import Arrendador, Arrendatario, Direccion
from .forms import CustomUserCreationForm

class RegisterView(generic.CreateView):
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        # Guardar el usuario
        user = form.save()

        # Crear la dirección
        direccion = Direccion.objects.create(
            calle=form.cleaned_data.get('calle'),
            ciudad=form.cleaned_data.get('ciudad'),
            estado=form.cleaned_data.get('estado'),
            codigo_postal=form.cleaned_data.get('codigo_postal'),
        )

        # Crear el perfil de arrendador o arrendatario según la selección
        role = form.cleaned_data.get('role')
        if role == 'arrendador':
            Arrendador.objects.create(
                usuario=user,
                nombre=form.cleaned_data.get('nombre'),
                apellidos=form.cleaned_data.get('apellidos'),
                telefono=form.cleaned_data.get('telefono'),
                correo=form.cleaned_data.get('correo'),
                direccion=direccion,
            )
        elif role == 'arrendatario':
            Arrendatario.objects.create(
                usuario=user,
                nombre=form.cleaned_data.get('nombre'),
                apellidos=form.cleaned_data.get('apellidos'),
                telefono=form.cleaned_data.get('telefono'),
                correo=form.cleaned_data.get('correo'),
                direccion=direccion,
            )

        return redirect(self.success_url)
