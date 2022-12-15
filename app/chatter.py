import json
import traceback

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model

from .serializers import ChatMessageSerializer


UserModel = get_user_model()


class Dummy(WebsocketConsumer):
    def connect(self):
        self.group_name = "."
        self.close(4004)


class Chatter(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            receiver_id = self.scope['url_route']['kwargs']['user_id']
            if UserModel.objects.filter(id=receiver_id).exists():
                self.receiver = UserModel.objects.get(id=receiver_id)
                self.group_name = f'{self.user.id}-{receiver_id}' if self.user.id > receiver_id else f'{receiver_id}-{self.user.id}'
                async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
                self.accept()
            else:
                self.group_name = "."
                self.close(4004)
        else:
            self.group_name = "."
            self.close(4003)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        try:
            serializer = ChatMessageSerializer(data=json.loads(text_data))
            if serializer.is_valid():
                serializer.save(sender=self.user, receiver=self.receiver, is_read=False)
                async_to_sync(self.channel_layer.group_send)(
                    self.group_name, {
                        'type': 'chat_message',
                        'message': serializer.data
                    }
                )
            else:
                self.send(json.dumps({'message': serializer.errors}))
        except:
            traceback.print_exc()
            self.send(json.dumps({'message': '发送的信息格式不正确。'}))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({'message': message}))
