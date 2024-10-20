from django import forms
from django.contrib.auth.models import User
from .models import Direccion

# Paso 1: Formulario de información básica de usuario
class UserForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

# Paso 2: Formulario de información personal (con selección de rol)
class PersonalInfoForm(forms.Form):
    ROLE_CHOICES = [
        ('arrendador', 'Arrendador'),
        ('arrendatario', 'Arrendatario'),
    ]

    nombre = forms.CharField(max_length=100, label="Nombre")
    apellidos = forms.CharField(max_length=100, label="Apellidos")
    telefono = forms.CharField(max_length=15, label="Teléfono")
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, label="¿Qué serás?")

# Paso 3: Formulario de dirección
class AddressForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['calle', 'ciudad', 'estado', 'codigo_postal']
