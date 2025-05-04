import logging
import jwt
from typing import Tuple, Optional

from django.db.models import Avg, FloatField
from django.db.models.functions import Coalesce

from src.utils.utils import generate_token, validate_token, generate_unique_url, send_mail_users
from src.utils.constants.email_constants import RECOVER_ACCOUNT_INFO, RECOVER_ACCOUNT_TITLE

logger = logging.getLogger(__name__)


def user_avatar_path(instance, filename: str) -> str:
    """
    Динамический путь для аватарки пользователя.
    Args:
        instance: объект UserProfile
        filename: название файла для поля avatar
    """
    return f'users/{instance.user.id}/avatar/{filename}'


def generate_token_for_user(email: str, user_id: int) -> str:
    """
    Фукнция генерации токена для восстановления аккаунта.
    Args:
        email: email пользователя
        user_id: id пользователя
    """

    payload = {
        'email': email,
        'user_id': user_id,
    }
    return generate_token(payload, days=1)


def validate_token_for_user(token: str) -> Tuple[Optional[str], Optional[int]]:
    """
    Валидация токена для пользователя.
    Args:
        token: токен для валидации
    """

    try:
        payload = validate_token(token, required_fields=['email', 'user_id'])
        return payload['email'], payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None, None


def generate_unique_url_for_user(token: str) -> str:
    """
    Функция для генерации уникальной ссылки для восстановления аккаунта пользователя.
    Args:
        token: токен для генерации уникальной ссылки на страницу создания отзыва
    """

    url = generate_unique_url('recover_account', kwargs={'token': token})
    return url


def send_mail_user_for_activate_account(email: str, unique_url: str) -> None:
    """
    Функция для отправки писем на почту пользователям для восстановления аккаунта.
    Args:
        email: email пользователя
        unique_url: уникальная ссылка для восстановления(активации)
    """

    subject = RECOVER_ACCOUNT_TITLE
    message = f'{RECOVER_ACCOUNT_INFO}{unique_url}'
    send_mail_users(subject, message, [email])


def calculate_average_rating_organizer(user_id: int) -> None:
    """
    Функция для расчета средней оценки организатора по отзывам на его мероприятия.
    Args:
        user_id: id пользователя(организатора)
    """
    from src.apps.userApp.models import UserProfile
    from src.apps.reviewApp.models import Review

    try:
        avg_rating = (
            Review.objects
            .filter(event__organizer__id=user_id)
            .aggregate(avg=Coalesce(Avg('rating', output_field=FloatField()), 0.0))['avg']
        )
        UserProfile.objects.filter(user__id=user_id).update(average_rating=round(avg_rating, 2))
    except Exception as e:
        logger.error(str(e))
        raise