from django import forms
from django.contrib.auth.models import User
from .models import Direccion, Arrendador, Arrendatario
import re

# Paso 1: Formulario de información básica de usuario
class UserForm(forms.ModelForm):
    """
    Formulario para capturar la información básica del usuario al registrarse.
    Incluye campos para el nombre de usuario, correo electrónico y contraseñas.
    Valida que ambas contraseñas coincidan y que cumplan con los requisitos de seguridad.
    """
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="Contraseña",
        help_text="La contraseña debe tener al menos 8 caracteres, incluyendo una mayúscula, una minúscula, un número y un carácter especial."
    )
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        """
        Realiza las validaciones del formulario:
        1. Verifica que ambas contraseñas coincidan.
        2. Valida que la contraseña cumpla con los requisitos de longitud y composición:
           - Al menos 8 caracteres.
           - Contiene al menos una letra mayúscula, una minúscula, un número y un carácter especial.
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # Verifica que ambas contraseñas coincidan
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")

        # Validaciones adicionales para la contraseña
        if password1:
            if len(password1) < 8:
                self.add_error('password1', "La contraseña debe tener al menos 8 caracteres.")
            if not re.search(r"[A-Z]", password1):
                self.add_error('password1', "La contraseña debe contener al menos una letra mayúscula.")
            if not re.search(r"[a-z]", password1):
                self.add_error('password1', "La contraseña debe contener al menos una letra minúscula.")
            if not re.search(r"[0-9]", password1):
                self.add_error('password1', "La contraseña debe contener al menos un número.")
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password1):
                self.add_error('password1', "La contraseña debe contener al menos un carácter especial.")

        return cleaned_data

# Paso 2: Formulario de información personal (con selección de rol)
class PersonalInfoForm(forms.Form):
    """
    Formulario para capturar información personal del usuario y su rol en la plataforma.
    Incluye campos para nombre, apellidos, teléfono, rol (arrendador o arrendatario) y carga de imagen INE.
    """
    ROLE_CHOICES = [
        ('arrendador', 'Arrendador'),
        ('arrendatario', 'Arrendatario'),
    ]
    
    nombre = forms.CharField(max_length=100, label="Nombre")
    apellidos = forms.CharField(max_length=100, label="Apellidos")
    telefono = forms.CharField(max_length=15, label="Teléfono")
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, label="¿Qué serás?")
    ine_image = forms.ImageField(label="Subir INE Mexicano", required=True)

    def save(self, user, direccion):
        """
        Guarda la información del perfil del usuario en la base de datos.
        Crea un perfil de Arrendador o Arrendatario según el rol seleccionado y asocia la dirección y la imagen del INE.
        """
        role = self.cleaned_data.get('role')
        if role == 'arrendador':
            return Arrendador.objects.create(
                usuario=user,
                nombre=self.cleaned_data['nombre'],
                apellidos=self.cleaned_data['apellidos'],
                telefono=self.cleaned_data['telefono'],
                ine_image=self.cleaned_data['ine_image'],
                direccion=direccion
            )
        else:
            return Arrendatario.objects.create(
                usuario=user,
                nombre=self.cleaned_data['nombre'],
                apellidos=self.cleaned_data['apellidos'],
                telefono=self.cleaned_data['telefono'],
                ine_image=self.cleaned_data['ine_image'],
                direccion=direccion
            )

# Paso 3: Formulario de dirección
class AddressForm(forms.ModelForm):
    """
    Formulario para capturar la información de dirección del usuario.
    Este formulario se usa para recolectar los datos de ubicación como calle, ciudad, estado y código postal.
    """
    class Meta:
        model = Direccion
        fields = ['calle', 'ciudad', 'estado', 'codigo_postal']
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////