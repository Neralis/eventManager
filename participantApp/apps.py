from django.apps import AppConfig


class ParticipantappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'participantApp'

    def ready(self):
        import participantApp.signals
