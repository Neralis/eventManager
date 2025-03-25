from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from participantApp.models import Participants
from utils.constants.email_constants import SEND_MAIL_REGISTER_ON_EVENT_TITLE, SEND_MAIL_REGISTER_ON_EVENT_TEXT


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
    from utils.utils import send_mail_users

    if created:
        subject = f'{SEND_MAIL_REGISTER_ON_EVENT_TITLE}{instance.event.title}'
        message = SEND_MAIL_REGISTER_ON_EVENT_TEXT
        send_mail_users(subject, message, [instance.get_email()])


@receiver(post_delete, sender=Participants)
def update_available_places_on_delete(sender, instance, **kwargs) -> None:
    """Сигнал для изменения количества свободных мест(увеличение) после удаления участника."""
    event = instance.event
    event.available_places += 1
    event.save(update_fields=['available_places'])