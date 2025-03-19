from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils.timezone import now
from eventApp.models import Event


@receiver(post_migrate, sender=Event)
def create_default_organizer(sender, instance, **kwargs) -> None:
    """Сигнал для создания дефолтного пользователя после миграций."""
    try:
        CustomUser = sender.get_model('userApp', 'CustomUser')
        CustomUser.objects.get_or_create(
            username='default_remove_user',
            email='remove_user@gmail.com',
            date_birthday=now(),
            phone='+12345678911'
        )
    except LookupError:
        pass