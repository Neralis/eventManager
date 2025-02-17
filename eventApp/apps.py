from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.timezone import now


class EventappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eventApp'

    def ready(self):
        from eventApp.apps import get_default_organizer  # Импортируем функцию внутри ready()
        post_migrate.connect(create_default_organizer, sender=self)


def create_default_organizer(sender, **kwargs):
    get_default_organizer()  # Вызываем функцию для создания пользователя


def get_default_organizer():
    from userApp.models import CustomUser

    user, _ = CustomUser.objects.get_or_create(
        username='default_remove_user',
        email='remove_user@gmail.com',
        date_birthday=now(),
        phone='+12345678911'
    )
    return user
