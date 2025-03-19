from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.timezone import now
from userApp.models import CustomUser


@receiver(pre_delete, sender=CustomUser)
def block_delete_user(sender, instance, **kwargs) -> None:
    """
    Сигнал для запрета удаления аккаунта пользователя,
    если у него на данный момент есть мероприятия, в которых он выполняет роль организатора.
    """

    from eventApp.models import Event

    events = Event.objects.filter(
        organizer=instance,
        date_start__lte=now(),
        date_end__gte=now()
    )
    if events.exists():
        raise Exception('Пользователь с активными мероприятиями не может быть удален')


@receiver(pre_delete, sender=CustomUser)
def delete_users_events(sender, instance, **kwargs) -> None:
    """
    Сигнал для удаления всех будущих мероприятий у пользователя,
    если он является организатором этих мероприятий.
    """

    from eventApp.models import Event

    events = Event.objects.filter(
        organizer=instance,
        date_start__gt=now()
    )
    events.delete()