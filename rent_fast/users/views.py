# views.py
from django.views.decorators.csrf import csrf_exempt

import requests
from django.db.models import Q
import boto3
import qrcode
from urllib.parse import quote  # En lugar de urlquote
from django.http import HttpResponse

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
from .models import Arrendador, Arrendatario, Direccion, Notificacion

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
    """
    Verifica la identidad de un usuario utilizando AWS Rekognition.
    
    Recibe dos imágenes a través de una solicitud POST:
    1. Imagen capturada por el usuario.
    2. Imagen INE (identificación oficial).
    
    Realiza la detección de rostros en ambas imágenes y compara los rostros para verificar si coinciden. Si las imágenes coinciden, devuelve una respuesta positiva. De lo contrario, devuelve un error indicando que no hay coincidencias.

    Args:
        request (HttpRequest): La solicitud que contiene las imágenes capturadas y del INE.

    Returns:
        JsonResponse: Respuesta JSON con el resultado de la comparación de los rostros.
    """
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
        """
        Devuelve la plantilla correspondiente según el paso actual del formulario.
        """
        return [TEMPLATES[self.steps.current]]

    def post(self, *args, **kwargs):
        """
        Sobreescribe el método `post` para agregar validación en el paso de información personal.
        """
        step = self.steps.current
        response = super().post(*args, **kwargs)

        if step == 'personal':
            form = self.get_form(data=self.request.POST, files=self.request.FILES)
            if not form.is_valid():
                messages.error(self.request, "Por favor, verifica los campos del formulario.")
                return self.render_to_response(self.get_context_data(form=form))
            profile_picture = form.cleaned_data.get('profile_picture')
            if not profile_picture:
                messages.error(self.request, "La foto de perfil es obligatoria.")
                return self.render_to_response(self.get_context_data(form=form))

        return response

    def done(self, form_list, **kwargs):
        """
        Método obligatorio que maneja la finalización del asistente.
        """
        user_data = form_list[0].cleaned_data
        personal_data = form_list[1].cleaned_data
        address_data = form_list[2].cleaned_data

        # Crear el usuario
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password1']
        )

        # Crear la dirección
        direccion = Direccion.objects.create(
            calle=address_data['calle'],
            ciudad=address_data['ciudad'],
            estado=address_data['estado'],
            colonia=address_data.get('colonia', ''),
            codigo_postal=address_data['codigo_postal']
        )

        # Crear perfil
        role = personal_data['role']
        profile_picture = personal_data.get('profile_picture')

        if role == 'arrendador':
            Arrendador.objects.create(
                usuario=user,
                nombre=personal_data['nombre'],
                apellidos=personal_data['apellidos'],
                telefono=personal_data['telefono'],
                correo=user.email,
                ine_image=personal_data['ine_image'],
                profile_picture=profile_picture,
                direccion=direccion
            )
        else:
            Arrendatario.objects.create(
                usuario=user,
                nombre=personal_data['nombre'],
                apellidos=personal_data['apellidos'],
                telefono=personal_data['telefono'],
                correo=user.email,
                ine_image=personal_data['ine_image'],
                profile_picture=profile_picture,
                direccion=direccion
            )

        # Mensaje de éxito y redirección
        messages.success(self.request, "Registro completado con éxito.")
        return redirect('login')



    def verify_ine(self, ine_image):
        """
        Verifica el documento INE utilizando la API de IDAnalyzer.
        
        Convierte la imagen INE a Base64 y la envía a la API de IDAnalyzer para su verificación.
        
        Args:
            ine_image (file): Imagen del INE proporcionada por el usuario.

        Returns:
            bool: Retorna True si la verificación fue exitosa, False si hubo un error.
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
    """
    Valida la fortaleza de una contraseña.

    Verifica que la contraseña cumpla con los siguientes requisitos:
    - Al menos 8 caracteres de longitud.
    - Contiene al menos una letra mayúscula.
    - Contiene al menos una letra minúscula.
    - Contiene al menos un número.
    - Contiene al menos un carácter especial.

    Parámetros:
    password (str): La contraseña que se va a validar.

    Excepciones:
    - Lanza `ValidationError` si alguna de las condiciones no se cumple.

    Retorna:
    None: Si la contraseña es válida.
    """
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
    """
    Vista que maneja la solicitud de restablecimiento de contraseña.

    Permite que el usuario ingrese su correo electrónico para solicitar un restablecimiento de contraseña.
    Si el correo pertenece a un **Arrendador** o **Arrendatario**, se genera un código de verificación y se envía por correo.

    Parámetros:
    request (HttpRequest): La solicitud HTTP del usuario.

    Retorna:
    HttpResponse: Redirige a la vista de verificación de código si la solicitud es exitosa, 
                  o renderiza la vista actual con un mensaje de error en caso contrario.
    """
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
    """
    Vista que verifica el código de restablecimiento de contraseña.

    Permite al usuario ingresar el código de verificación enviado por correo.
    Si el código es correcto, se redirige al usuario a la vista para establecer una nueva contraseña.

    Parámetros:
    request (HttpRequest): La solicitud HTTP del usuario.

    Retorna:
    HttpResponse: Redirige a la vista de establecimiento de nueva contraseña si el código es correcto,
                  o muestra un mensaje de error si el código es inválido o ha expirado.
    """
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
    """
    Vista para permitir al usuario establecer una nueva contraseña.

    Valida la fortaleza de la nueva contraseña y actualiza la contraseña en el modelo `User` del
    **Arrendador** o **Arrendatario** correspondiente. Luego, limpia la sesión y redirige al usuario
    a la página de inicio de sesión.

    Parámetros:
    request (HttpRequest): La solicitud HTTP del usuario.

    Retorna:
    HttpResponse: Redirige a la página de inicio de sesión si la contraseña es cambiada correctamente,
                  o muestra los errores de validación si no se cumple con los requisitos de seguridad.
    """
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
    """
    Vista para actualizar los datos de usuario (información personal y dirección) del usuario autenticado.
    Dependiendo del tipo de usuario (Arrendador o Arrendatario), se muestra el formulario adecuado para editar sus datos.
    Se validan y actualizan los datos del formulario y luego se guarda la nueva información.

    Parámetros:
    request (HttpRequest): La solicitud HTTP del usuario.

    Retorna:
    HttpResponse: Redirige a la página de inicio del arrendador o arrendatario según el tipo de usuario,
                  o renderiza la vista con los mensajes correspondientes en caso de errores.
    """ 
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

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UpdateAddressForm
from .models import Arrendador, Arrendatario
from django.urls import reverse

@login_required
def update_address(request):
    """
    Vista para actualizar la dirección del usuario autenticado.
    Determina si el usuario es Arrendador o Arrendatario y permite actualizar los datos de su dirección.

    Parámetros:
    request (HttpRequest): La solicitud HTTP del usuario.

    Retorna:
    HttpResponse: Redirige al usuario después de guardar la nueva dirección o muestra un mensaje de error
                  si el formulario no es válido.
    """
    try:
        # Determinar si el usuario es Arrendador
        perfil = Arrendador.objects.get(usuario=request.user)
        es_arrendador = True
    except Arrendador.DoesNotExist:
        # Si no es Arrendador, verificar si es Arrendatario
        perfil = Arrendatario.objects.get(usuario=request.user)
        es_arrendador = False

    # Obtener la dirección asociada al perfil
    direccion = perfil.direccion

    # Determinar la URL de redirección según el rol del usuario
    redireccion_url = reverse('arrendador_home') if es_arrendador else reverse('arrendatario_home')

    if request.method == 'POST':
        # Procesar el formulario con los datos enviados
        form = UpdateAddressForm(request.POST, instance=direccion)
        if form.is_valid():
            # Guardar los cambios en la dirección
            form.save()
            messages.success(request, "¡Tu dirección ha sido actualizada correctamente!")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        # Mostrar el formulario con los datos existentes
        form = UpdateAddressForm(instance=direccion)

    # Contexto para renderizar la plantilla
    context = {
        'form': form,
        'redireccion_url': redireccion_url,
    }
    return render(request, 'users/update_address.html', context)

@login_required
def ver_notificaciones(request):
    """
    Vista para mostrar las notificaciones del usuario autenticado.
    Incluye filtros por tipo y estado.
    """
    usuario = request.user

    # Obtener todas las notificaciones del usuario actual
    notificaciones = Notificacion.objects.filter(usuario=usuario).order_by('-creado')

    # Aplicar filtros basados en los parámetros GET
    tipo = request.GET.get('tipo')  # 'herramienta', 'chat', 'general'
    estado = request.GET.get('estado')  # 'leido', 'no_leido'

    if tipo == 'herramienta':
        notificaciones = notificaciones.filter(Q(mensaje__icontains='Tu') | Q(mensaje__icontains='Has'))
    elif tipo == 'chat':
        # Filtrar por notificaciones relacionadas con "chat" basadas en el mensaje
        notificaciones = notificaciones.filter(mensaje__icontains='chat')

    if estado == 'leido':
        notificaciones = notificaciones.filter(leido=True)
    elif estado == 'no_leido':
        notificaciones = notificaciones.filter(leido=False)

    # Marcar todas las notificaciones como leídas
    notificaciones.update(leido=True)

    # Determinar la redirección según el rol del usuario
    if hasattr(usuario, 'arrendador'):
        url_redireccion = 'arrendador_home'
    elif hasattr(usuario, 'arrendatario'):
        url_redireccion = 'arrendatario_home'
    else:
        url_redireccion = 'home'

    context = {
        'notificaciones': notificaciones,
        'url_redireccion': reverse(url_redireccion),
    }
    return render(request, 'users/notificaciones.html', context)


import uuid
from django.core.cache import cache

def generate_qr_for_identity(request):
    """
    Genera un código QR temporal para la verificación de identidad del usuario.
    El código contiene una URL para cargar la imagen de identidad del usuario, que incluye un ID temporal.

    Parámetros:
    request (HttpRequest): La solicitud HTTP del usuario.

    Retorna:
    HttpResponse: La imagen PNG del código QR generado.
    """
    temp_id = uuid.uuid4()  # Genera un UUID temporal
    url = request.build_absolute_uri(reverse('upload_identity_image')) + f"?temp_id={temp_id}"
    qr = qrcode.make(url)
    response = HttpResponse(content_type="image/png")
    qr.save(response, "PNG")

    # Guarda el ID temporal en cache para verificación
    cache.set(f'verification_{temp_id}', False, timeout=3600)  # Valido por 1 hora
    return response

@csrf_exempt
def upload_identity_image(request):
    """
    Permite al usuario subir una imagen de identidad (INE) para la verificación.
    Utiliza AWS Rekognition para comparar las imágenes subidas con la imagen capturada desde el dispositivo del usuario.

    Parámetros:
    request (HttpRequest): La solicitud HTTP que contiene la imagen capturada y la imagen del INE.

    Retorna:
    JsonResponse: La respuesta que indica si la verificación fue exitosa o fallida.
    """
    if request.method == 'GET':
        # Renderiza la página para capturar la foto desde el dispositivo
        return render(request, 'users/mobile_verification.html')

    elif request.method == 'POST':
        captured_image_data = request.POST.get('captured_image')
        ine_image_data = request.FILES.get('ine_image')  # Permite que el usuario suba su INE

        if not captured_image_data or not ine_image_data:
            return JsonResponse({"success": False, "error": "Se requieren ambas imágenes para la verificación."})

        try:
            # Decodificar la imagen capturada y la imagen del INE en binario
            captured_image = base64.b64decode(captured_image_data.split(',')[1])
            ine_image = ine_image_data.read()

            rekognition_client = boto3.client(
                'rekognition',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )

            # Detectar rostros en ambas imágenes
            captured_response = rekognition_client.detect_faces(Image={'Bytes': captured_image}, Attributes=['ALL'])
            ine_response = rekognition_client.detect_faces(Image={'Bytes': ine_image}, Attributes=['ALL'])

            if not captured_response['FaceDetails'] or not ine_response['FaceDetails']:
                return JsonResponse({"success": False, "error": "No se detectó un rostro en una de las imágenes."})

            # Comparar ambas imágenes
            comparison_response = rekognition_client.compare_faces(
                SourceImage={'Bytes': ine_image},
                TargetImage={'Bytes': captured_image},
                SimilarityThreshold=90
            )

            if comparison_response['FaceMatches']:
                # Guardar el estado de verificación en la sesión
                request.session['identity_verified'] = True
                return JsonResponse({"success": True, "message": "La verificación fue exitosa."})
            else:
                return JsonResponse({"success": False, "error": "Las imágenes no coinciden."})

        except Exception as e:
            return JsonResponse({"success": False, "error": f"Error en la verificación: {str(e)}"})

    return JsonResponse({"success": False, "error": "Método no permitido."})

from django.shortcuts import render
from tools.models import Tool

def contratos_view(request):
    """
    Vista para mostrar los contratos disponibles o relacionados con el usuario.
    Este ejemplo asume que se está mostrando una herramienta asociada a un contrato.

    Parámetros:
    request (HttpRequest): La solicitud HTTP del usuario.

    Retorna:
    HttpResponse: Renderiza la vista de los contratos asociados.
    """
    # Supongamos que quieres pasar una herramienta específica
    tool = Tool.objects.first()  # O la forma en que obtienes la herramienta
    return render(request, 'users/contratos.html', {'tool': tool})


from django.http import JsonResponse
from django.conf import settings
import requests

def buscar_codigo_postal_calle(request):
    """
    Busca la ciudad y el estado a partir de un código postal y una calle, utilizando la API de Geocoding de Google Maps.

    Parámetros:
    request (HttpRequest): La solicitud HTTP que contiene el código postal y la calle a buscar.

    Retorna:
    JsonResponse: Contiene los resultados de la búsqueda de la ciudad y el estado si la API devuelve éxito,
                  o un error si no se proporcionan los parámetros requeridos o si la API falla.
    """
    codigo_postal = request.GET.get("codigo_postal")
    calle = request.GET.get("calle")

    if not codigo_postal or not calle:
        return JsonResponse({"error": "El código postal y la calle son requeridos."}, status=400)

    resultado = {"ciudad": "", "estado": ""}

    # Construcción de la URL para la API de Geocoding
    api_key = settings.GOOGLE_MAPS_API_KEY
    maps_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={calle},{codigo_postal}&key={api_key}"

    try:
        response = requests.get(maps_url)
        data = response.json()

        if data.get("status") == "OK":
            address_components = data["results"][0]["address_components"]

            # Extraer ciudad y estado
            resultado["ciudad"] = next((comp["long_name"] for comp in address_components if "locality" in comp["types"]), "")
            resultado["estado"] = next((comp["long_name"] for comp in address_components if "administrative_area_level_1" in comp["types"]), "")
        else:
            return JsonResponse({"error": "No se encontraron resultados para la dirección especificada."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Error al conectar con Google Maps: {str(e)}"}, status=500)

    return JsonResponse(resultado)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Arrendador, Arrendatario

@login_required
def gestionar_usuarios(request):
    """
    Vista para listar y gestionar los usuarios registrados (Arrendadores y Arrendatarios).

    Parámetros:
    request (HttpRequest): La solicitud HTTP del usuario.

    Retorna:
    HttpResponse: Renderiza la vista para gestionar usuarios, mostrando tanto a los arrendadores como arrendatarios.
    """
    arrendadores = Arrendador.objects.all()
    arrendatarios = Arrendatario.objects.all()

    context = {
        'arrendadores': arrendadores,
        'arrendatarios': arrendatarios,
    }
    return render(request, 'users/gestionar_usuarios.html', context)

@login_required
def eliminar_usuario(request, usuario_id, tipo_usuario):
    """
    Vista para eliminar un usuario (Arrendador o Arrendatario) del sistema.

    Parámetros:
    request (HttpRequest): La solicitud HTTP del usuario.
    usuario_id (int): El ID del usuario a eliminar.
    tipo_usuario (str): El tipo de usuario a eliminar ('arrendador' o 'arrendatario').

    Retorna:
    HttpResponse: Redirige al listado de usuarios después de eliminar el usuario seleccionado, o muestra un mensaje de error si el tipo es incorrecto.
    """
    """
    Vista para eliminar un usuario (Arrendador o Arrendatario).
    """
    if tipo_usuario == 'arrendador':
        usuario = get_object_or_404(Arrendador, id=usuario_id)
    elif tipo_usuario == 'arrendatario':
        usuario = get_object_or_404(Arrendatario, id=usuario_id)
    else:
        messages.error(request, 'Tipo de usuario no válido.')
        return redirect('gestionar_usuarios')

    # Almacenar el nombre del usuario antes de eliminarlo
    nombre_usuario = f'{usuario.nombre} {usuario.apellidos}'

    usuario.usuario.delete()  # Eliminar al usuario relacionado
    usuario.delete()  # Eliminar el perfil

    # Agregar un mensaje de éxito
    messages.success(request, f'El usuario {nombre_usuario} ha sido eliminado correctamente.')

    # Redirigir a la página de gestión de usuarios
    return redirect('gestionar_usuarios')


# views.py
from django.contrib import messages
from .forms import PersonalInfoForm, UpdateAddressForm
from .models import Arrendador, Arrendatario
from django.shortcuts import get_object_or_404, redirect, render
from .forms import EditarArrendadorForm, EditarArrendatarioForm
from .models import Arrendador, Arrendatario
@login_required
def editar_usuario(request, usuario_id, tipo_usuario):
    """
    Vista para editar la información de un usuario (Arrendador o Arrendatario).

    Parámetros:
    request (HttpRequest): La solicitud HTTP del usuario.
    usuario_id (int): El ID del usuario a editar.
    tipo_usuario (str): El tipo de usuario a editar ('arrendador' o 'arrendatario').

    Retorna:
    HttpResponse: Renderiza el formulario de edición para el usuario o redirige después de guardar los cambios.
    """
    if tipo_usuario == "arrendador":
        usuario = get_object_or_404(Arrendador, id=usuario_id)
        form_class = EditarArrendadorForm
    elif tipo_usuario == "arrendatario":
        usuario = get_object_or_404(Arrendatario, id=usuario_id)
        form_class = EditarArrendatarioForm
    else:
        return redirect('gestionar_usuarios')  # Si el tipo no coincide, regresa a la gestión de usuarios.

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()  # Guarda los cambios en la base de datos.
            return redirect('gestionar_usuarios')  # Redirige después de guardar.
    else:
        form = form_class(instance=usuario)  # Carga los datos actuales del usuario.

    return render(request, 'users/editar_usuario.html', {'form': form, 'tipo_usuario': tipo_usuario})
from .forms import RetiroForm
from .models import Balance, Retiro

@login_required
def balance_view(request):
    """
    Vista para mostrar y gestionar el balance y los retiros de un arrendador.

    Parámetros:
    request (HttpRequest): La solicitud HTTP del usuario.

    Retorna:
    HttpResponse: Renderiza la vista del balance del arrendador y permite hacer retiros si el saldo es suficiente.
    """
    arrendador = request.user.arrendador
    balance, created = Balance.objects.get_or_create(arrendador=arrendador)
    retiros = Retiro.objects.filter(arrendador=arrendador).order_by('-fecha')

    if request.method == 'POST':
        form = RetiroForm(request.POST)
        if form.is_valid():
            monto = form.cleaned_data['monto']
            if monto <= balance.saldo_total:
                Retiro.objects.create(arrendador=arrendador, monto=monto)
                balance.saldo_total -= monto
                balance.save()
                messages.success(request, f"Se ha solicitado un retiro de ${monto:.2f}.")
                return redirect('balance_view')
            else:
                messages.error(request, "No tienes saldo suficiente para este retiro.")
    else:
        form = RetiroForm()

    return render(request, 'users/balance.html', {
        'balance': balance,
        'retiros': retiros,
        'form': form,
    })