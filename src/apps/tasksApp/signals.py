from django.db.models.signals import post_migrate
from django.dispatch import receiver
from src.apps.tasksApp.celery_schedule import setup_periodic_tasks


@receiver(post_migrate)
def setup_periodic_tasks_after_migrate(sender, **kwargs) -> None:
    """Сигнал для выполнения celery-задач только после миграций."""
    if sender.name == 'tasksApp':
        setup_periodic_tasks()