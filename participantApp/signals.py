from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from participantApp.models import Participants


@receiver(post_save, sender=Participants)
def update_available_places_on_save(sender, instance, created, **kwargs) -> None:
    """Сигнал для изменения количества свободных мест(уменьшение) после создания нового участника."""
    if created:
        event = instance.event
        event.available_places -= 1
        event.save(update_fields=['available_places'])


@receiver(post_save, sender=Participants)
def registration_on_event(sender, instance, created, **kwargs) -> None:
    """Сигнал для отправки письма на почту пользователю после создания нового участника."""
    from tasksApp.utils import registration_on_event

    if created:
        registration_on_event(instance)


@receiver(post_delete, sender=Participants)
def update_available_places_on_delete(sender, instance, **kwargs) -> None:
    """Сигнал для изменения количества свободных мест(увеличение) после удаления участника."""
    event = instance.event
    event.available_places += 1
    event.save(update_fields=['available_places'])