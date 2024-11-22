from django.contrib import admin
from .models import Renta

from .models import Chat, Mensaje

class MensajeInline(admin.TabularInline):
    """
    Esta clase permite la inclusión de mensajes en el formulario de edición del chat.
    Los mensajes se gestionan como objetos relacionados (inline) dentro del modelo de Chat.
    
    Atributos:
    - model: El modelo relacionado, en este caso Mensaje, que será mostrado en la vista de administración.
    - extra: Número de instancias vacías (extra) de Mensaje que se agregarán por defecto al formulario de edición.
    """
    model = Mensaje
    extra = 1  # Número de mensajes adicionales en el formulario de edición

class ChatAdmin(admin.ModelAdmin):
    """
    Esta clase personaliza la vista de administración del modelo Chat.
    
    Atributos:
    - list_display: Define los campos que se mostrarán en la lista de chats en la vista de administración.
    - search_fields: Permite buscar por los campos especificados en la vista de administración.
    - inlines: Permite incluir el modelo Mensaje como un formulario en línea dentro de la administración de Chat.
    """
    list_display = ('arrendador', 'arrendatario', 'herramienta', 'creado')
    search_fields = ('arrendador__nombre', 'arrendatario__nombre', 'herramienta__nombre')
    inlines = [MensajeInline]  # Incluye los mensajes relacionados en el admin de Chat

class MensajeAdmin(admin.ModelAdmin):
    """
    Esta clase personaliza la vista de administración del modelo Mensaje.
    
    Atributos:
    - list_display: Define los campos que se mostrarán en la lista de mensajes en la vista de administración.
    - search_fields: Permite buscar por el nombre de usuario del remitente y por el contenido del mensaje.
    - list_filter: Permite filtrar los mensajes por la fecha de envío.
    """
    list_display = ('chat', 'remitente', 'contenido', 'enviado')
    search_fields = ('remitente__username', 'contenido')
    list_filter = ('enviado',)

admin.site.register(Chat, ChatAdmin)
admin.site.register(Mensaje, MensajeAdmin)

class RentaAdmin(admin.ModelAdmin):
    """
    Esta clase personaliza la vista de administración del modelo Renta.
    
    Atributos:
    - model: El modelo que será registrado en la administración de Django.
    - list_display: Define los campos que se mostrarán en la lista de rentas en la vista de administración.
    """
    model = Renta
    list_display = ["herramienta"]

admin.site.register(Renta, RentaAdmin)
