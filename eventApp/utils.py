import logging
import string
from random import choices
from typing import List
from django.utils.timezone import now
from django.db import transaction
from unidecode import unidecode
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from utils.file_handler import FileHandler
from utils.utils import send_mail_users
from utils.constants.email_constants import DELETE_EVENT_MESSAGE_INFO, DELETE_EVENT_MESSAGE_TITLE

logger = logging.getLogger(__name__)


def event_main_photo_path(instance, filename: str) -> str:
    """
    Динамический путь для основного фото мероприятия.
    Args:
        instance: объект Event
        filename: название файла для поля main_photo
    """

    return f'events/{instance.slug}/main_photo/{filename}'


def event_additional_image_path(instance, filename: str) -> str:
    """
    Динамический путь для основного фото мероприятия.
    Args:
        instance: объект EventImages
        filename: название файла для поля image
    """

    return f'events/{instance.event.slug}/additional_images/{filename}'


def get_random_string() -> str:
    """Функция для генерации рандомной строки. Используется для создания уникальных слагов."""
    return ''.join(choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=6))


def generate_unique_slug(instance) -> None:
    """
    Функция для генерации уникального слага.
    Args:
        instance: объект Event
    """

    from eventApp.models import Event

    baseslug = slugify(unidecode(instance.title))
    if not instance.slug or not instance.slug.startswith(baseslug):
        slug = f'{baseslug}-{get_random_string()}'
        while Event.objects.filter(slug=slug).exists():
            slug = f'{baseslug}-{get_random_string()}'
        instance.slug = slug


def update_available_places_from_participants_limit(instance) -> None:
    """
    Функция для обновления свободных мест на мероприятии.
    Args:
        instance: объект Event
    """

    from participantApp.models import Participants

    if instance.id:
        participants_count = Participants.objects.filter(event=instance).count()
        if instance.participants_limit < participants_count:
            raise ValidationError('error: Лимит участников не может быть меньше,'
                                  'чем количество зарегистрированных участников.')
        instance.available_places = instance.participants_limit - participants_count
    else:
        instance.available_places = instance.participants_limit


def update_completed_events() -> List[int]:
    """
    Обновление статуса активности завершившихся мероприятий, если такие есть.
    Возвращает список id завершившихся мероприятий.
    """

    from eventApp.models import Event

    completed_events = Event.objects.filter(
        is_active=True,
        date_end__lt=now()
    )
    if not completed_events.exists():
        logger.info('Подходящие мероприятия не найдены')
        return []
    completed_events_id = list(completed_events.values_list('id', flat=True))
    with transaction.atomic():
        completed_events.update(is_active=False)
        logger.info('Успешно')
    return completed_events_id


def delete_old_main_image(instance) -> None:
    """
    Функция для удаления старого главного изображения перед сохранением нового.
    Args:
        instance: объект Event
    """

    from eventApp.models import Event
    FileHandler.delete_old_image(instance, Event, 'main_photo')


def delete_old_additional_image(instance) -> None:
    """
    Функция для удаления старого дополнительного изображения перед сохранением нового.
    Args:
        instance: объект EventImages
    """

    from eventApp.models import EventImages
    FileHandler.delete_old_image(instance, EventImages, 'image')


def search_event(query: str, min_similarity: float = 0.2) -> QuerySet:
    """
    Функция для поиска мероприятий по названию и описанию.
    Args:
        query: текс запроса в поисковой строке
        min_similarity: порог сходства для поиска(по умолчанию равен 0.2)
    """

    from eventApp.models import Event
    from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
    from django.db.models import F, Value

    query = query.strip().lower()
    search_query = SearchQuery(Value(query), config='russian')

    result = Event.objects.annotate(
        search=SearchVector('title', 'description', config='russian'),
        rank=SearchRank(SearchVector('title', 'description', config='russian'), search_query),
        title_similarity=TrigramSimilarity('title', Value(query)),
        description_similarity=TrigramSimilarity('description', Value(query)),
        weighted_similarity=(F('title_similarity') * 0.7) + (F('description_similarity') * 0.3),
    ).filter(
        weighted_similarity__gt=min_similarity
    ).order_by('-weighted_similarity')

    return result


def send_mail_with_reason(email_list: List[str], event_title: str, reason: str = '') -> None:
    """
    Функция для отправки сообщений на почту участникам мероприятия, если организатор его отменит.
    Args:
        email_list: список email участников мероприятия
        event_title: название мероприятия, которое удалили
        reason: причина удаления мероприятия, по умполчанию None
    """

    subject = f'{DELETE_EVENT_MESSAGE_TITLE}{event_title}'
    message = DELETE_EVENT_MESSAGE_INFO
    if reason:
        message += f'\nПричина отмены мероприятия: {reason}'
    send_mail_users(subject, message, email_list)