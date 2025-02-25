from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now, timedelta
from eventApp.models import Event
from participantApp.models import Participants
from userApp.models import Notification
from django.core.mail import send_mail
from celery import shared_task
from .utils import generate_token


@shared_task
def send_email_for_users_before_event():
    participants = Participants.objects.filter(
        event__in=Event.objects.filter(
            is_active=True,
            date_start__range=(now() + timedelta(hours=2, minutes=59), now() + timedelta(hours=3, minutes=1))
        )
    ).select_related('event', 'user', 'not_auth_user')
    participant_email = [participant.get_email() for participant in participants if participant.get_email()]
    # noinspection PyTypeChecker
    send_mail(
        'Начало вашего мероприятия через 3 часа',
        'поспешите пу-пу-пу',
        'example@gmail.com',
        [participant_email],
        fail_silently=False,
    )



@shared_task
def check_actual_date_event():
    participants = Participants.objects.filter(
        event__in=Event.objects.filter(
            is_active=True,
            date_end__lt=now()
        )
    ).select_related('event', 'user', 'not_auth_user')
    notifications = []
    send_mails = []
    for participant in participants:
        if participant.user:
            notifications.append(
                Notification(
                    user=participant.user,
                    text=f'Мероприятие, в котром вы участвовали {participant.event.title} завершилось',
                    url_event=participant.event.get_absolute_url()
                )
            )
        else:
            send_mails.append((participant, participant.event))

    Notification.objects.bulk_create(notifications)

    for participant, event in send_mails:
        send_mail_to_participant.delay(participant, event)


@shared_task
def send_mail_to_participant(participant, event):
    email = participant.get_email()
    token = generate_token(email, event.pk)
    unique_url = f'http://127.0.0.1:8000/review/review_create/{token}/'

    send_mail(
        f'Мероприятие "{event.title}" завершилось',
        f'Оставьте, пожалуйста, свое мнение о мероприятии по этой ссылке: {unique_url}',
        'example@gmail.com',
        [email],
        fail_silently=False,
    )
