# views.py
from django.views.decorators.csrf import csrf_exempt

import requests
import boto3
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
import json
from django.http import JsonResponse
from base64 import b64decode
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

@csrf_exempt
def verify_identity(request):
    if request.method == 'POST':
        # Obtener imagen capturada en base64 y la imagen INE del formulario
        captured_image_data = request.POST.get('captured_image')
        ine_image = request.FILES.get('ine_image')

        # Validar que ambas imágenes estén presentes
        if not (captured_image_data and ine_image):
            print("Error: Una o ambas imágenes están ausentes")
            return JsonResponse({"success": False, "error": "Se requieren ambas imágenes."})

        try:
            # Decodificar la imagen capturada en base64 a binario
            captured_image = base64.b64decode(captured_image_data.split(',')[1])
            print("Imagen capturada decodificada exitosamente.")

            # Preparar cliente de AWS Rekognition
            import boto3
            rekognition_client = boto3.client(
                'rekognition',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )

            # Detectar rostros en la imagen capturada
            print("Enviando solicitud para detectar rostros en la imagen capturada...")
            captured_response = rekognition_client.detect_faces(
                Image={'Bytes': captured_image},
                Attributes=['ALL']
            )
            print("Respuesta de detección (capturada):", captured_response)

            if not captured_response['FaceDetails']:
                print("No se detectó ningún rostro en la imagen capturada.")
                return JsonResponse({"success": False, "error": "No se detectó un rostro en la imagen capturada."})

            # Leer y enviar la imagen INE
            ine_image_data = ine_image.read()
            print("Enviando solicitud para detectar rostros en la imagen INE...")
            ine_response = rekognition_client.detect_faces(
                Image={'Bytes': ine_image_data},
                Attributes=['ALL']
            )
            print("Respuesta de detección (INE):", ine_response)

            if not ine_response['FaceDetails']:
                print("No se detectó ningún rostro en la imagen INE.")
                return JsonResponse({"success": False, "error": "No se detectó un rostro en la imagen INE."})

            # Comparar rostros
            print("Enviando solicitud para comparar rostros...")
            comparison_response = rekognition_client.compare_faces(
                SourceImage={'Bytes': ine_image_data},
                TargetImage={'Bytes': captured_image},
                SimilarityThreshold=90  # Cambia el umbral según tus necesidades
            )
            print("Respuesta de comparación de rostros:", comparison_response)

            # Validar si se encontraron coincidencias con el umbral de similitud
            if not comparison_response['FaceMatches']:
                print("No se encontró coincidencia en los rostros.")
                return JsonResponse({"success": False, "error": "Los rostros no coinciden."})

            # Resultado de coincidencia
            print("Coincidencia de rostros exitosa.")
            return JsonResponse({"success": True})

        except Exception as e:
            print(f"Error en la solicitud a AWS Rekognition: {str(e)}")
            return JsonResponse({"success": False, "error": f"Error en la solicitud a AWS Rekognition: {str(e)}"})

    print("Error: Método no permitido")
    return JsonResponse({"success": False, "error": "Método no permitido."})


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
            email=user_data['email'],  # Asegúrate de que este campo proviene del formulario correctamente
            password=user_data['password1'],
        )
        print("Usuario creado con correo:", user.email)  # Línea de depuración para verificar el correo

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
                correo=user.email,  # Asegúrate de que estamos guardando el correo en el perfil
                ine_image=personal_data['ine_image'],
                direccion=direccion,
                profile_picture=profile_picture
            )
            print("Perfil de Arrendador creado con correo:", user.email)
        else:
            Arrendatario.objects.create(
                usuario=user,
                nombre=personal_data['nombre'],
                apellidos=personal_data['apellidos'],
                telefono=personal_data['telefono'],
                correo=user.email,  # Asegúrate de que estamos guardando el correo en el perfil
                ine_image=personal_data['ine_image'],
                direccion=direccion,
                profile_picture=profile_picture
            )
            print("Perfil de Arrendatario creado con correo:", user.email)

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
    
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from datetime import timedelta
import re
from .models import Arrendador, Arrendatario  # Importa tus modelos correctos

