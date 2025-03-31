from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import AnonymousUserMessage

@shared_task
def delete_old_messages():
    expiration_time = timezone.now() - timedelta(days=1)
    AnonymousUserMessage.objects.filter(timestamp__lt=expiration_time).delete()
