from django.contrib.auth.views import LoginView, LogoutView
from .views import RegisterWizard,ver_notificaciones, Landing,verify_identity, RegisterAddres, TerminosCondiciones, RegisterPersonal, password_reset_request, verify_reset_code, set_new_password, actualizar_datos_view 
from .views import RegisterWizard, Landing,verify_identity, RegisterAddres, TerminosCondiciones, RegisterPersonal, password_reset_request, verify_reset_code, set_new_password, actualizar_datos_view, update_address, generate_qr_for_identity, upload_identity_image, contratos_view
from django.urls import path

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

]


