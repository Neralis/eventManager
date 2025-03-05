from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.timezone import now


class EventappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eventApp'

    def ready(self):
        import eventApp.signals


