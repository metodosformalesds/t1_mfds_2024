
from django.urls import path

urlpatterns = [
    path(
        "home/", LoginView.as_view(template_name="home_arrendador.html"), 
        name="home"
        ),

]