from django.db.models.signals import post_migrate, pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from eventApp.models import Event


@receiver(post_migrate, sender=Event)
def create_default_organizer(sender, instance, **kwargs):
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


@receiver(pre_save, sender=Event)
def update_available_places_from_participants_limit(sender, instance, **kwargs):
    from participantApp.models import Participants
    if instance.pk is None:
        instance.available_places = instance.participants_limit
    else:
        participants_count = Participants.objects.filter(event=instance).count()
        if instance.participants_limit < participants_count:
            raise ValueError('error: Лимит участников не может быть меньше,'
                             'чем количество зарегистрированных участников')
        instance.available_places = instance.participants_limit - participants_count
