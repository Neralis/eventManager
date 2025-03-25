import jwt
import datetime
import logging
from typing import List, Dict, Any, Optional
from django.utils.timezone import now
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.urls import reverse
from eventManager import settings

logger = logging.getLogger(__name__)


def send_mail_users(subject: str, message: str, recipient_list: List[str], fail_silently: bool = False) -> None:
    """
    Общая функция для отправки сообщений на почту.
    Args:
        subject: заголовок
        message: текст письма
        recipient_list: список email-адресов
        fail_silently: параметр для игнорирования ошибки, если True, то ошибка игнорируется и наоборот
    """

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=fail_silently
        )
    except Exception as e:
        logger.error(f'Ошибка при отправки email: {e}')


def generate_unique_url(view_name: str, kwargs: Dict[str, Any]) -> str:
    """
    Общая функция для генерации ссылки.
    Args:
        view_name: название представления
        kwargs: словарь параметров для генерации ссылки
    """

    try:
        site_domain = Site.objects.get_current().domain
        url = reverse(view_name, kwargs=kwargs)
        return f"{site_domain}{url}"
    except Exception as e:
        logger.error(f'Ошибка генерации url: {e}')


def generate_token(payload: Dict[str, Any], days: int = 7) -> str:
    """
    Общая функция для генерации JWT-токена.
    Args:
        payload: словарь данных для генеарции токена
        days: время жизни токена в днях
    """

    try:
        token_payload = payload.copy()
        if 'exp' not in token_payload:
            token_payload['exp'] = now() + datetime.timedelta(days=days)
        if 'iat' not in token_payload:
            token_payload['iat'] = now()
        return jwt.encode(token_payload, settings.SECRET_KEY, algorithm='HS256')
    except Exception as e:
        logger.error(f'Ошибка при генерации токена {e}')


def validate_token(token: str, required_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Общая функция для валидации JWT-токена и возврата содержимого.
    Args:
        token: токен для валидации
        required_fields: список полей, которые должны содержаться в payload(необязательный параметр)
    """

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        if required_fields:
            missing_fields = [field for field in required_fields if field not in payload]
            if missing_fields:
                raise jwt.InvalidTokenError(f'Токен должен содержать указанные поля: {missing_fields}')
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        logger.error(f'Ошибка при валидации токена {e}')
        raise
