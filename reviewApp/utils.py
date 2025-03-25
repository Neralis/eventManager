import jwt
from typing import Optional, Tuple
from utils.utils import generate_unique_url, generate_token, validate_token, send_mail_users
from utils.constants_email import (
    MESSAGE_TITLE,
    MESSAGE_TEXT_EVENT_INFO,
    MESSAGE_TEXT_EVENT_URL
)


def generate_token_for_review(email: str, event_id: int) -> str:
    """
    Генерация токена для создания отзыва на мероприятие.
    Args:
        email: email участника для генерации токена
        event_id: id мероприятия для генерации токена
    """

    payload = {
        'email': email,
        'event_id': event_id,
    }
    return generate_token(payload, days=7)


def validate_token_for_review(token: str) -> Tuple[Optional[str], Optional[int]]:
    """
    Валидация токена для отзыва.
    Args:
        token: токен для валидации
    """

    try:
        payload = validate_token(token, required_fields=['email', 'event_id'])
        return payload['email'], payload['event_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None, None


def generate_unique_url_for_participants(token: str) -> str:
    """
    Генерация уникальной ссылки при помощи токена для создания отзыва.
    Args:
        token: токен для генерации уникальной ссылки на страницу создания отзыва
    """

    url = generate_unique_url('review_create', kwargs={'token': token})
    return url


def send_mail_to_not_auth_user_participant(email: str, event_title: str, unique_url: str) -> None:
    """
    Функция для отправки писем на почту неавторизованным пользователям.
    Args:
        email: email участника, которому будет отправлено письмо для оставления отзыва
        event_title: название мероприятия
        unique_url: уникальная ссылка для оставления отзыва
    """

    subject = MESSAGE_TITLE
    message = f'{MESSAGE_TEXT_EVENT_INFO}{event_title}\n{MESSAGE_TEXT_EVENT_URL}{unique_url}'
    send_mail_users(subject, message, [email])