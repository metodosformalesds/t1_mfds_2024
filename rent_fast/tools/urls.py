from django.urls import path
from .views import home_view, arrendador_home, arrendatario_home, ToolFormView, ToolListView

urlpatterns = [
    path('', home_view, name='home'),
    path('arrendador/', arrendador_home, name='arrendador_home'),
    path('arrendatario/', arrendatario_home, name='arrendatario_home'),
    path('agregar/', ToolFormView.as_view(), name='add_tool'),
    path('', ToolListView.as_view(), name='list_tool'),
]
