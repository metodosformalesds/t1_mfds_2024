from django.urls import path
from .views import home_view, arrendador_home, arrendatario_home, ToolFormView, ToolListView, ToolDetailView, add_tool_view, rent_tool_view, agregar_al_carrito_view, carrito_view, seleccionar_fechas_view, resumen_view, confirmar_renta_view, admin_home, approve_tool, reject_tool, cotizar_envio_view, uber_callback_view, uber_login_view, pagar_sin_paypal_view

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
    path('admin_home/', admin_home, name='admin_home'),  # Ruta para el home del administrador
    path('admin/approve_tool/<int:tool_id>/', approve_tool, name='approve_tool'),
    path('admin/reject_tool/<int:tool_id>/', reject_tool, name='reject_tool'),
     path('uber/login/', uber_login_view, name='uber_login'),
    path('uber/callback/', uber_callback_view, name='uber_callback'),
    path('cotizar-envio/<int:tool_id>/', cotizar_envio_view, name='cotizar_envio'),
    path("pago/sin-paypal/", pagar_sin_paypal_view, name="pagar_sin_paypal"),  # Nueva URL

]
