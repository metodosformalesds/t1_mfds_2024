from django.contrib import admin
from django.contrib.auth.models import User
from .models import Arrendador, Arrendatario, Direccion

# Muestra la información de la Dirección en el Admin
class DireccionAdmin(admin.ModelAdmin):
    """
Juan Carlos & Manuel Villarreal & Daniel Esqueda
Se trabajo en conjunto
"""

    """
    Configuración del panel de administración para el modelo Direccion.

    Esta clase personaliza la forma en que las direcciones se muestran en el panel de administración de Django,
    permitiendo la búsqueda y filtrado por ciudad, estado y código postal.

    Atributos:
    - list_display: Define los campos que se mostrarán en la lista de direcciones.
    - search_fields: Especifica los campos que se pueden buscar (ciudad, estado, código postal).
    """

    list_display = ('calle', 'ciudad', 'estado', 'codigo_postal')
    search_fields = ('ciudad', 'estado', 'codigo_postal')

# Muestra la información de Arrendador con el usuario relacionado
class ArrendadorAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Arrendador.

    Esta clase personaliza la visualización y administración de los arrendadores en el panel de administración de Django.
    Permite marcar arrendadores como verificados, eliminar arrendadores junto con sus usuarios, y filtrarlos por ciudad.

    Atributos:
    - list_display: Define los campos que se mostrarán para cada arrendador.
    - search_fields: Especifica los campos por los cuales se puede buscar un arrendador (nombre, apellidos, correo).
    - list_filter: Permite filtrar los arrendadores por verificación y ciudad.
    - actions: Define acciones personalizadas para los arrendadores.
    
    Métodos:
    - usuario: Muestra el nombre de usuario asociado a cada arrendador.
    - marcar_como_verificado: Acción personalizada para marcar varios arrendadores como verificados.
    - eliminar_usuarios_seleccionados: Acción personalizada para eliminar arrendadores seleccionados y sus usuarios relacionados.
    """
    list_display = ('nombre', 'apellidos', 'correo', 'telefono', 'direccion', 'is_verificado')
    search_fields = ('nombre', 'apellidos', 'correo')
    list_filter = ('is_verificado', 'direccion__ciudad')
    actions = ['marcar_como_verificado', 'eliminar_usuarios_seleccionados']
    
    # Para mostrar el nombre de usuario relacionado
    def usuario(self, obj):
        """
        Muestra el nombre de usuario relacionado al arrendador.

        Parámetros:
        - obj: El objeto de arrendador para el que se quiere obtener el nombre de usuario.

        Devuelve:
        - El nombre de usuario del arrendador.
        """  
        return obj.usuario.username

    # Acción para marcar como verificado
    def marcar_como_verificado(self, request, queryset):
        """
        Marca como verificados los arrendadores seleccionados.

        Esta acción personaliza la administración de arrendadores, marcando a los arrendadores seleccionados
        como verificados y mostrando un mensaje de éxito.

        Parámetros:
        - request: La solicitud HTTP que contiene los datos de los arrendadores seleccionados.
        - queryset: El conjunto de arrendadores seleccionados.

        Devuelve:
        - Un mensaje informando al administrador la cantidad de arrendadores verificados.
        """
        queryset.update(is_verificado=True)
        self.message_user(request, f"{queryset.count()} arrendadores marcados como verificados.")
    marcar_como_verificado.short_description = "Marcar como verificado"

    # Acción personalizada para eliminar usuarios seleccionados
    def eliminar_usuarios_seleccionados(self, request, queryset):
        """
        Elimina los arrendadores seleccionados junto con sus usuarios relacionados.

        Esta acción personalizada elimina a los arrendadores seleccionados de la base de datos,
        así como sus usuarios asociados, proporcionando un mensaje de éxito al administrador.

        Parámetros:
        - request: La solicitud HTTP con los arrendadores seleccionados.
        - queryset: El conjunto de arrendadores seleccionados.

        Devuelve:
        - Un mensaje informando al administrador la cantidad de arrendadores eliminados.
        """
        for arrendador in queryset:
            usuario = arrendador.usuario
            arrendador.delete()
            usuario.delete()
        self.message_user(request, f"{queryset.count()} arrendadores eliminados junto con sus usuarios relacionados.")
    eliminar_usuarios_seleccionados.short_description = "Eliminar usuarios seleccionados"

# Muestra la información de Arrendatario con el usuario relacionado
class ArrendatarioAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Arrendatario.

    Esta clase personaliza la visualización y administración de los arrendatarios en el panel de administración de Django.
    Permite marcar arrendatarios como verificados, eliminar arrendatarios junto con sus usuarios, y filtrarlos por ciudad.

    Atributos:
    - list_display: Define los campos que se mostrarán para cada arrendatario.
    - search_fields: Especifica los campos por los cuales se puede buscar un arrendatario (nombre, apellidos, correo).
    - list_filter: Permite filtrar los arrendatarios por verificación y ciudad.
    - actions: Define acciones personalizadas para los arrendatarios.
    
    Métodos:
    - usuario: Muestra el nombre de usuario asociado a cada arrendatario.
    - marcar_como_verificado: Acción personalizada para marcar varios arrendatarios como verificados.
    - eliminar_usuarios_seleccionados: Acción personalizada para eliminar arrendatarios seleccionados y sus usuarios relacionados.
    """
    list_display = ('nombre', 'apellidos', 'correo', 'telefono', 'direccion', 'is_verificado')
    search_fields = ('nombre', 'apellidos', 'correo')
    list_filter = ('is_verificado', 'direccion__ciudad')
    actions = ['marcar_como_verificado', 'eliminar_usuarios_seleccionados']
    
    def usuario(self, obj):
        """
        Muestra el nombre de usuario relacionado al arrendatario.

        Parámetros:
        - obj: El objeto de arrendatario para el que se quiere obtener el nombre de usuario.

        Devuelve:
        - El nombre de usuario del arrendatario.
        """
        return obj.usuario.username

    # Acción para marcar como verificado
    def marcar_como_verificado(self, request, queryset):
        """
        Marca como verificados los arrendatarios seleccionados.

        Esta acción personaliza la administración de arrendatarios, marcando a los arrendatarios seleccionados
        como verificados y mostrando un mensaje de éxito.

        Parámetros:
        - request: La solicitud HTTP que contiene los datos de los arrendatarios seleccionados.
        - queryset: El conjunto de arrendatarios seleccionados.

        Devuelve:
        - Un mensaje informando al administrador la cantidad de arrendatarios verificados.
        """
        queryset.update(is_verificado=True)
        self.message_user(request, f"{queryset.count()} arrendatarios marcados como verificados.")
    marcar_como_verificado.short_description = "Marcar como verificado"

    # Acción personalizada para eliminar usuarios seleccionados
    def eliminar_usuarios_seleccionados(self, request, queryset):
        """
        Elimina los arrendatarios seleccionados junto con sus usuarios relacionados.

        Esta acción personalizada elimina a los arrendatarios seleccionados de la base de datos,
        así como sus usuarios asociados, proporcionando un mensaje de éxito al administrador.

        Parámetros:
        - request: La solicitud HTTP con los arrendatarios seleccionados.
        - queryset: El conjunto de arrendatarios seleccionados.

        Devuelve:
        - Un mensaje informando al administrador la cantidad de arrendatarios eliminados.
        """ 
        for arrendatario in queryset:
            usuario = arrendatario.usuario
            arrendatario.delete()
            usuario.delete()
        self.message_user(request, f"{queryset.count()} arrendatarios eliminados junto con sus usuarios relacionados.")
    eliminar_usuarios_seleccionados.short_description = "Eliminar usuarios seleccionados"

# Registra los modelos en el panel de admin
admin.site.register(Direccion, DireccionAdmin)
admin.site.register(Arrendador, ArrendadorAdmin)
admin.site.register(Arrendatario, ArrendatarioAdmin)
