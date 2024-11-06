from django.contrib import admin
from .models import Renta

from .models import Chat, Mensaje

class MensajeInline(admin.TabularInline):
    model = Mensaje
    extra = 1  # Número de mensajes adicionales en el formulario de edición

class ChatAdmin(admin.ModelAdmin):
    list_display = ('arrendador', 'arrendatario', 'herramienta', 'creado')
    search_fields = ('arrendador__nombre', 'arrendatario__nombre', 'herramienta__nombre')
    inlines = [MensajeInline]  # Incluye los mensajes relacionados en el admin de Chat

class MensajeAdmin(admin.ModelAdmin):
    list_display = ('chat', 'remitente', 'contenido', 'enviado')
    search_fields = ('remitente__username', 'contenido')
    list_filter = ('enviado',)

admin.site.register(Chat, ChatAdmin)
admin.site.register(Mensaje, MensajeAdmin)

class RentaAdmin(admin.ModelAdmin):
    model = Renta
    list_display = ["herramienta"]

admin.site.register(Renta, RentaAdmin)
