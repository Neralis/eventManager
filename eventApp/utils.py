import os
import shutil
import string
from random import choices
from unidecode import unidecode
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from eventManager import settings
from userApp.models import CustomUser


def get_default_organizer() -> int:
    """Функция для получения id дефолтного пользователя."""
    return CustomUser.objects.get(username='default_remove_user').id


def event_main_photo_path(instance, filename: str) -> str:
    """Динамический путь для основного фото мероприятия."""
    if instance.id:
        return f'events/{instance.id}/main_photo/{filename}'
    return f'temp/events/main_photo/{filename}'


def event_additional_image_path(instance, filename: str) -> str:
    """Динамический путь для дополнительных изображений."""
    if instance.event_id:
        return f'events/{instance.event.id}/additional_images/{filename}'
    return f'temp/events/additional_images/{filename}'


def get_random_string() -> str:
    """Функция для генерации рандомной строки. Используется для создания уникальных слагов."""
    return ''.join(choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=6))


def generate_unique_slug(instance) -> None:
    """Функция для генерации уникального слага."""
    from eventApp.models import Event

    baseslug = slugify(unidecode(instance.title))
    if not instance.slug or not instance.slug.startswith(baseslug):
        slug = f'{baseslug}-{get_random_string()}'
        while Event.objects.filter(slug=slug).exists():
            slug = f'{baseslug}-{get_random_string()}'
        instance.slug = slug


def update_available_places_from_participants_limit(instance) -> None:
    """Функция для обновления свободных мест на мероприятии."""
    from participantApp.models import Participants

    if instance.id:
        participants_count = Participants.objects.filter(event=instance).count()
        if instance.participants_limit < participants_count:
            raise ValidationError('error: Лимит участников не может быть меньше,'
                                  'чем количество зарегистрированных участников.')
        instance.available_places = instance.participants_limit - participants_count
    else:
        instance.available_places = instance.participants_limit


def create_directory_for_main_photo(instance) -> None:
    """Функция для создания директории для основного изображения."""
    if instance.main_photo:
        event_dir = os.path.join(settings.MEDIA_ROOT, f'events/{instance.id}')
        main_photo_dir = os.path.join(event_dir, 'main_photo')
        try:
            os.makedirs(main_photo_dir, exist_ok=True)
        except OSError as e:
            raise ValidationError(f"Ошибка при создании директорий: {e}")


def create_directory_for_additional_image(instance) -> None:
    """Функция для создания директории для дополнительных изображений."""
    event_dir = os.path.join(settings.MEDIA_ROOT, f'events/{instance.event.id}/additional_images')
    try:
        os.makedirs(event_dir, exist_ok=True)
    except OSError as e:
        raise ValidationError(f"Ошибка при создании директории: {e}")


def move_event_directory(instance) -> None:
    """Функция для создания директории для главного изображения после сохранения."""
    create_directory_for_main_photo(instance)
    if instance.main_photo and instance.main_photo.name.startswith('temp/'):
        old_path = instance.main_photo.path
        new_path = os.path.join(settings.MEDIA_ROOT, event_main_photo_path(instance, os.path.basename(old_path)))
        shutil.move(old_path, new_path)
        instance.main_photo.name = event_main_photo_path(instance, os.path.basename(old_path))
        instance.save(update_fields=['main_photo'])


def move_event_image_directory(instance) -> None:
    """Функция для создания директории для дополнительных изображений после сохранения."""
    create_directory_for_additional_image(instance)
    if instance.image and instance.image.name.startswith('temp/'):
        old_path = instance.image.path
        new_path = os.path.join(settings.MEDIA_ROOT,
                                event_additional_image_path(instance, os.path.basename(old_path)))
        shutil.move(old_path, new_path)
        instance.image.name = event_additional_image_path(instance, os.path.basename(old_path))
        instance.save(update_fields=['image'])


def delete_old_file(file_path: str) -> None:
    """Функция для удаления файла."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError as e:
            print(f'Ошибка при удалении файла: {e}')


def delete_old_main_image(instance) -> None:
    """Функция для удаления старого главного изображения перед сохранением нового."""
    from eventApp.models import Event

    if instance.id:
        try:
            old_instance = Event.objects.get(pk=instance.pk)
            if old_instance.main_photo and instance.main_photo and instance.main_photo != old_instance.main_photo:
                delete_old_file(old_instance.main_photo.path)
        except Event.DoesNotExist:
            return


def delete_old_additional_image(instance) -> None:
    """Функция для удаления старого дополнительного изображения перед сохранением нового."""
    from eventApp.models import EventImages

    if instance.id:
        try:
            old_instance = EventImages.objects.get(pk=instance.pk)
            if old_instance.image and instance.image and instance.image != old_instance.image:
                delete_old_file(old_instance.image.path)
        except EventImages.DoesNotExist:
            return


def delete_event_directory(instance) -> None:
    """Функция для удаления папки мероприятия."""
    event_dir = os.path.join(settings.MEDIA_ROOT, f'events/{instance.id}')
    if os.path.exists(event_dir):
        try:
            shutil.rmtree(event_dir)
        except OSError as e:
            print(f"Ошибка при удалении файла: {e}")


def delete_event_image_file(instance):
    """Функция для удаления изображения при удалении объекта EventImages."""
    if instance.image and os.path.exists(instance.image.path):
        try:
            os.remove(instance.image.path)
        except OSError as e:
            print(f"Ошибка при удалении файла: {e}")