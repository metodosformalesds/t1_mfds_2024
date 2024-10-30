from django.contrib import admin
from .models import Renta

class RentaAdmin(admin.ModelAdmin):
    model = Renta
    list_display = ["herramienta"]

admin.site.register(Renta, RentaAdmin)
