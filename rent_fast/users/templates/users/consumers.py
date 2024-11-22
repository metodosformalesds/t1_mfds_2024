# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
import json


class IdentityConsumer(AsyncWebsocketConsumer):
    """
    Consumer para manejar la verificación de identidad a través de WebSockets.

    Este consumidor maneja la conexión de un cliente (usuario) para verificar su identidad mediante imágenes.
    Recibe imágenes de un cliente y las envía a todos los miembros del grupo (en este caso, el grupo correspondiente al usuario).
    """
    async def connect(self):
        """
        Maneja la conexión de un cliente WebSocket.
        
        Crea un grupo de WebSocket único para cada usuario basado en su `user_id`. 
        Este grupo permitirá que las imágenes relacionadas con la verificación de identidad 
        se envíen a las pestañas abiertas del cliente.

        Se une al grupo de WebSocket asociado a `user_id` y acepta la conexión WebSocket.
        """
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f"identity_verification_{self.user_id}"

        # Únete al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """
        Maneja la desconexión del cliente WebSocket.

        Al desconectar, abandona el grupo asociado al usuario para evitar el envío de mensajes innecesarios.
        """
        # Abandona el grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Maneja los datos recibidos del cliente WebSocket.

        Recibe las imágenes enviadas por el cliente, las decodifica y las envía a todos los miembros del grupo.
        """
        data = json.loads(text_data)
        image_data = data.get('image_data')

        # Envía la imagen a la pestaña abierta en la computadora
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_image',
                'image_data': image_data
            }
        )

    async def send_image(self, event):
        """
        Maneja el envío de la imagen a todos los miembros del grupo.

        Recibe los datos de la imagen desde el grupo y los envía a través del WebSocket.
        """
        image_data = event['image_data']

        # Envía la imagen a la pestaña de la computadora
        await self.send(text_data=json.dumps({
            'image_data': image_data
        }))


class VerifyIdentityConsumer(WebsocketConsumer):
    """
    Consumer para la verificación de identidad utilizando una imagen temporal.

    Este consumidor maneja la verificación de identidad de un usuario basado en un `temp_id`. 
    Recibe imágenes de la cámara del usuario y las envía a todos los miembros del grupo 
    para su validación.
    """ 
    def connect(self):
        """
        Maneja la conexión de un cliente WebSocket para la verificación de identidad.

        Crea un grupo de WebSocket único basado en el `temp_id` del usuario. 
        Este grupo está destinado a la verificación de identidad temporal.
        """
        self.temp_id = self.scope['url_route']['kwargs']['temp_id']
        self.room_group_name = f'verify_{self.temp_id}'

        # Unirse al grupo
        self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        """
        Maneja la desconexión de un cliente WebSocket para la verificación de identidad.

        Al desconectar, abandona el grupo asociado a la verificación de identidad temporal.
        """
        # Abandonar el grupo
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        """
        Maneja los datos recibidos del cliente WebSocket.

        Recibe las imágenes enviadas por el cliente para la verificación de identidad 
        y las envía al grupo correspondiente.
        """
        data = json.loads(text_data)
        image_data = data.get('image_data')

        # Enviar imagen al grupo
        self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_image',
                'image_data': image_data
            }
        )

    def send_image(self, event):
        """
        Maneja el envío de la imagen para la verificación de identidad.

        Recibe la imagen del grupo y la envía al cliente WebSocket para su visualización.
        """
        image_data = event['image_data']
        self.send(text_data=json.dumps({
            'image_data': image_data
        }))