# Función para validar la fortaleza de la contraseña
def validate_password_strength(password):
    errors = []
    if len(password) < 8:
        errors.append("La contraseña debe tener al menos 8 caracteres.")
    if not re.search(r"[A-Z]", password):
        errors.append("La contraseña debe contener al menos una letra mayúscula.")
    if not re.search(r"[a-z]", password):
        errors.append("La contraseña debe contener al menos una letra minúscula.")
    if not re.search(r"\d", password):
        errors.append("La contraseña debe contener al menos un número.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("La contraseña debe contener al menos un carácter especial.")
    
    if errors:
        raise ValidationError(errors)

# Vista para solicitar el restablecimiento de contraseña
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Intenta buscar el usuario en Arrendador o Arrendatario
        try:
            user = Arrendador.objects.get(correo=email)
            user_type = 'Arrendador'
        except Arrendador.DoesNotExist:
            try:
                user = Arrendatario.objects.get(correo=email)
                user_type = 'Arrendatario'
            except Arrendatario.DoesNotExist:
                messages.error(request, 'No se encontró ningún usuario con ese correo.')
                return redirect('password_reset')

        # Generar el código de verificación
        reset_code = get_random_string(6, allowed_chars='0123456789')
        expiration_time = timezone.now() + timedelta(minutes=30)

        # Guardar el código en la sesión en lugar de un modelo (simplificación)
        request.session['reset_email'] = email
        request.session['reset_code'] = reset_code
        request.session['user_type'] = user_type

        # Enviar el código de verificación usando send_mail
        subject = 'Código de restablecimiento de contraseña'
        message = f'Tu código para restablecer la contraseña es: {reset_code}'
        email_from = 'rentfast64@gmail.com'  # Puedes usar DEFAULT_FROM_EMAIL directamente
        recipient_list = [email]

        try:
            send_mail(subject, message, email_from, recipient_list)
            messages.success(request, 'Se envió un código a tu correo, favor de verificarlo.')
            return redirect('verify_reset_code')
        except Exception as e:
            messages.error(request, f'Hubo un problema al enviar el correo: {e}')

    return render(request, 'users/reset_password_combined.html', {'stage': 'reset_request'})

# Vista para verificar el código de restablecimiento
def verify_reset_code(request):
    email = request.session.get('reset_email')
    stored_code = request.session.get('reset_code')

    if request.method == 'POST':
        reset_code = request.POST.get('reset_code')

        if reset_code == stored_code:
            return redirect('set_new_password')
        else:
            messages.error(request, 'Código inválido o expirado.')
            return redirect('verify_reset_code')

    return render(request, 'users/reset_password_combined.html', {'stage': 'verify_code', 'email': email})

# Vista para establecer una nueva contraseña
def set_new_password(request):
    email = request.session.get('reset_email')
    user_type = request.session.get('user_type')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')

        try:
            # Validar la fortaleza de la contraseña
            validate_password_strength(new_password)

            # Buscar y actualizar el usuario
            if user_type == 'Arrendador':
                user = Arrendador.objects.get(correo=email)
            elif user_type == 'Arrendatario':
                user = Arrendatario.objects.get(correo=email)
            else:
                messages.error(request, 'No se encontró ningún usuario. Inténtalo de nuevo.')
                return redirect('password_reset')

            # Cambiar la contraseña del usuario relacionado (en el modelo User)
            user.usuario.set_password(new_password)
            user.usuario.save()

            # Limpiar la sesión
            del request.session['reset_email']
            del request.session['reset_code']
            del request.session['user_type']

            messages.success(request, 'Tu contraseña se ha cambiado correctamente.')
            return redirect('login')  # Ajusta el nombre de la URL de inicio de sesión

        except ValidationError as e:
            # Mostrar cada mensaje de error individualmente
            for error in e.messages:
                messages.error(request, error)

        except (Arrendador.DoesNotExist, Arrendatario.DoesNotExist):
            messages.error(request, 'Error al restablecer la contraseña. Inténtalo de nuevo.')
            return redirect('password_reset')

    return render(request, 'users/set_new_password.html', {'email': email})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserForm, PersonalInfoForm, AddressForm
from .models import Arrendador, Arrendatario, Direccion
from django.urls import reverse

@login_required
def actualizar_datos_view(request):
    # Determina si el usuario es Arrendador o Arrendatario
    try:
        perfil = Arrendador.objects.get(usuario=request.user)
        es_arrendador = True
    except Arrendador.DoesNotExist:
        perfil = Arrendatario.objects.get(usuario=request.user)
        es_arrendador = False

    direccion = perfil.direccion

    # Determina la URL de redirección
    redireccion_url = reverse('arrendador_home') if es_arrendador else reverse('arrendatario_home')

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        personal_form = PersonalInfoForm(request.POST, request.FILES)
        address_form = AddressForm(request.POST, instance=direccion)

        # Remover campos de contraseña y otros no necesarios del formulario de usuario
        user_form.fields.pop('password1', None)
        user_form.fields.pop('password2', None)
        personal_form.fields.pop('role', None)
        personal_form.fields.pop('ine_image', None)

        if user_form.is_valid() and personal_form.is_valid() and address_form.is_valid():
            # Guardar los cambios en el usuario
            user_form.save()

            # Actualizar manualmente los datos personales
            perfil.nombre = personal_form.cleaned_data['nombre']
            perfil.apellidos = personal_form.cleaned_data['apellidos']
            perfil.telefono = personal_form.cleaned_data['telefono']

            # Verifica y actualiza la imagen de perfil solo si se ha proporcionado un nuevo archivo
            if 'profile_picture' in request.FILES:
                perfil.profile_picture = personal_form.cleaned_data.get('profile_picture')

            perfil.save()
            address_form.save()

            messages.success(request, 'Tu información ha sido actualizada con éxito.')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        # Inicializar los formularios con los datos existentes
        user_form = UserForm(instance=request.user)
        personal_form = PersonalInfoForm(initial={
            'nombre': perfil.nombre,
            'apellidos': perfil.apellidos,
            'telefono': perfil.telefono,
            'profile_picture': perfil.profile_picture
        })
        address_form = AddressForm(instance=direccion)

        user_form.fields.pop('password1', None)
        user_form.fields.pop('password2', None)
        personal_form.fields.pop('role', None)
        personal_form.fields.pop('ine_image', None)

    context = {
        'user_form': user_form,
        'personal_form': personal_form,
        'address_form': address_form,
        'es_arrendador': es_arrendador,
        'redireccion_url': redireccion_url
    }
    return render(request, 'users/update_dates.html', context)






