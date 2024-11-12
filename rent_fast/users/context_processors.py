from .models import Notificacion
from django.conf import settings

def notificaciones_no_leidas(request):
    if request.user.is_authenticated:
        unread_count = Notificacion.objects.filter(usuario=request.user, leido=False).count()
        return {'unread_count': unread_count}
    return {'unread_count': 0}


def cart_count(request):
    if request.user.is_authenticated:
        cart_count = request.user.cart.items.count()
    else:
        cart_count = 0
    return {'cart_count': cart_count}
