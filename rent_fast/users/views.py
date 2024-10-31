# views.py

import requests
import base64
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib import messages  
from django.shortcuts import redirect, render
from formtools.wizard.views import SessionWizardView
from django.conf import settings
from django.views.generic import TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import UserForm, PersonalInfoForm, AddressForm
from .models import Arrendador, Arrendatario, Direccion

# Configura el almacenamiento de archivos temporales
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
    form_list = FORMS
    template_name = 'users/register_wizard.html'
    file_storage = file_storage

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def post(self, *args, **kwargs):
        print("Paso actual del asistente:", self.steps.current)  # Debug del paso actual

        # Llamar a la lógica de post de `SessionWizardView`
        response = super().post(*args, **kwargs)

        # Si estamos en el paso 'personal', realizar la verificación de INE
        if self.steps.current == 'personal':
            form = self.get_form(data=self.request.POST, files=self.request.FILES)
            if form.is_valid():
                ine_image = form.cleaned_data.get('ine_image')
                
                # Realizar verificación de INE solo si se ha proporcionado la imagen
                if ine_image:
                    ine_verification_status = self.verify_ine(ine_image)
                    if not ine_verification_status:
                        messages.error(self.request, "La verificación del documento INE falló. Inténtalo nuevamente.")
                        print("Error en verificación de INE.")
                        return self.render_to_response(self.get_context_data(form=form))
                    else:
                        messages.success(self.request, "¡El documento INE fue verificado con éxito!")
                        print("INE verificado correctamente.")

                # Si existe una foto de perfil, guardarla en `extra_data`
                profile_picture = form.cleaned_data.get('profile_picture')
                if profile_picture:
                    self.storage.extra_data['profile_picture'] = profile_picture

        return response

    def done(self, form_list, **kwargs):
        print("Entrando en el método done()")  # Confirmar que hemos llegado a done()

        # Obtener los datos de cada formulario en `form_list`
        user_data = form_list[0].cleaned_data
        personal_data = form_list[1].cleaned_data
        address_data = form_list[2].cleaned_data

        # Crear el usuario
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password1'],
        )
        print("Usuario creado:", user.username)

        # Crear la dirección
        direccion = Direccion.objects.create(
            calle=address_data['calle'],
            ciudad=address_data['ciudad'],
            estado=address_data['estado'],
            codigo_postal=address_data['codigo_postal'],
        )
        print("Dirección creada:", direccion)

        # Crear el perfil (Arrendador o Arrendatario)
        profile_picture = self.storage.extra_data.get('profile_picture')
        role = personal_data['role']
        
        if role == 'arrendador':
            Arrendador.objects.create(
                usuario=user,
                nombre=personal_data['nombre'],
                apellidos=personal_data['apellidos'],
                telefono=personal_data['telefono'],
                ine_image=personal_data['ine_image'],
                direccion=direccion,
                profile_picture=profile_picture
            )
            print("Perfil de Arrendador creado.")
        else:
            Arrendatario.objects.create(
                usuario=user,
                nombre=personal_data['nombre'],
                apellidos=personal_data['apellidos'],
                telefono=personal_data['telefono'],
                ine_image=personal_data['ine_image'],
                direccion=direccion,
                profile_picture=profile_picture
            )
            print("Perfil de Arrendatario creado.")

        messages.success(self.request, "Registro completado con éxito.")
        print("Registro completado. Redirigiendo al login.")
        return redirect('login')

    def verify_ine(self, ine_image):
        """
        Verifica el documento INE utilizando la API de IDAnalyzer.
        """
        api_key = settings.IDANALYZER_API_KEY  
        api_url = 'https://api2.idanalyzer.com/quickscan'
        
        # Convertir a Base64
        ine_image_base64 = base64.b64encode(ine_image.read()).decode('utf-8')
        data = {
            'document': ine_image_base64,
            'ocr_extraction': 'true',
        }
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'X-API-KEY': api_key
        }

        try:
            response = requests.post(api_url, json=data, headers=headers)
            print("Respuesta de la API de verificación de INE:", response.text)

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

class RegisterAddres(LoginRequiredMixin, View):
    """
    Vista para agregar la dirección del usuario autenticado.
    """
    template_name = "users/register_address.html"

    def get(self, request):
        # Muestra el formulario vacío de dirección
        form = AddressForm()
        return render(request, self.template_name, {'form': form})

def post(self, *args, **kwargs):
        print("Paso actual:", self.steps.current)  # Imprime el paso actual del asistente
        
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
                
                profile_picture = form.cleaned_data.get('profile_picture')
                if profile_picture:
                    self.storage.extra_data['profile_picture'] = profile_picture

                print("INE verificado, avanzando al siguiente paso.")
                return self.render_next_step(form)
            else:
                print("Formulario 'personal' no válido.")
        
        return super().post(*args, **kwargs)

class TerminosCondiciones(TemplateView):
    """
    Vista para mostrar la página de Términos y Condiciones.
    """
    template_name = "users/terms_conditions.html"

class RegisterPersonal(View):
    """
    Vista para manejar el formulario de información personal y conservar datos al regresar.
    """
    template_name = "users/register_personal.html"

    def get(self, request):
        # Obtiene los datos del formulario almacenados en la sesión, si existen
        form_data = request.session.get('form_data', {})
        return render(request, self.template_name, {'form_data': form_data})

    def post(self, request):
        # Guarda los datos del formulario en la sesión
        form_data = request.POST.dict()
        request.session['form_data'] = form_data
        return render(request, self.template_name, {'form_data': form_data})
