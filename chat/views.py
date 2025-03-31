from django.shortcuts import render, get_object_or_404
from .models import AIModel, AnonymousUserMessage
import uuid


def models_view(request):
    ai_models = AIModel.objects.all()
    return render(request, 'chat/index.html', {'ai_models': ai_models})


def chat_view(request, model_name):
    user_uuid = request.COOKIES.get('user_uuid')
    if not user_uuid:
        user_uuid = str(uuid.uuid4())

    ai_model = get_object_or_404(AIModel, slug=model_name)

    messages = AnonymousUserMessage.objects.filter(
        uuid=user_uuid, ai_model=ai_model
    ).order_by('timestamp')

    response = render(request, 'chat/chat.html', {
        'model_name': model_name,
        'messages': messages,
    })
    response.set_cookie('user_uuid', user_uuid, max_age=60 * 60 * 24, httponly=True)

    return response



