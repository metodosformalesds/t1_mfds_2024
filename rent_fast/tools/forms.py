from django import forms
from .models import Tool, Carrito, Categoria
from rentas.models import Renta

class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = ['nombre', 'descripcion', 'costo_dia', 'imagenes', 'categoria']  # Incluimos el campo `categoria`
        labels = {
            'nombre': 'Nombre de la Herramienta',
            'descripcion': 'Descripción',
            'costo_dia': 'Costo por Día',
            'imagenes': 'Imágenes',
            'categoria': 'Categoría'
        }

    def save(self, arrendador, *args, **kwargs):
        tool = super().save(commit=False)
        tool.arrendador = arrendador
        tool.estado = "Pendiente"  # Asignamos el estado por defecto a "Pendiente"
        tool.save()
        return tool

class RentaForm(forms.ModelForm):
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
    class Meta:
        model = Carrito
        fields = ['fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, arrendatario, herramienta, commit=True):
        carrito_item = super().save(commit=False)
        carrito_item.arrendatario = arrendatario
        carrito_item.herramienta = herramienta
        dias_renta = (self.cleaned_data["fecha_fin"] - self.cleaned_data["fecha_inicio"]).days + 1
        carrito_item.costo_total = dias_renta * herramienta.costo_dia
        if commit:
            carrito_item.save()
        return carrito_item