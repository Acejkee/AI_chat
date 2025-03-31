# django_celery/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.autodiscover_tasks()


app.conf.beat_schedule = {
    'delete-old-messages-every-day': {
        'task': 'chat.tasks.delete_old_messages',
        'schedule': crontab(minute=0, hour=0),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')