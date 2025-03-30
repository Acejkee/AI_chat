from autoslug import AutoSlugField

from django.db import models


class AIModel(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(max_length=400, populate_from='name', always_update=True, editable=False)
    model = models.CharField(max_length=255)
    image = models.ImageField(upload_to='ai_models/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


