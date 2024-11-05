# chat/forms.py
from django import forms
from .models import Mensaje

class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['contenido']
        labels = {'contenido': 'Escribe tu mensaje'}
        widgets = {'contenido': forms.Textarea(attrs={'rows': 3})}
