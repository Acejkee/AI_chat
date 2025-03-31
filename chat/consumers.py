import json
import uuid
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from openai import AsyncOpenAI
from .models import AIModel, AnonymousUserMessage
from dotenv import load_dotenv
load_dotenv()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.model_slug = self.scope['url_route']['kwargs']['model_name']
        self.uuid = self.scope['cookies'].get('user_uuid') # Получаем UUID из куки

        if not self.uuid: # Если UUID нет в куки
            self.uuid = str(uuid.uuid4())

        self.room_group_name = f'chat_{self.model_slug}_{self.uuid}'

        self.ai_model = await self.get_ai_model(self.model_slug)
        if not self.ai_model:
            await self.close()
            return

        self.model_identifier = self.ai_model.model

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()



    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data['message']

        await self.send(text_data=json.dumps({
            'message': "⏳ AI обрабатывает ваш запрос. Пожалуйста, подождите немного ...",
            'user_message': user_message,
            'is_thinking': True,
        }))

        response_content = await self.get_ai_response(user_message)
        await self.save_message(user_message, response_content)

        await self.send(text_data=json.dumps({
            'message': response_content,
            'user_message': user_message,
            'is_thinking': False,
        }))

    async def chat_message(self, event):
        message = event['message']
        user_message = event['user_message']

        # Отправляем сообщение пользователю
        await self.send(text_data=json.dumps({
            'message': message,
            'user_message': user_message,
        }))

    async def get_ai_response(self, user_message):
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv('api_key')
        )

        try:
            response = await client.chat.completions.create(
                model=self.model_identifier,
                messages=[{"role": "user", "content": user_message}]
            )

            if not response.choices:
                print("Нет доступных вариантов в ответе.")
                return "Извините, я не смог получить ответ."

            ai_message = response.choices[0].message.content
            print("Ответ от API:", ai_message)
            return ai_message

        except Exception as e:
            print(f"Произошла ошибка при вызове API: {e}")
            return "Произошла ошибка при получении ответа."

    @database_sync_to_async
    def get_ai_model(self, slug):
        try:
            return AIModel.objects.get(slug=slug)
        except AIModel.DoesNotExist:
            return None

    async def save_message(self, user_message, ai_message):
        await database_sync_to_async(AnonymousUserMessage.objects.create)(
            uuid=self.uuid,
            ai_model=self.ai_model,
            role='user',
            content=user_message
        )
        await database_sync_to_async(AnonymousUserMessage.objects.create)(
            uuid=self.uuid,
            ai_model=self.ai_model,
            role='ai',
            content=ai_message
        )



