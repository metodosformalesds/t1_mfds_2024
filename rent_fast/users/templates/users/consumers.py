# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
import json


class IdentityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f"identity_verification_{self.user_id}"

        # Únete al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Abandona el grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
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
        image_data = event['image_data']

        # Envía la imagen a la pestaña de la computadora
        await self.send(text_data=json.dumps({
            'image_data': image_data
        }))


class VerifyIdentityConsumer(WebsocketConsumer):
    def connect(self):
        self.temp_id = self.scope['url_route']['kwargs']['temp_id']
        self.room_group_name = f'verify_{self.temp_id}'

        # Unirse al grupo
        self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Abandonar el grupo
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
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
        image_data = event['image_data']
        self.send(text_data=json.dumps({
            'image_data': image_data
        }))
