from django.db import models
from users.models import Arrendador, Arrendatario
from rentas.models import Renta
from datetime import timedelta  

class Categoria(models.Model):
    """
    Representa una categoría a la que puede pertenecer una herramienta.

    Atributos:
    - nombre (str): El nombre de la categoría de la herramienta. Este campo es único.

    Métodos:
    - __str__(): Devuelve el nombre de la categoría como representación de cadena.
    """
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre
        
class Tool(models.Model):
    """
    Representa una herramienta disponible para ser alquilada por un arrendatario.

    Atributos:
    - arrendador (ForeignKey): El arrendador que posee la herramienta.
    - nombre (str): Nombre de la herramienta.
    - descripcion (TextField): Descripción detallada de la herramienta.
    - costo_dia (DecimalField): Costo de alquiler de la herramienta por día.
    - estado (str): Estado de la herramienta. Puede ser 'Pendiente', 'Disponible', o 'Rechazado'.
    - imagenes (ImageField): Imágenes de la herramienta.
    - categoria (ForeignKey): Categoría a la que pertenece la herramienta.
    - mensaje_rechazo (TextField): Motivo por el cual la herramienta fue rechazada, si aplica.

    Métodos:
    - __str__(): Devuelve el nombre de la herramienta como representación de cadena.
    - is_available(): Verifica si la herramienta está disponible para ser alquilada. 
    """
    arrendador = models.ForeignKey(Arrendador, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    costo_dia = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=[('Pendiente', 'Pendiente'), ('Disponible', 'Disponible'), ('Rechazado', 'Rechazado')], default='Pendiente')
    imagenes = models.ImageField(upload_to='tools/', null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    mensaje_rechazo = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre

    def is_available(self):
        """
        Verifica si la herramienta está disponible para rentar.
        Retorna False si está en una renta activa, True en caso contrario.
        """
        return not Renta.objects.filter(herramienta=self, estado="Activa").exists()


        
class Carrito(models.Model):
    """
    Representa un elemento en el carrito de un arrendatario.

    Atributos:
    - arrendatario (ForeignKey): El arrendatario que tiene la herramienta en su carrito.
    - herramienta (ForeignKey): La herramienta que se encuentra en el carrito.
    - fecha_agregada (DateTimeField): Fecha y hora en la que la herramienta fue agregada al carrito.
    - fecha_inicio (DateField): Fecha de inicio de la renta de la herramienta.
    - fecha_fin (DateField): Fecha de finalización de la renta de la herramienta.
    - costo_total (DecimalField): Costo total de la renta calculado en función de las fechas.

    Métodos:
    - __str__(): Devuelve una representación de cadena del carrito, mostrando el nombre de la herramienta y el arrendatario.
    """
    arrendatario = models.ForeignKey(Arrendatario, on_delete=models.CASCADE)
    herramienta = models.ForeignKey('Tool', on_delete=models.CASCADE)
    fecha_agregada = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)

    def _str_(self):
        return f"{self.herramienta.nombre} en el carrito de {self.arrendatario}"
