import logging
import os
import shutil
from django.core.files.storage import default_storage
from eventManager import settings

logger = logging.getLogger(__name__)


class FileHandler:
    """Класс для обработки файлов."""
    @staticmethod
    def save_file(instance, file_field_name: str, path_function) -> None:
        file_field = getattr(instance, file_field_name)
        if file_field:
            try:
                if hasattr(file_field, 'file') and hasattr(file_field.file, 'name'):
                    original_filename = os.path.basename(file_field.file.name)
                else:
                    original_filename = os.path.basename(file_field.name)
                name, ext = os.path.splitext(original_filename)
                if len(name) > 100:
                    name = name[:100]
                    original_filename = f'{name}{ext}'
                new_name = path_function(instance, original_filename)
                saved_path = default_storage.save(new_name, file_field)
                setattr(instance, file_field_name, saved_path)
            except Exception as e:
                logger.error(f"Ошибка при сохранении файла {file_field.name}: {e}")
        else:
            logger.debug(f"Файл не загружен: {file_field}")

    @staticmethod
    def delete_file(file_path: str) -> None:
        """Удаляет файл, если тот есть."""
        if file_path:
            try:
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
            except Exception as e:
                logger.error(f"Ошибка при удалении файла {file_path}: {e}")

    @staticmethod
    def delete_old_image(instance, model_class, file_field_name: str) -> None:
        """Удаляет старое изображение перед сохранением нового."""
        if instance.id:
            try:
                old_instance = model_class.objects.get(id=instance.id)
                old_file = getattr(old_instance, file_field_name)
                new_file = getattr(instance, file_field_name)
                if old_file and new_file and old_file != new_file:
                    FileHandler.delete_file(old_file.name)
            except model_class.DoesNotExist:
                pass

    @staticmethod
    def delete_event_folder(slug) -> None:
        """Удаляет полностью папку мероприятия."""
        folder_path = os.path.join(settings.MEDIA_ROOT, 'events', slug)
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
            except Exception as e:
                logger.error(f"Ошибка при удалении папки {folder_path}: {e}")

    @staticmethod
    def delete_folder_if_empty(folder_path: str) -> None:
        """Удаляет папку, если она пуста."""
        if os.path.exists(folder_path):
            try:
                if not os.listdir(folder_path):
                    os.rmdir(folder_path)
            except Exception as e:
                logger.error(f"Ошибка при удалении папки {folder_path}: {e}")

    @staticmethod
    def delete_event_image_with_folder_cleanup(file_path: str) -> None:
        """Удаляет файл и папку, если та пустая, после удаления объекта EventImages."""
        if file_path:
            FileHandler.delete_file(file_path)
            folder_path = os.path.dirname(os.path.join(settings.MEDIA_ROOT, file_path))
            FileHandler.delete_folder_if_empty(folder_path)