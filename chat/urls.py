from django.urls import path
from .views import chat_view, models_view

urlpatterns = [
    path('', models_view, name='models'),
    path('chat/<slug:model_name>/', chat_view, name='chat'),
]
