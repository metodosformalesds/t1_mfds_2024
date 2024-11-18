from django.contrib import admin
from django.contrib.auth.models import User
from .models import Arrendador, Arrendatario, Direccion

# Muestra la información de la Dirección en el Admin
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('calle', 'ciudad', 'estado', 'codigo_postal')
    search_fields = ('ciudad', 'estado', 'codigo_postal')

# Muestra la información de Arrendador con el usuario relacionado
class ArrendadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'correo', 'telefono', 'direccion', 'is_verificado')
    search_fields = ('nombre', 'apellidos', 'correo')
    list_filter = ('is_verificado', 'direccion__ciudad')
    actions = ['marcar_como_verificado', 'eliminar_usuarios_seleccionados']
    
    # Para mostrar el nombre de usuario relacionado
    def usuario(self, obj):
        return obj.usuario.username

    # Acción para marcar como verificado
    def marcar_como_verificado(self, request, queryset):
        queryset.update(is_verificado=True)
        self.message_user(request, f"{queryset.count()} arrendadores marcados como verificados.")
    marcar_como_verificado.short_description = "Marcar como verificado"

    # Acción personalizada para eliminar usuarios seleccionados
    def eliminar_usuarios_seleccionados(self, request, queryset):
        for arrendador in queryset:
            usuario = arrendador.usuario
            arrendador.delete()
            usuario.delete()
        self.message_user(request, f"{queryset.count()} arrendadores eliminados junto con sus usuarios relacionados.")
    eliminar_usuarios_seleccionados.short_description = "Eliminar usuarios seleccionados"

# Muestra la información de Arrendatario con el usuario relacionado
class ArrendatarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'correo', 'telefono', 'direccion', 'is_verificado')
    search_fields = ('nombre', 'apellidos', 'correo')
    list_filter = ('is_verificado', 'direccion__ciudad')
    actions = ['marcar_como_verificado', 'eliminar_usuarios_seleccionados']
    
    def usuario(self, obj):
        return obj.usuario.username

    # Acción para marcar como verificado
    def marcar_como_verificado(self, request, queryset):
        queryset.update(is_verificado=True)
        self.message_user(request, f"{queryset.count()} arrendatarios marcados como verificados.")
    marcar_como_verificado.short_description = "Marcar como verificado"

    # Acción personalizada para eliminar usuarios seleccionados
    def eliminar_usuarios_seleccionados(self, request, queryset):
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
