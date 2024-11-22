from django import forms
from django.contrib.auth.models import User
from .models import Direccion, Arrendador, Arrendatario
import re
 
class RetiroForm(forms.Form):
    """
    Formulario para realizar un retiro de dinero.
    Permite al usuario ingresar la cantidad que desea retirar.
    
    Campos:
    - monto: Un campo decimal que representa la cantidad a retirar.
    """
    monto = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Cantidad a retirar",
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Monto'})
    )
 
# Paso 1: Formulario de información básica de usuario
class UserForm(forms.ModelForm):
    """
    Formulario para capturar la información básica del usuario al registrarse.
    Incluye campos para el nombre de usuario, correo electrónico y contraseñas.
    Valida que ambas contraseñas coincidan y que cumplan con los requisitos de seguridad.
    """
    email = forms.EmailField(
        label="Correo Electrónico",
        required=True,
        help_text="Introduce un correo electrónico válido.",
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Por favor, introduce un correo electrónico válido.',
        }
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'id_password1', 'class': 'form-input'}),
        label="Contraseña",
        help_text="La contraseña debe tener al menos 8 caracteres, incluyendo una mayúscula, una minúscula, un número y un carácter especial."
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'id_password2', 'class': 'form-input'}),
        label="Confirmar Contraseña"
    )
 
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
 
 
# Paso 2: Formulario de información personal (con selección de rol y foto de perfil)
class PersonalInfoForm(forms.Form):
    """
    Formulario para capturar información personal del usuario y su rol en la plataforma.
    """
    ROLE_CHOICES = [
        ('arrendador', 'Arrendador'),
        ('arrendatario', 'Arrendatario'),
    ]
    
    nombre = forms.CharField(max_length=100, label="Nombre")
    apellidos = forms.CharField(max_length=100, label="Apellidos")
    telefono = forms.CharField(max_length=15, label="Teléfono")
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, label="¿Qué serás?")
    ine_image = forms.ImageField(label="Sube tu INE Mexicano", required=True, widget=forms.ClearableFileInput(attrs={'id': 'id_ine_image'}))
    profile_picture = forms.ImageField(label="Foto de perfil", required=False)
    
    def clean_nombre(self):
        """
        Valida que el campo nombre solo contenga letras y espacios.
        """
        nombre = self.cleaned_data.get('nombre')
        if not nombre.replace(" ", "").isalpha():
            raise forms.ValidationError("El nombre solo puede contener letras y espacios.")
        return nombre
    
    def clean_apellidos(self):
        """
        Valida que el campo apellidos solo contenga letras y espacios.
        """
        apellidos = self.cleaned_data.get('apellidos')
        if not apellidos.replace(" ", "").isalpha():
            raise forms.ValidationError("Los apellidos solo pueden contener letras y espacios.")
        return apellidos
    
    def clean_telefono(self):
        """
        Valida que el campo teléfono solo contenga números y tenga exactamente 10 dígitos.
        """
        telefono = self.cleaned_data.get('telefono')
        if not telefono.isdigit():
            raise forms.ValidationError("El teléfono solo puede contener números.")
        if len(telefono) != 10:
            raise forms.ValidationError("El teléfono debe tener 10 dígitos.")
        return telefono
 
    def save(self, user, direccion):
        """
        Guarda la información del perfil del usuario en la base de datos.
        Crea un perfil de Arrendador o Arrendatario según el rol seleccionado y
        asocia la dirección, imagen del INE y foto de perfil.
        """
        role = self.cleaned_data.get('role')
        if role == 'arrendador':
            return Arrendador.objects.create(
                usuario=user,
                nombre=self.cleaned_data['nombre'],
                apellidos=self.cleaned_data['apellidos'],
                telefono=self.cleaned_data['telefono'],
                ine_image=self.cleaned_data['ine_image'],
                profile_picture=self.cleaned_data.get('profile_picture'),  # Guarda la foto de perfil
                direccion=direccion
            )
        else:
            return Arrendatario.objects.create(
                usuario=user,
                nombre=self.cleaned_data['nombre'],
                apellidos=self.cleaned_data['apellidos'],
                telefono=self.cleaned_data['telefono'],
                ine_image=self.cleaned_data['ine_image'],
                profile_picture=self.cleaned_data.get('profile_picture'),  # Guarda la foto de perfil
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
        fields = ['calle', 'colonia', 'codigo_postal', 'ciudad', 'estado' ]
 
class UpdateAddressForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['calle', 'colonia', 'ciudad', 'estado', 'codigo_postal']  # Incluye 'colonia'
        widgets = {
            'calle': forms.TextInput(attrs={'class': 'form-input'}),
            'colonia': forms.TextInput(attrs={'class': 'form-input'}),  # Widget para 'colonia'
            'ciudad': forms.TextInput(attrs={'class': 'form-input'}),
            'estado': forms.TextInput(attrs={'class': 'form-input'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-input'}),
        }
 
from django import forms
from .models import Arrendador, Arrendatario
 
class EditarArrendadorForm(forms.ModelForm):
    """
    Formulario para editar la información de un Arrendador.
    """
    class Meta:
        model = Arrendador
        fields = ['nombre', 'apellidos', 'telefono', 'correo', 'profile_picture']
 
class EditarArrendatarioForm(forms.ModelForm):
    """
    Formulario para editar la información de un Arrendatario.
    """
    class Meta:
        model = Arrendatario
        fields = ['nombre', 'apellidos', 'telefono', 'correo', 'profile_picture']