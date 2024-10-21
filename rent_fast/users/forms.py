from django import forms
from django.contrib.auth.models import User
from .models import Direccion, Arrendador, Arrendatario

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
    ine_image = forms.ImageField(label="Subir INE Mexicano", required=True)

    def save(self, user, direccion):
        # Guardar el perfil (Arrendador o Arrendatario) con la imagen del INE
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
    class Meta:
        model = Direccion
        fields = ['calle', 'ciudad', 'estado', 'codigo_postal']
