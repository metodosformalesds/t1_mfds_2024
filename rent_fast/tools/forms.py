from django import forms
from .models import Tool

class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = ['nombre', 'descripcion', 'costo_hora', 'costo_dia', 'estado', 'imagenes']
        labels = {
            'nombre': 'Nombre de la Herramienta',
            'descripcion': 'Descripción',
            'costo_hora': 'Costo por Hora',
            'costo_dia': 'Costo por Día',
            'estado': 'Estado de la Herramienta',
            'imagenes': 'Imágenes',
        }
    
    def save(self, arrendador):
        tool = Tool.objects.create(
            arrendador=arrendador,
            nombre=self.cleaned_data["nombre"],
            descripcion=self.cleaned_data["descripcion"],
            costo_hora=self.cleaned_data["costo_hora"],
            costo_dia=self.cleaned_data["costo_dia"],
            estado=self.cleaned_data["estado"],
            imagenes=self.cleaned_data["imagenes"],
        )
        return tool
