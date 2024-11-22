from django.contrib import admin
from .models import Tool, Renta

class ToolAdmin(admin.ModelAdmin):
    """
    Configuración para la administración del modelo Tool en el panel de administración de Django.

    Atributos:
    model (Tool): El modelo asociado a esta clase de administración.
    list_display (list): Campos a mostrar en la lista de herramientas dentro del panel de administración.
    search_fields (list): Campos por los cuales se podrá buscar al realizar consultas en el panel de administración.

    Campos visibles:
    - nombre: El nombre de la herramienta.
    - costo_dia: El costo de la herramienta por día.
    - estado: El estado de la herramienta (disponible o no).
    """  
    model = Tool
    list_display = ["nombre", "costo_dia", "estado"]
    search_fields = ["nombre", "descripcion"]

class RentaAdmin(admin.ModelAdmin):
    """
    Configuración para la administración del modelo Renta en el panel de administración de Django.

    Atributos:
    model (Renta): El modelo asociado a esta clase de administración.
    list_display (list): Campos a mostrar en la lista de rentas dentro del panel de administración.

    Campos visibles:
    - herramienta: La herramienta asociada con la renta.
    """
    model = Renta
    list_display = ["herramienta"]

admin.site.register(Tool, ToolAdmin)
























