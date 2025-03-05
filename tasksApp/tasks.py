from django.db import transaction
from django.utils.timezone import now, timedelta
from eventApp.models import Event
from participantApp.models import Participants
from userApp.models import Notification
from django.core.mail import send_mail
from celery import shared_task
from tasksApp.utils import generate_token


@shared_task
def send_email_for_users_before_event():
    event_time_lower = now() + timedelta(hours=2, minutes=56)
    event_time_upper = now() + timedelta(hours=3, minutes=1)
    participants = Participants.objects.filter(
        event__in=Event.objects.filter(
            is_active=True,
            date_start__range=(event_time_lower, event_time_upper)
        )
    ).select_related('event', 'user', 'not_auth_user')
    participant_email = [participant.get_email() for participant in participants]
    # noinspection PyTypeChecker
    send_mail(
        'Начало вашего мероприятия через 3 часа',
        'поспешите пу-пу-пу',
        'example@gmail.com',
        participant_email,
        fail_silently=False,
    )


def update_completed_events():
    completed_events = Event.objects.filter(
        is_active=True,
        date_end__lt=now()
    )
    if not completed_events.exists():
        print('Подходящие мероприятия не найдены')
        return []
    completed_events_id = list(completed_events.values_list('id', flat=True))
    with transaction.atomic():
        completed_events.update(is_active=False)
        print('Успешно')
    return completed_events_id


@shared_task
def check_actual_date_event():
    completed_event_id = update_completed_events()
    if not completed_event_id:
        return
    participants = Participants.objects.filter(
        event__id__in=completed_event_id,
    ).select_related('event', 'user', 'not_auth_user')
    if not participants.exists():
        return
    notifications = []
    send_mails = []
    for participant in participants:
        if participant.user:
            notifications.append(
                Notification(
                    user=participant.user,
                    title='Оставьте, пожалуйста, отзыв',
                    text=f'Мероприятие, в котром вы участвовали {participant.event.title} завершилось',
                    url_event=participant.event.get_absolute_url()
                )
            )
        else:
            send_mails.append((participant.pk, participant.event.pk))
    if notifications:
        Notification.objects.bulk_create(notifications)
    if send_mails:
        for participant_id, event_id in send_mails:
            send_mail_to_participant.delay(participant_id, event_id)


@shared_task
def send_mail_to_participant(participant_id, event_id):
    participant = Participants.objects.get(pk=participant_id)
    event = Event.objects.get(pk=event_id)
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


@shared_task
def remove_notifications():
    time_life = now() - timedelta(days=30)
    try:
        Notification.objects.filter(created_at__lt=time_life).delete()
    except Exception as e:
        print(f'error {e}')
