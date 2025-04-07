import os
import django


# Указываем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventManager.settings')
django.setup()


from django.contrib.sites.models import Site
from tasksApp.celery_schedule import setup_periodic_tasks
from userApp.models import CustomUser

# Выполняем задачи
setup_periodic_tasks()

Site.objects.update_or_create(
    id=1,
    defaults={'name': 'localhost', 'domain': '127.0.0.1:8000'}
)

if not CustomUser.objects.filter(username='test').exists():
    CustomUser.objects.create_superuser(
        username='test',
        email='test@gmail.com',
        password='test'
    )

