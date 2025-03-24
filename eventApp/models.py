import logging
from django.db import models
from django.db.models import Q, F
from django.core.validators import FileExtensionValidator
from eventApp.utils import event_main_photo_path, generate_unique_slug, \
    update_available_places_from_participants_limit, \
    event_additional_image_path, delete_old_additional_image
from userApp.models import CustomUser
from utils.file_handler import FileHandler

logger = logging.getLogger(__name__)


class Category(models.Model):
    title = models.CharField(
        max_length=50,
        verbose_name='Название категории',
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Event(models.Model):
    EVENT_FORMAT = [
        ('Online', 'Онлайн'),
        ('Offline', 'Оффлайн'),
    ]

    title = models.CharField(
        max_length=250,
        verbose_name='Название мероприятия',
    )
    slug = models.SlugField(
        blank=True,
        unique=True,
        verbose_name='Слаг'
    )
    category = models.ManyToManyField(
        Category,
        related_name='events',
        verbose_name='Категории'
    )
    description = models.TextField(
        blank=True,
        max_length=3500,
        verbose_name='Описание мероприятия'
    )
    date_start = models.DateTimeField(
        verbose_name='Дата и время начала мероприятия'
    )
    date_end = models.DateTimeField(
        verbose_name='Дата и время конца мероприятия'
    )
    age_limit = models.PositiveIntegerField(
        default=0,
        verbose_name='Возрастное ограничение'
    )

    organizer = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='events',
        verbose_name='Организатор мероприятия'
    )

    event_format = models.CharField(
        max_length=7,
        choices=EVENT_FORMAT,
        verbose_name='Формат мероприятия'
    )
    registration_status = models.BooleanField(
        default=False,
        verbose_name='Статус регистрации для мероприятия'
    )

    participants_limit = models.PositiveIntegerField(
        default=1,
        verbose_name='Лимит участников'
    )
    available_places = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество свободных мест'
    )

    location_offline = models.CharField(
        max_length=300,
        blank=True,
        default='',
        verbose_name='Место проведения мероприятия оффлайн'
    )
    city = models.CharField(
        max_length=300,
        blank=True,
        default='',
        verbose_name='Город, в котором проводится оффлайн мероприятия'
    )
    location_online = models.URLField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name='Ссылка для проведения онлайн мероприятия'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Статус активности мероприятия'
    )

    main_photo = models.ImageField(
        upload_to=event_main_photo_path,
        blank=True,
        max_length=255,
        validators=[FileExtensionValidator(
            allowed_extensions=['png', 'jpg', 'jpeg'],
            message='Вы можете использовать только файлы с расширениями PNG и JPEG.'
        )],
        verbose_name='Фото для обложки'
    )

    objects = models.Manager()

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['date_start', 'date_end']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(date_end__gt=F('date_start')),
                name='check_data'
            ),
            models.CheckConstraint(
                check=(
                        (Q(location_offline='') & Q(location_online__isnull=False)) |
                        (~Q(location_offline='') & Q(location_online__isnull=True))
                ),
                name='check_location'
            )
        ]

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        generate_unique_slug(self)
        update_available_places_from_participants_limit(self)
        if self.id:
            old_instance = self.__class__.objects.get(id=self.id)
            if old_instance.main_photo != self.main_photo:
                FileHandler.delete_old_image(self, self.__class__, 'main_photo')
        if self.main_photo:
            FileHandler.save_file(
                instance=self,
                file_field_name='main_photo',
                path_function=event_main_photo_path,
            )
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка при сохранении объекта в базе данных: {e}")
            if self.main_photo:
                FileHandler.delete_event_folder(self.slug)
            raise

    def delete(self, *args, **kwargs):
        FileHandler.delete_event_folder(self.slug)
        super().delete(*args, **kwargs)


class EventImages(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='event_images',
        verbose_name='Мероприятие'
    )
    image = models.ImageField(
        upload_to=event_additional_image_path,
        max_length=255,
        validators=[FileExtensionValidator(
            allowed_extensions=['png', 'jpg', 'jpeg'],
            message='Вы можете использовать только файлы с расширениями PNG и JPEG.'
        )],
        verbose_name='Картинки для мероприятия'
    )

    class Meta:
        verbose_name = 'Картинка для мероприятий'
        verbose_name_plural = 'Картинки для мероприятий'

    def save(self, *args, **kwargs):
        delete_old_additional_image(self)
        FileHandler.save_file(
            instance=self,
            file_field_name='image',
            path_function=event_additional_image_path
        )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        FileHandler.delete_event_image_with_folder_cleanup(self.image.name)
        super().delete(*args, **kwargs)
