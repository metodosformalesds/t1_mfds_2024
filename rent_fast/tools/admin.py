from django.contrib import admin
from .models import Tool

class ToolAdmin(admin.ModelAdmin):
    model = Tool
    list_display = ["nombre", "costo_hora", "costo_dia", "estado"]
    search_fields = ["nombre", "descripcion"]

admin.site.register(Tool, ToolAdmin)
