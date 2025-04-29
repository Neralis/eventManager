from django.apps import AppConfig


class ParticipantAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.apps.participantApp'

    def ready(self):
        import src.apps.participantApp.signals
