# chat/forms.py
from django import forms
from .models import Mensaje
from .models import Pregunta, Respuesta

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['pregunta_texto']
        labels = {'pregunta_texto': 'Tu pregunta'}

class RespuestaForm(forms.ModelForm):
    class Meta:
        model = Respuesta
        fields = ['respuesta_texto']
        labels = {'respuesta_texto': 'Responder'}

class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['contenido']
        labels = {'contenido': 'Escribe tu mensaje'}
        widgets = {'contenido': forms.Textarea(attrs={'rows': 3})}
        
# rentas/forms.py

from django import forms
from .models import Resena

class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['comentario', 'calificacion']
        widgets = {
            'comentario': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Escribe tu comentario aqu ...'}),
            'calificacion': forms.Select(attrs={'class': 'form-select'}),
        }
