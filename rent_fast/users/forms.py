from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Arrendador, Arrendatario, Direccion

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('arrendador', 'Arrendador'),
        ('arrendatario', 'Arrendatario'),
    )

    # Campo para seleccionar el rol
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
    nombre = forms.CharField(max_length=100, required=True)
    apellidos = forms.CharField(max_length=100, required=True)
    telefono = forms.CharField(max_length=15, required=True)
    correo = forms.EmailField(required=True)
    
    # Campos para la dirección
    calle = forms.CharField(max_length=255, required=True)
    ciudad = forms.CharField(max_length=100, required=True)
    estado = forms.CharField(max_length=100, required=True)
    codigo_postal = forms.CharField(max_length=10, required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role', 'nombre', 'apellidos', 'telefono', 'correo', 'calle', 'ciudad', 'estado', 'codigo_postal']
