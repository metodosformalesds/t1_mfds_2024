from django.urls import path
from .views import ProductFormView, ProductListView

urlpatterns = [
    path("login", ProductListView.as_view(), name="login"),
    path('register/', ProductFormView.as_view(), name="register"),
]