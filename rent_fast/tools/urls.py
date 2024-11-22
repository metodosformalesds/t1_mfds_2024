from django.urls import path
from .views import home_view, arrendador_home, arrendatario_home, ToolFormView, ToolListView, ToolDetailView, add_tool_view, rent_tool_view, agregar_al_carrito_view, carrito_view, seleccionar_fechas_view, resumen_view, confirmar_renta_view, admin_home, approve_tool, reject_tool, uber_auth, uber_callback, obtener_cotizacion, pagar_sin_paypal_view, eliminar_del_carrito_view, editar_herramienta_view, eliminar_herramienta_view, revisar_tool_view

"""
Este archivo contiene las rutas URL para las vistas de la aplicación relacionada con la gestión de herramientas y rentas.

Las rutas están organizadas para cubrir tanto el acceso de los arrendadores y arrendatarios a las herramientas,
como las funcionalidades de carrito de compras, pagos y administración de herramientas.

Rutas Definidas:

1. Home:
   - '/' : Página principal de la aplicación, accesible para todos los usuarios.

2. Arrendador:
   - '/arrendador/' : Página principal para arrendadores.
   - '/agregar/' : Vista para que los arrendadores agreguen nuevas herramientas.
   - '/herramienta/<pk>/' : Vista de detalle de herramienta.
   - '/herramienta/<tool_id>/editar/' : Vista para editar una herramienta específica.
   - '/herramienta/<tool_id>/eliminar/' : Vista para eliminar una herramienta específica.

3. Arrendatario:
   - '/arrendatario/' : Página principal para arrendatarios.
   - '/herramienta/<int:tool_id>/seleccionar-fechas/' : Vista para seleccionar las fechas de renta de una herramienta.
   - '/herramienta/<tool_id>/agregar-al-carrito/' : Vista para agregar una herramienta al carrito de un arrendatario.
   - '/carrito/' : Vista para mostrar el carrito de alquiler del arrendatario.
   - '/carrito/eliminar/<int:item_id>/' : Elimina una herramienta del carrito.
   - '/resumen/' : Vista que muestra un resumen de la renta antes de confirmarla.
   - '/confirmar-renta/' : Vista para confirmar la renta de herramientas.

4. Administración:
   - '/admin_home/' : Página de inicio del panel de administración.
   - '/admin/approve_tool/<int:tool_id>/' : Ruta para aprobar una herramienta que ha sido enviada por un arrendador.
   - '/admin/reject_tool/<int:tool_id>/' : Ruta para rechazar una herramienta enviada por un arrendador.
   - '/admin/revisar_tool/<int:tool_id>/' : Ruta para revisar una herramienta antes de aprobarla o rechazarla.

5. Pago:
   - '/pago/sin-paypal/' : Ruta para realizar pagos sin usar PayPal.

6. Uber:
   - '/uber/auth/' : Ruta de autenticación con Uber.
   - '/uber/callback/' : Ruta de callback de Uber para obtener resultados después de la autenticación.
   - '/uber/cotizacion/' : Ruta para obtener una cotización de Uber.

"""
urlpatterns = [
    path('', home_view, name='home'),
    path('arrendador/', arrendador_home, name='arrendador_home'),
    path('herramienta/<int:pk>/', ToolDetailView.as_view(), name='tool_detail'),
    path('arrendatario/', arrendatario_home, name='arrendatario_home'),
    path('agregar/', add_tool_view, name='add_tool'),
    path('', ToolListView.as_view(), name='list_tool'),
    path('carrito/', carrito_view, name='carrito'),
    path('carrito/eliminar/<int:item_id>/', eliminar_del_carrito_view, name='eliminar_del_carrito'),
    path('herramienta/<int:tool_id>/seleccionar-fechas/', seleccionar_fechas_view, name='seleccionar_fechas'),
    path('herramienta/<int:tool_id>/agregar-al-carrito/', agregar_al_carrito_view, name='agregar_al_carrito'),
    path('resumen/', resumen_view, name='resumen'),
    path('confirmar-renta/', confirmar_renta_view, name='confirmar_renta'),
    path('admin_home/', admin_home, name='admin_home'),  # Ruta para el home del administrador
    path('admin/approve_tool/<int:tool_id>/', approve_tool, name='approve_tool'),
    path('admin/reject_tool/<int:tool_id>/', reject_tool, name='reject_tool'),
    path("pago/sin-paypal/", pagar_sin_paypal_view, name="pagar_sin_paypal"),  # Nueva URL
    path('uber/auth/', uber_auth, name='uber_auth'),
    path('uber/callback/', uber_callback, name='uber_callback'),
    path('uber/cotizacion/', obtener_cotizacion, name='obtener_cotizacion'),
    
    path('herramienta/<int:tool_id>/editar/', editar_herramienta_view, name='editar_herramienta'),
    path('herramienta/<int:tool_id>/eliminar/', eliminar_herramienta_view, name='eliminar_herramienta'),
    path('admin/revisar_tool/<int:tool_id>/', revisar_tool_view, name='revisar_tool'),

]