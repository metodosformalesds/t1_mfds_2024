from django.urls import path
from .views import home_view, arrendador_home, arrendatario_home, ToolFormView, ToolListView, ToolDetailView, add_tool_view, rent_tool_view, agregar_al_carrito_view, carrito_view, seleccionar_fechas_view, resumen_view, confirmar_renta_view

urlpatterns = [
    path('', home_view, name='home'),
    path('arrendador/', arrendador_home, name='arrendador_home'),
    path('herramienta/<int:pk>/', ToolDetailView.as_view(), name='tool_detail'),
    path('arrendatario/', arrendatario_home, name='arrendatario_home'),
    path('agregar/', add_tool_view, name='add_tool'),
    path('', ToolListView.as_view(), name='list_tool'),
    path('carrito/', carrito_view, name='carrito'),
    path('carrito/', carrito_view, name='carrito'),
    path('herramienta/<int:tool_id>/seleccionar-fechas/', seleccionar_fechas_view, name='seleccionar_fechas'),
    path('herramienta/<int:tool_id>/agregar-al-carrito/', agregar_al_carrito_view, name='agregar_al_carrito'),
    path('resumen/', resumen_view, name='resumen'),
    path('confirmar-renta/', confirmar_renta_view, name='confirmar_renta'),

]
