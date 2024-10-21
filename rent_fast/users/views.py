import requests
import base64
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib import messages  
from django.shortcuts import redirect
from formtools.wizard.views import SessionWizardView
from .forms import UserForm, PersonalInfoForm, AddressForm
from .models import Arrendador, Arrendatario, Direccion
from django.conf import settings

# Configura el almacenamiento de archivos
file_storage = FileSystemStorage(location='media/tmp')

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
    file_storage = file_storage  # Añadir el almacenamiento de archivos

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def post(self, *args, **kwargs):
        """
        Sobrescribir la función `post` para realizar la verificación antes de avanzar al siguiente paso.
        """
        step = self.steps.current

        # Solo verificar el INE en el paso "personal"
        if step == 'personal':
            # Verificar el formulario y la imagen del INE
            form = self.get_form(data=self.request.POST, files=self.request.FILES)
            if form.is_valid():
                ine_image = form.cleaned_data.get('ine_image')
                ine_verification_status = self.verify_ine(ine_image)

                # Si la verificación falla, muestra un error y no avances
                if not ine_verification_status:
                    messages.error(self.request, "La verificación del documento INE falló. Inténtalo nuevamente.")
                    return self.render_to_response(self.get_context_data(form=form))

                # Si la verificación es exitosa, muestra un mensaje de éxito y avanza al siguiente paso
                messages.success(self.request, "¡El documento INE fue verificado con éxito!")
                # Avanzar al siguiente paso (dirección)
                return self.render_next_step(form)

        # Continuar normalmente con el flujo del wizard
        return super().post(*args, **kwargs)

    def done(self, form_list, **kwargs):
        """
        Lógica cuando se completan todos los pasos del wizard.
        """
        # Extraer los datos de cada formulario
        form_data = [form.cleaned_data for form in form_list]

        # Paso 1: Crear el usuario
        user_data = form_data[0]
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password1'],
        )

        # Paso 2: Crear la dirección del usuario
        address_data = form_list[2]
        direccion = Direccion.objects.create(
            calle=address_data.cleaned_data['calle'],
            ciudad=address_data.cleaned_data['ciudad'],
            estado=address_data.cleaned_data['estado'],
            codigo_postal=address_data.cleaned_data['codigo_postal'],
        )

        # Paso 3: Guardar el perfil del usuario y la imagen del INE
        personal_form = form_list[1]
        user_profile = personal_form.save(user, direccion)

        return redirect('login')

    def verify_ine(self, ine_image):
        """
        Verificar el INE utilizando la API de IDAnalyzer.
        """
        api_key = settings.IDANALYZER_API_KEY  
        api_url = 'https://api2.idanalyzer.com/quickscan'

        # Leer el archivo de la imagen y convertirlo a Base64
        ine_image_file = ine_image.read()
        ine_image_base64 = base64.b64encode(ine_image_file).decode('utf-8')

        # Preparar los datos para la solicitud
        data = {
            'document': ine_image_base64,
            'ocr_extraction': 'true',  # Extraer datos como nombre, fecha de nacimiento, etc.
        }

        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'X-API-KEY': api_key 
        }

        try:
            # Hacer la solicitud POST a la API
            response = requests.post(api_url, json=data, headers=headers)

            # Imprimir la respuesta para depuración
            print("Código de estado de la API:", response.status_code)
            print("Respuesta de la API:", response.text) 

            if response.status_code == 200:
                # Procesar la respuesta en formato JSON
                result = response.json()
                print("JSON de la respuesta:", result)  
                # Verificar si el documento es válido
                return result.get('success', False)
            else:
                print(f"Error en la solicitud a la API: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"Error en la conexión o solicitud a la API: {e}")
            return False
