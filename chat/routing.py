from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<str:model_name>/', consumers.ChatConsumer.as_asgi()),
]
