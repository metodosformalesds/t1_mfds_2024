from django.urls import path
from .views import home_view, arrendador_home, arrendatario_home, ToolFormView, ToolListView, ToolDetailView

urlpatterns = [
    path('', home_view, name='home'),
    path('arrendador/', arrendador_home, name='arrendador_home'),
    path('herramienta/<int:pk>/', ToolDetailView.as_view(), name='tool_detail'),
    path('arrendatario/', arrendatario_home, name='arrendatario_home'),
    path('agregar/', ToolFormView.as_view(), name='add_tool'),
    path('', ToolListView.as_view(), name='list_tool'),
]
