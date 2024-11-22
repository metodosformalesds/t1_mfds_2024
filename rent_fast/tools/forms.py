from django import forms
from .models import Tool, Carrito, Categoria
from rentas.models import Renta

from django.core.exceptions import ValidationError

class ToolForm(forms.ModelForm):
    """
    Formulario para crear y editar herramientas.

    Este formulario permite ingresar información relacionada con las herramientas, 
    como el nombre, la descripción, el costo por día, las imágenes y la categoría. 
    También valida que al menos se haya subido una imagen.

    Atributos:
    - nombre (str): Nombre de la herramienta.
    - descripcion (str): Descripción de la herramienta.
    - costo_dia (float): Costo de la herramienta por día.
    - imagenes (ImageField): Imágenes asociadas a la herramienta.
    - categoria (ForeignKey): Categoría a la que pertenece la herramienta.

    Métodos:
    - clean(): Valida que se haya subido al menos una imagen para la herramienta.
    - save(arrendador): Guarda la herramienta asignando un arrendador, estado y disponibilidad.
    """
    class Meta:
        model = Tool
        fields = ['nombre', 'descripcion', 'costo_dia', 'imagenes', 'categoria']
        labels = {
            'nombre': 'Nombre de la Herramienta',
            'descripcion': 'Descripción',
            'costo_dia': 'Costo por Día',
            'imagenes': 'Imágenes',
            'categoria': 'Categoría',
        }

    def clean(self):
        cleaned_data = super().clean()
        imagenes = cleaned_data.get('imagenes')
        if not imagenes:
            raise ValidationError("Debes subir al menos una imagen para la herramienta.")
        return cleaned_data

    def save(self, arrendador, *args, **kwargs):
        """
        Guarda la herramienta asignando un arrendador, estado y disponibilidad.

        Atributos:
        - arrendador (Arrendador): El arrendador al que se le asigna la herramienta.

        Devuelve:
        - tool (Tool): La herramienta guardada con los campos adicionales asignados.
        """
        tool = super().save(commit=False)
        tool.arrendador = arrendador
        tool.estado = "Pendiente"  # Asignar el estado por defecto
        tool.disponibilidad = True  # Asignar disponibilidad por defecto
        tool.save()
        return tool


class RentaForm(forms.ModelForm):
    """
    Formulario para crear y editar rentas de herramientas.

    Este formulario permite ingresar las fechas de inicio y fin de una renta, 
    y valida que la fecha de inicio no sea posterior a la fecha de fin.

    Atributos:
    - fecha_inicio (DateField): Fecha de inicio de la renta.
    - fecha_fin (DateField): Fecha de finalización de la renta.

    Métodos:
    - clean(): Valida que la fecha de inicio no sea posterior a la fecha de fin.
    """
    class Meta:
        model = Renta
        fields = ['fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise forms.ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")
        return cleaned_data

class CarritoForm(forms.ModelForm):
    """
    Formulario para crear y editar los elementos del carrito de renta.

    Este formulario permite ingresar las fechas de inicio y fin de la renta de una herramienta 
    y calcular el costo total de la renta basándose en las fechas y el costo diario de la herramienta.

    Atributos:
    - fecha_inicio (DateField): Fecha de inicio de la renta.
    - fecha_fin (DateField): Fecha de finalización de la renta.
    - herramienta (ForeignKey): Herramienta que se está agregando al carrito.
    - arrendatario (ForeignKey): El arrendatario que está realizando la renta.

    Métodos:
    - save(arrendatario, herramienta): Guarda el elemento en el carrito con los datos proporcionados.
    """
    class Meta:
        model = Carrito
        fields = ['fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, arrendatario, herramienta, commit=True):
        """
        Guarda el carrito de renta calculando el costo total.

        Atributos:
        - arrendatario (Arrendatario): El arrendatario que está agregando la herramienta al carrito.
        - herramienta (Tool): La herramienta que se agrega al carrito.

        Devuelve:
        - carrito_item (Carrito): El elemento del carrito con la herramienta y el arrendatario asignados.
        """
        carrito_item = super().save(commit=False)
        carrito_item.arrendatario = arrendatario
        carrito_item.herramienta = herramienta
        dias_renta = (self.cleaned_data["fecha_fin"] - self.cleaned_data["fecha_inicio"]).days + 1
        carrito_item.costo_total = dias_renta * herramienta.costo_dia
        if commit:
            carrito_item.save()
        return carrito_item
    
from django import forms
from .models import Tool

class RechazarToolForm(forms.ModelForm):
    """
    Formulario para rechazar una herramienta.

    Este formulario permite a un arrendador escribir un mensaje de rechazo para una herramienta 
    que ha sido rechazada, indicando el motivo del rechazo.

    Atributos:
    - mensaje_rechazo (TextField): Motivo del rechazo de la herramienta.

    Métodos:
    - No tiene métodos adicionales, sólo es un formulario para capturar el motivo del rechazo.
    """  
    class Meta:
        model = Tool
        fields = ['mensaje_rechazo']
        widgets = {
            'mensaje_rechazo': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe el motivo del rechazo...'}),
        }

    