from django.contrib.auth.views import LoginView, LogoutView
from .views import RegisterWizard, Landing, RegisterAddres, TerminosCondiciones, RegisterPersonal, password_reset_request, verify_reset_code, set_new_password, actualizar_datos_view  # Agrega RegisterPersonal
from django.urls import path

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("registro/", RegisterWizard.as_view(), name="register"),
    path("landing/", Landing.as_view(), name="landing"),
    path("address/", RegisterAddres.as_view(), name="address"),
    path("terminos/", TerminosCondiciones.as_view(), name="terminos"),
    path("registro_personal/", RegisterPersonal.as_view(), name="register_personal"), 
    path('password_reset/', password_reset_request, name='password_reset'),
    path('verify_reset_code/', verify_reset_code, name='verify_reset_code'),
    path('set_new_password/', set_new_password, name='set_new_password'),
    path("update_dates/", actualizar_datos_view, name="update_dates"),

]
