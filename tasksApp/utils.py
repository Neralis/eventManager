import datetime
import jwt
from django.conf import settings
from django.contrib.sites.models import Site
from typing import List, Optional, Tuple
from django.core.mail import send_mail
from django.utils.timezone import now
from django.db import transaction
from django.urls import reverse
from eventApp.models import Event
from tasksApp.constants import (
    MESSAGE_TITLE,
    MESSAGE_TEXT_EVENT_INFO,
    MESSAGE_TEXT_EVENT_URL,
    SEND_MAIL_REGISTER_ON_EVENT_TEXT,
    SEND_MAIL_REGISTER_ON_EVENT_TITLE
)


def generate_token(email: str, event_id: int) -> str:
    """Генерация токена для создания отзыва на мероприятие."""
    payload = {
        'email': email,
        'event_id': event_id,
        'exp': now() + datetime.timedelta(days=7),
        'iat': now()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def validate_token(token: str) -> Tuple[Optional[str], Optional[int]]:
    """Валидация токена."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload['email'], payload['event_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None, None


def update_completed_events() -> List[int]:
    """
    Обновление статуса активности завершившихся мероприятий, если такие есть.
    Возвращает список id завершившихся мероприятий.
    """

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


def generate_unique_url_for_participants(token: str) -> str:
    """Генерация уникальной ссылки при помощи токена для создания отзыва."""
    path = reverse('review_create', kwargs={'token': token})
    site_domain = Site.objects.get_current().domain
    return f'{site_domain}{path}'


def send_mail_to_not_auth_user_participant(email: str, event_title: str, unique_url: str) -> None:
    """Функция для отправки писем на почту неавторизованным пользователям."""
    send_mail(
        MESSAGE_TITLE,
        f'{MESSAGE_TEXT_EVENT_INFO}{event_title}\n{MESSAGE_TEXT_EVENT_URL}{unique_url}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


def registration_on_event(instance) -> None:
    """Функция для отправки письма на почту пользователю после создания нового участника."""
    send_mail(
        f'{SEND_MAIL_REGISTER_ON_EVENT_TITLE}{instance.event.title}',
        SEND_MAIL_REGISTER_ON_EVENT_TEXT,
        settings.EMAIL_HOST_USER,
        [instance.get_email()],
        fail_silently=False,
    )