import logging
from typing import List
from django.conf import settings
from django.utils.timezone import now, timedelta
from eventApp.models import Event
from eventApp.utils import update_completed_events, send_mail_with_reason
from participantApp.models import Participants
from reviewApp.utils import generate_token_for_review, generate_unique_url_for_participants, \
    send_mail_to_not_auth_user_participant
from userApp.utils import send_mail_user
from userApp.models import Notification
from django.core.mail import send_mail
from celery import shared_task
from utils.constants.email_constants import (
    SEND_MAIL_BEFORE_EVENT_TITLE,
    SEND_MAIL_BEFORE_EVENT_TEXT,
    MESSAGE_TITLE,
    MESSAGE_TEXT_EVENT_INFO,
    MESSAGE_TEXT_EVENT_URL
)

logger = logging.getLogger(__name__)


@shared_task
def send_email_for_participants_before_event() -> None:
    """Функция celery для отправки писем на почту пользователям за 3 часа до начала мероприятия."""
    event_time_lower = now() + timedelta(hours=2, minutes=57)
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
        SEND_MAIL_BEFORE_EVENT_TITLE,
        SEND_MAIL_BEFORE_EVENT_TEXT,
        settings.EMAIL_HOST_USER,
        participant_email,
        fail_silently=False,
    )


@shared_task
def check_actual_date_event() -> None:
    """
    Функция celery для проверки наличия актуальных событий, дата завершения которых прошла.
    Если такие существуют, то отправялется ссылка для создания отзыва участникам мероприятия.
    """

    completed_event_id = update_completed_events()
    if not completed_event_id:
        return
    participants = Participants.objects.filter(
        event__id__in=completed_event_id,
    ).select_related('event', 'user', 'not_auth_user')
    notifications = []
    send_mails = []
    for participant in participants:
        event = participant.event
        token = generate_token_for_review(participant.get_email(), event.id)
        unique_url = generate_unique_url_for_participants(token)
        if participant.user:
            notifications.append(
                Notification(
                    user=participant.user,
                    title=MESSAGE_TITLE,
                    text=f'{MESSAGE_TEXT_EVENT_INFO}{event.title}\n{MESSAGE_TEXT_EVENT_URL}',
                    url_event=unique_url
                )
            )
        else:
            send_mails.append((participant.get_email(), event.title, unique_url))
    if notifications:
        Notification.objects.bulk_create(notifications)
    if send_mails:
        for email, event_title, unique_url in send_mails:
            send_mail_to_not_auth_user_participant(email, event_title, unique_url)


@shared_task
def remove_notifications() -> None:
    """Функция celery для удаления уведомлений, дата создания которых больше месяца назад."""
    time_life = now() - timedelta(days=30)
    try:
        Notification.objects.filter(created_at__lt=time_life).delete()
    except Exception as e:
        logger.error(f'Ошибка {e}')


@shared_task
def send_mail_with_reason_task(email_list: List[str], event_title: str, reason: str) -> None:
    """
    Функция celery для отправки сообщений участникам о причине удаления мероприятия.
    Args:
        email_list: список email участников мероприятия
        event_title: название мероприятия, которое удалили
        reason: причина удаления мероприятия
    """

    send_mail_with_reason(email_list, event_title, reason)


@shared_task
def send_mail_for_activate_account_task(email: str, unique_url: str) -> None:
    """
    Функция celery для отправки сообщений пользователям для восстановления(активации) аккаунта.
    Args:
        email: список email участников мероприятия
        unique_url: уникальная ссылка для восстановления аккаунта
    """

    send_mail_user(email, unique_url)

