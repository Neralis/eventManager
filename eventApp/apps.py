from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.timezone import now


def create_default_organizer(sender, **kwargs):
    try:
        CustomUser = sender.get_model('userApp', 'CustomUser')
        CustomUser.objects.get_or_create(
            username='default_remove_user',
            email='remove_user@gmail.com',
            date_birthday=now(),
            phone='+12345678911'
        )
    except LookupError:
        pass


class EventappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eventApp'

    def ready(self):
        post_migrate.connect(create_default_organizer, sender=self)


