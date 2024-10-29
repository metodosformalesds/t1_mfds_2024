from django.contrib.auth.views import LoginView, LogoutView
from .views import RegisterWizard, Landing, RegisterAddres  # Importa solo de .views
from django.urls import path

urlpatterns = [
    path(
        "login/", LoginView.as_view(template_name="users/login.html"), 
        name="login"
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("registro/", RegisterWizard.as_view(), name="register"),
    path("landing/", Landing.as_view(), name="landing"),
    path("address/", RegisterAddres.as_view(), name="address"),
]
