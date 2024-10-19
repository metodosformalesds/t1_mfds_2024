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
    
    # Para ver la información relacionada del usuario en la misma tabla
    def usuario(self, obj):
        return obj.usuario.username

# Muestra la información de Arrendatario con el usuario relacionado
class ArrendatarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'correo', 'telefono', 'direccion', 'is_verificado')
    search_fields = ('nombre', 'apellidos', 'correo')
    list_filter = ('is_verificado', 'direccion__ciudad')
    
    def usuario(self, obj):
        return obj.usuario.username

# Registra los modelos en el panel de admin
admin.site.register(Direccion, DireccionAdmin)
admin.site.register(Arrendador, ArrendadorAdmin)
admin.site.register(Arrendatario, ArrendatarioAdmin)
