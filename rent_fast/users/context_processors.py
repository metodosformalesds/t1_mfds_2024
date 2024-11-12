from .models import Notificacion

def notificaciones_no_leidas(request):
    if request.user.is_authenticated:
        unread_count = Notificacion.objects.filter(usuario=request.user, leido=False).count()
        return {'unread_count': unread_count}
    return {'unread_count': 0}
