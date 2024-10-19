from django.contrib.auth.views import LoginView, LogoutView, RegisterView
from django.urls import path

urlpatterns = [
    path(
        "login/", LoginView.as_view(template_name="users/login.html"), 
        name="login"
        ),
    path(
        "register/", RegisterView.as_view(template_name="users/register.html"), 
        name="register"
        ),

    path("logout/", LogoutView.as_view(), name="logout"),
]