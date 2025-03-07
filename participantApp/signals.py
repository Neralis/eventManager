from django.db.models.signals import post_save, post_delete, pre_save
from django.utils.timezone import now
from django.conf import settings
from django.dispatch import receiver
from django.core.mail import send_mail
from participantApp.models import Participants
from tasksApp.constants import SEND_MAIL_REGISTER_ON_EVENT_TEXT, SEND_MAIL_REGISTER_ON_EVENT_TITLE


@receiver(pre_save, sender=Participants)
def check_organizer_registration(sender, instance, **kwargs) -> None:
    """Сигнал для проверки, что организатор не может зарегистрироваться на созданное им же мероприятие."""
    event = instance.event
    user = instance.user if instance.user else None
    if user:
        if instance.user == event.organizer:
            raise ValueError('error: Организатор не может зарегистрироваться на свое же мероприятие.')


@receiver(pre_save, sender=Participants)
def check_date_birth_participant(sender, instance, **kwargs) -> None:
    """Сигнал для проверки, что на мероприятии с обязательной регистрацией необходима проврека возраста пользователя"""
    if instance.event.registration_status and instance.user is not None:
        participant_date_birthday = instance.user.date_birthday
        today = now().date()
        age = today.year - participant_date_birthday.year
        if (today.month, today.day) < (participant_date_birthday.month, participant_date_birthday.day):
            age -= 1
        if int(age) < instance.event.age_limit:
            raise ValueError('error: Возрастное ограничение, вы не достигли необходимого возроста для участия')


@receiver(pre_save, sender=Participants)
def check_activity_status_and_date(sender, instance, **kwargs) -> None:
    """Сигнал для проверки статуса активности и даты начала мероприятия перед созданием нового участника."""
    event = instance.event
    if not event.is_active or event.date_start < now():
        raise ValueError('error: Нельзя зарегистрироваться на прошедшее или уже начавшееся событие.')


@receiver(pre_save, sender=Participants)
def check_participants_limit(sender, instance, **kwargs) -> None:
    """Сигнал для проверки количества свободных мест на мероприятии перед созданием нового участника."""
    available_places = instance.event.available_places
    if available_places <= 0:
        raise ValueError('error: Нет свободных мест для регистрации на мероприятие.')


@receiver(pre_save, sender=Participants)
def check_status_registration_on_event(sender, instance, **kwargs) -> None:
    """Сигнал для проверки статуса регистрации мероприятия перед созданием нового участника."""
    event = instance.event
    if event.registration_status and instance.not_auth_user is not None:
        raise ValueError('error: Неавторизованный пользователь не может '
                         'записаться на мероприятие с обязательной регистрацией.')


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
    if created:
        event = instance.event
        send_mail(
            f'{SEND_MAIL_REGISTER_ON_EVENT_TITLE}{event.title}',
            SEND_MAIL_REGISTER_ON_EVENT_TEXT,
            settings.EMAIL_HOST_USER,
            [instance.get_email()],
            fail_silently=False,
        )


@receiver(post_delete, sender=Participants)
def update_available_places_on_delete(sender, instance, **kwargs) -> None:
    """Сигнал для изменения количества свободных мест(увеличение) после удаления участника."""
    event = instance.event
    event.available_places += 1
    event.save(update_fields=['available_places'])



