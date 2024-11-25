from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.conf.urls.static import static
from .views import RegisterWizard,ver_notificaciones, Landing,verify_identity, RegisterAddres, TerminosCondiciones, RegisterPersonal, password_reset_request, verify_reset_code, set_new_password, actualizar_datos_view, gestionar_usuarios, eliminar_usuario
from .views import RegisterWizard, balance_view, Landing,verify_identity, RegisterAddres, TerminosCondiciones, RegisterPersonal, password_reset_request, verify_reset_code, set_new_password, actualizar_datos_view, update_address, generate_qr_for_identity, upload_identity_image, contratos_view
from django.urls import path
from . import views
 
urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("registro/", RegisterWizard.as_view(), name="register"),
    path("landing/", Landing.as_view(), name="landing"),
    path("address/", RegisterAddres.as_view(), name="address"),
    path("terminos/", TerminosCondiciones.as_view(), name="terminos"),
    path('verify_identity/', verify_identity, name='verify_identity'),
    path('notificaciones/', ver_notificaciones, name='notificaciones'),
    path("registro_personal/", RegisterPersonal.as_view(), name="register_personal"),
    path('password_reset/', password_reset_request, name='password_reset'),
    path('verify_reset_code/', verify_reset_code, name='verify_reset_code'),
    path('set_new_password/', set_new_password, name='set_new_password'),
    path("update_dates/", actualizar_datos_view, name="update_dates"),
    path("update_address/", update_address, name="update_address"),
    path('generate_qr_for_identity/', generate_qr_for_identity, name='generate_qr_for_identity'),
    path('upload_identity_image/', upload_identity_image, name='upload_identity_image'),
    path('contratos/', contratos_view, name='contratos'),
    path("buscar-codigo-postal-calle/", views.buscar_codigo_postal_calle, name="buscar_codigo_postal_calle"),
    path('gestionar_usuarios/', gestionar_usuarios, name='gestionar_usuarios'),
    path('eliminar_usuario/<int:usuario_id>/<str:tipo_usuario>/', eliminar_usuario, name='eliminar_usuario'),
    path("editar_usuario/<int:usuario_id>/<str:tipo_usuario>/", views.editar_usuario, name="editar_usuario"),
    path('balance/', balance_view, name='balance_view'),
 
 
]
 
# Configuración para servir archivos de medios en modo desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)