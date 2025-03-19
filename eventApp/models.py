from django.db import models
from django.db.models import Q, F, SET_DEFAULT
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFit
from eventApp.utils import get_default_organizer, event_main_photo_path, generate_unique_slug, \
    update_available_places_from_participants_limit, delete_old_main_image, move_event_directory, \
    delete_event_directory, event_additional_image_path, delete_old_additional_image, move_event_image_directory, \
    delete_event_image_file
from userApp.models import CustomUser


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
        verbose_name='Описание меропрития'
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
        default=get_default_organizer,
        on_delete=SET_DEFAULT,
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

    main_photo = ProcessedImageField(
        upload_to=event_main_photo_path,
        processors=[ResizeToFit(800, 600)],
        format='JPEG',
        options={'quality': 70},
        blank=True,
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
        delete_old_main_image(self)
        super().save(*args, **kwargs)
        move_event_directory(self)

    def delete(self, *args, **kwargs):
        delete_event_directory(self)
        super().delete(*args, **kwargs)


class EventImages(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='event_images',
        verbose_name='Мероприятие'
    )
    image = ProcessedImageField(
        upload_to=event_additional_image_path,
        processors=[ResizeToFit(800, 600)],
        format='JPEG',
        options={'quality': 70},
        verbose_name='Картинки для мероприятия'
    )

    class Meta:
        verbose_name = 'Картинка для мероприятий'
        verbose_name_plural = 'Картинки для мероприятий'

    def save(self, *args, **kwargs):
        delete_old_additional_image(self)
        super().save(*args, **kwargs)
        move_event_image_directory(self)

    def delete(self, *args, **kwargs):
        delete_event_image_file(self)
        super().delete(*args, **kwargs)
