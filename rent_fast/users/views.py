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

    def get(self, *args, **kwargs):
        # Si el usuario ya está autenticado, redirigir directamente al segundo paso
        if self.request.user.is_authenticated and not self.request.user.has_perm('app.perfil_completo'):  # puedes usar una marca para verificar si ya tiene perfil
            return redirect('register_personal')  # Redirige a la página de info personal
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        step = self.steps.current

        if step == 'personal':
            form = self.get_form(data=self.request.POST, files=self.request.FILES)
            if form.is_valid():
                ine_image = form.cleaned_data.get('ine_image')
                ine_verification_status = self.verify_ine(ine_image)
                if not ine_verification_status:
                    messages.error(self.request, "La verificación del documento INE falló. Inténtalo nuevamente.")
                    return self.render_to_response(self.get_context_data(form=form))
                messages.success(self.request, "¡El documento INE fue verificado con éxito!")
                return self.render_next_step(form)

        return super().post(*args, **kwargs)

    def done(self, form_list, **kwargs):
        form_data = [form.cleaned_data for form in form_list]

        if not self.request.user.is_authenticated:
            user_data = form_data[0]
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password1'],
            )
        else:
            user = self.request.user  # Usuario autenticado con Google

        address_data = form_list[2]
        direccion = Direccion.objects.create(
            calle=address_data.cleaned_data['calle'],
            ciudad=address_data.cleaned_data['ciudad'],
            estado=address_data['estado'],
            codigo_postal=address_data['codigo_postal'],
        )

        personal_form = form_list[1]
        personal_form.save(user, direccion)

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
