from autoslug import AutoSlugField

from django.db import models
import uuid


class AIModel(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(max_length=400, populate_from='name', always_update=True, editable=False)
    model = models.CharField(max_length=255)
    image = models.ImageField(upload_to='model_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class AnonymousUserMessage(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('ai', 'AI')]) # !!! Новое поле
    content = models.TextField() # !!! content вместо message
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta: # !!! Сортировка по умолчанию
        ordering = ['timestamp']
