import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import AIModel  # Импортируйте вашу модель
from openai import AsyncOpenAI  # Импортируйте ваш клиент OpenAI
from dotenv import load_dotenv
import os
load_dotenv()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.model_name = self.scope['url_route']['kwargs']['model_name']
        self.room_group_name = f'chat_{self.model_name}'

        # Получаем модель AI из базы данных по slug
        self.ai_model = await self.get_ai_model(self.model_name)
        if not self.ai_model:
            await self.close()  # Закрываем соединение, если модель не найдена

        self.model_identifier = self.ai_model.model  # Получаем значение поля model

        # Присоединяемся к группе чата
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Отключаемся от группы чата
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data['message']

        # Отправляем сообщение "думаю..." пользователю
        await self.send(text_data=json.dumps({
            'message': "Ai обрабатывает ваш запрос. Пожалуйста, подождите немного ...",
            'user_message': user_message,
            'is_thinking': True,  # Новый флаг
        }))

        response_content = await self.get_ai_response(user_message)

        # Отправляем окончательный ответ
        await self.send(text_data=json.dumps({
            'message': response_content,
            'user_message': user_message,
            'is_thinking': False,  # Новый флаг
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
            api_key=os.getenv('api_key')  # Не храните API ключи в коде
        )

        try:
            print(self.model_identifier)
            response = await client.chat.completions.create(
                model=self.model_identifier,  # Используем модель из базы данных
                messages=[{"role": "user", "content": user_message}]
            )

            if not response.choices:
                print("Нет доступных вариантов в ответе.")
                return "Извините, я не смог получить ответ."  # Возвращаем строку

            ai_message = response.choices[0].message.content
            print("Ответ от API:", ai_message)
            return ai_message  # Возвращаем строку

        except Exception as e:
            print(f"Произошла ошибка при вызове API: {e}")
            return "Произошла ошибка при получении ответа."  # Возвращаем строку

    @database_sync_to_async
    def get_ai_model(self, slug):
        try:
            return AIModel.objects.get(slug=slug)
        except AIModel.DoesNotExist:
            return None
