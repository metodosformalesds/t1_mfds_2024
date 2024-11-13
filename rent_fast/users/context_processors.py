from .models import Notificacion
from django.conf import settings

from .models import Notificacion
from django.conf import settings

def notificaciones_no_leidas(request):
    if request.user.is_authenticated:
        # Obtener el conteo de notificaciones no leídas
        unread_count = Notificacion.objects.filter(usuario=request.user, leido=False).count()
        
        # Obtener las notificaciones no leídas
        notificaciones_no_leidas = Notificacion.objects.filter(usuario=request.user, leido=False)
        
        # Enviar tanto el contador como las notificaciones
        return {
            'unread_count': unread_count,
            'notificaciones_no_leidas': notificaciones_no_leidas
        }
    
    # Si no está autenticado, retornar solo el contador en 0
    return {'unread_count': 0, 'notificaciones_no_leidas': []}



def cart_count(request):
    if request.user.is_authenticated:
        cart_count = request.user.cart.items.count()
    else:
        cart_count = 0
    return {'cart_count': cart_count}
