from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from userApp.models import CustomUser


@receiver(pre_save, sender=CustomUser)
def delete_users_events(sender, instance, **kwargs) -> None:
    """
    Сигнал для удаления всех будущих мероприятий у пользователя,
    если он является организатором этих мероприятий и его статус активности 'is_active' меняется на False.
    """

    from eventApp.models import Event

    if not instance.is_active:
        events = Event.objects.filter(
            organizer=instance,
            date_start__gt=now()
        )
        for event in events:
            event.delete()