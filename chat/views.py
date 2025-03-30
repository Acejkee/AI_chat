from django.shortcuts import render
from .models import AIModel


def models_view(request):
    ai_models = AIModel.objects.all()
    return render(request, 'chat/index.html', {'ai_models': ai_models})


def chat_view(request, model_name):
    return render(request, 'chat/chat.html', {'model_name': model_name})

