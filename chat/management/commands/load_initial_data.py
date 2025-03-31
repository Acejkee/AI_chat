from django.core.management.base import BaseCommand
from django.core.management import call_command
from chat.models import AIModel  # Импортируйте вашу модель

class Command(BaseCommand):
    help = 'Load initial data and update slugs'

    def handle(self, *args, **kwargs):
        # Загружаем данные из фиктуры
        call_command('loaddata', 'initial_data.json')  # Укажите имя вашей фиктуры

        # Обновляем slug для всех объектов
        for obj in AIModel.objects.all():
            obj.save()  # Это вызовет генерацию slug

        self.stdout.write(self.style.SUCCESS('Successfully loaded initial data and updated slugs.'))
