# chat/forms.py
from django import forms
from .models import Mensaje
from .models import Pregunta, Respuesta, Resena

class PreguntaForm(forms.ModelForm):
    """
    Formulario para crear una nueva pregunta.

    Este formulario permite a los usuarios enviar una pregunta relacionada con un tema específico.
    El único campo requerido es `pregunta_texto`.

    Meta:
    - model: `Pregunta`
    - fields: `['pregunta_texto']`: Define que el formulario solo tiene el campo `pregunta_texto`.
    - labels: Proporciona una etiqueta personalizada para el campo `pregunta_texto`.
    Juan Flores
    """
    class Meta:
        model = Pregunta
        fields = ['pregunta_texto']
        labels = {'pregunta_texto': 'Tu pregunta'}

class RespuestaForm(forms.ModelForm):
    """
    Formulario para crear una respuesta a una pregunta existente.

    Este formulario permite a los usuarios enviar una respuesta a una pregunta publicada.
    El único campo requerido es `respuesta_texto`.

    Meta:
    - model: `Respuesta`
    - fields: `['respuesta_texto']`: Define que el formulario solo tiene el campo `respuesta_texto`.
    - labels: Proporciona una etiqueta personalizada para el campo `respuesta_texto`.
    Manuel villarreal
    """
    class Meta:
        model = Respuesta
        fields = ['respuesta_texto']
        labels = {'respuesta_texto': 'Responder'}

class MensajeForm(forms.ModelForm):
    """
    Formulario para enviar un nuevo mensaje en el chat.

    Este formulario permite a los usuarios enviar un mensaje dentro de un chat. El campo `contenido`
    es donde se introduce el texto del mensaje, y se renderiza como un área de texto con 3 filas.

    Meta:
    - model: `Mensaje`
    - fields: `['contenido']`: Define que el formulario solo tiene el campo `contenido` para el mensaje.
    - labels: Proporciona una etiqueta personalizada para el campo `contenido`.
    - widgets: Especifica que el campo `contenido` se debe renderizar como un área de texto con 3 filas.
    DANIEL ESQUEDA
    """
    class Meta:
        model = Mensaje
        fields = ['contenido']
        labels = {'contenido': 'Escribe tu mensaje'}
        widgets = {'contenido': forms.Textarea(attrs={'rows': 3})}
        
# rentas/forms.py

from django import forms
from .models import Resena

class ResenaForm(forms.ModelForm):
    """
    Juan Carlos & Manuel Villarreal & Daniel Esqueda
    Formulario para crear una nueva reseña de una herramienta arrendada.

    Este formulario permite a los usuarios dejar una reseña sobre la herramienta que han arrendado.
    El formulario tiene dos campos: `comentario` y `calificacion`.

    Meta:
    - model: `Resena`
    - fields: `['comentario', 'calificacion']`: Define que el formulario tiene los campos `comentario` y `calificacion`.
    - widgets: Define que el campo `comentario` debe ser un área de texto y `calificacion` debe ser un selector de opciones.
    - labels: Proporciona etiquetas personalizadas para los campos `comentario` y `calificacion`.
    """
    class Meta:
        model = Resena
        fields = ['comentario', 'calificacion']
        widgets = {
            'comentario': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Escribe tu comentario aquí...'}),
            'calificacion': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'comentario': 'Comentario',
            'calificacion': 'Calificación'
        }