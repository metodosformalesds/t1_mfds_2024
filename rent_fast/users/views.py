from formtools.wizard.views import SessionWizardView
from django.contrib.auth.models import User
from django.shortcuts import redirect
from .forms import UserForm, PersonalInfoForm, AddressForm
from .models import Arrendador, Arrendatario, Direccion

FORMS = [
    ('user', UserForm),
    ('personal', PersonalInfoForm),
    ('address', AddressForm),
]

TEMPLATES = {
    'user': 'users/register_user.html',
    'personal': 'users/register_personal.html',
    'address': 'users/register_address.html',
}

class RegisterWizard(SessionWizardView):
    form_list = FORMS
    template_name = 'users/register_wizard.html'

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        # Extraer los datos de cada formulario
        form_data = [form.cleaned_data for form in form_list]

        # Paso 1: Crear el usuario
        user_data = form_data[0]
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password1'],
        )

        # Paso 2: Crear el perfil con los datos personales y el rol seleccionado
        personal_data = form_data[1]

        # Paso 3: Crear la dirección del usuario
        address_data = form_data[2]
        direccion = Direccion.objects.create(
            calle=address_data['calle'],
            ciudad=address_data['ciudad'],
            estado=address_data['estado'],
            codigo_postal=address_data['codigo_postal'],
        )

        # Determinar si el usuario será arrendador o arrendatario
        role = personal_data['role']
        if role == 'arrendador':
            Arrendador.objects.create(
                usuario=user,
                nombre=personal_data['nombre'],
                apellidos=personal_data['apellidos'],
                telefono=personal_data['telefono'],
                correo=user.email,
                direccion=direccion,
            )
        else:
            Arrendatario.objects.create(
                usuario=user,
                nombre=personal_data['nombre'],
                apellidos=personal_data['apellidos'],
                telefono=personal_data['telefono'],
                correo=user.email,
                direccion=direccion,
            )

        return redirect('login')
