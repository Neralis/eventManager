from django.db.models.signals import post_save, post_delete, pre_save
from django.utils.timezone import now
from django.dispatch import receiver
from django.core.mail import send_mail
from participantApp.models import Participants


@receiver(post_save, sender=Participants)
def update_available_places_on_save(sender, instance, created, **kwargs):
    if created:
        event = instance.event
        event.available_places = event.participants_limit - event.participants.count()
        event.save(update_fields=['available_places'])


@receiver(post_delete, sender=Participants)
def update_available_places_on_delete(sender, instance, **kwargs):
    event = instance.event
    event.available_places = event.participants_limit - event.participants.count()
    event.save(update_fields=['available_places'])


@receiver(post_save, sender=Participants)
def registration_on_event(sender, instance, **kwargs):
    event = instance.event
    send_mail(
        f'Вы зарегестрировались на мероприятие "{event.title}"',
        'Спасибо за вашу активность!',
        'example@gmail.com',
        [instance.get_email()],
        fail_silently=False,
    )


@receiver(pre_save, sender=Participants)
def check_participants_limit(sender, instance, **kwargs):
    available_places = instance.event.available_places
    if available_places <= 0:
        raise ValueError('error: Нет свободных мест для регистрации на мероприятие')


@receiver(pre_save, sender=Participants)
def check_activity_status_and_date(sender, instance, **kwargs):
    event = instance.event
    if not event.is_active or event.date_start > now():
        raise ValueError('error: Нельзя зарегистрироваться на прошедшее или уже начавшееся событие')