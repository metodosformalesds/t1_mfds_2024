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
from django.views.generic import TemplateView

# Configura el almacenamiento de archivos
file_storage = FileSystemStorage(location='media/tmp')

# Definición de formularios y plantillas para el asistente de registro
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
    """
    Asistente de registro en varios pasos que permite a los usuarios crear una cuenta y verificar
    su identidad con INE.
    """
    form_list = FORMS
    template_name = 'users/register_wizard.html'
    file_storage = file_storage

    def get_template_names(self):
        """
        Retorna la plantilla correspondiente al paso actual del asistente.
        """
        return [TEMPLATES[self.steps.current]]

    def get(self, *args, **kwargs):
        """
        Redirige al paso 'personal' si el usuario ya está autenticado pero no tiene perfil completo.
        """
        if self.request.user.is_authenticated and not self.request.user.has_perm('app.perfil_completo'):
            return redirect('register_personal')
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Manejo especial para la verificación de INE en el paso 'personal'.
        """
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
        """
        Procesa los datos al completar el asistente de registro.
        Crea el usuario, dirección y datos personales.
        """
        form_data = [form.cleaned_data for form in form_list]

        # Crea el usuario si no está autenticado (nuevo registro)
        if not self.request.user.is_authenticated:
            user_data = form_data[0]
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password1'],
            )
        else:
            user = self.request.user  # Usuario autenticado previamente

        # Procesa y guarda la dirección
        address_data = form_list[2]
        direccion = Direccion.objects.create(
            calle=address_data.cleaned_data['calle'],
            ciudad=address_data.cleaned_data['ciudad'],
            estado=address_data['estado'],
            codigo_postal=address_data['codigo_postal'],
        )

        # Guarda información personal vinculada al usuario y dirección
        personal_form = form_list[1]
        personal_form.save(user, direccion)

        return redirect('login')

    def verify_ine(self, ine_image):
        """
        Verifica el documento INE utilizando la API de IDAnalyzer.
        Convierte la imagen en Base64 y realiza una solicitud POST a la API.
        """
        api_key = settings.IDANALYZER_API_KEY  
        api_url = 'https://api2.idanalyzer.com/quickscan'
        
        # Convierte el archivo de imagen INE a Base64
        ine_image_file = ine_image.read()
        ine_image_base64 = base64.b64encode(ine_image_file).decode('utf-8')

        # Define los datos y encabezados para la solicitud
        data = {
            'document': ine_image_base64,
            'ocr_extraction': 'true',  # Extraer datos adicionales del documento
        }
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'X-API-KEY': api_key
        }

        try:
            # Realiza la solicitud a la API
            response = requests.post(api_url, json=data, headers=headers)
            print("Código de estado de la API:", response.status_code)
            print("Respuesta de la API:", response.text)

            if response.status_code == 200:
                result = response.json()
                return result.get('success', False)
            else:
                print(f"Error en la solicitud a la API: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"Error en la conexión o solicitud a la API: {e}")
            return False

class Landing(TemplateView):
    """
    Vista de la página de aterrizaje para visitantes.
    """
    template_name = "visitors/landing.html"  # Asegúrate de que la ruta coincida con la estructura del proyecto
