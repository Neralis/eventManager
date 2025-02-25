from __future__ import absolute_import
import os
from celery import Celery
from click import clear

# этот код скопирован с manage.py
# он установит модуль настроек по умолчанию Django для приложения 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventManager.settings')

# здесь вы меняете имя
app = Celery("eventManager", broker="redis://localhost:6379", backend="redis://localhost:6379")
clear()

# Для получения настроек Django, связываем префикс "CELERY" с настройкой celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# загрузка tasks.py в приложение django
app.autodiscover_tasks()


@app.task
def add(x, y):
    return x / y