from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from src.apps.participantApp.models import Participants
from src.apps.eventApp.models import Event


@receiver(post_save, sender=Participants)
def update_available_places_on_save(sender, instance, created, **kwargs) -> None:
    """Сигнал для изменения количества свободных мест(уменьшение) после создания нового участника."""
    if created:
        Event.objects.filter(id=instance.id).update(available_places=F('available_places') - 1)


@receiver(post_save, sender=Participants)
def registration_on_event(sender, instance, created, **kwargs) -> None:
    """Сигнал для отправки письма на почту пользователю после создания нового участника."""
    from src.apps.tasksApp.tasks import registration_on_event_task

    registration_on_event_task.delay(instance.get_email(), instance.event.title)


@receiver(post_delete, sender=Participants)
def update_available_places_on_delete(sender, instance, **kwargs) -> None:
    """Сигнал для изменения количества свободных мест(увеличение) после удаления участника."""
    Event.objects.filter(id=instance.id).update(available_places=F('available_places') + 1)