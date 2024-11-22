from .models import Notificacion
from django.conf import settings

from .models import Notificacion
from django.conf import settings

def notificaciones_no_leidas(request):
    """
    Obtiene el número de notificaciones no leídas para el usuario autenticado.

    Esta función consulta la base de datos para contar las notificaciones no leídas 
    asociadas al usuario actualmente autenticado, y también obtiene una lista de esas notificaciones.

    Parámetros:
    - request: Objeto HttpRequest que contiene la información del usuario autenticado.

    Devuelve:
    - Un diccionario con dos claves:
        - 'unread_count': El número total de notificaciones no leídas para el usuario.
        - 'notificaciones_no_leidas': Una lista de las notificaciones no leídas para el usuario.
    """
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
    """
    Obtiene el número de artículos en el carrito de compras del usuario autenticado.

    Esta función consulta la base de datos para contar el número de artículos que el usuario ha agregado 
    al carrito de compras. Si el usuario no está autenticado, devuelve un conteo de 0.

    Parámetros:
    - request: Objeto HttpRequest que contiene la información del usuario autenticado.

    Devuelve:
    - Un diccionario con la clave 'cart_count', que indica el número total de artículos en el carrito del usuario.
    """
    if request.user.is_authenticated:
        cart_count = request.user.cart.items.count()
    else:
        cart_count = 0
    return {'cart_count': cart_count}
