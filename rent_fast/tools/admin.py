from django.contrib import admin
from .models import Tool, Renta

class ToolAdmin(admin.ModelAdmin):
    model = Tool
    list_display = ["nombre", "costo_hora", "costo_dia", "estado"]
    search_fields = ["nombre", "descripcion"]

class RentaAdmin(admin.ModelAdmin):
    model = Renta
    list_display = ["herramienta"]

admin.site.register(Tool, ToolAdmin)
























