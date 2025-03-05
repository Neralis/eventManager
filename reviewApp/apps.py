from django.apps import AppConfig


class ReviewappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviewApp'

    def ready(self):
        import reviewApp.signals
