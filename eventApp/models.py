from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import os
import shutil

from django.conf import settings
from unidecode import unidecode
from django.db import models
from django.db.models import Q, F, SET_DEFAULT
from django.db.models.functions import Now
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFit
from eventApp.utils import get_random_string
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


def event_main_photo_path(instance, filename):
    """Динамический путь для основного фото мероприятия"""
    # Убедимся, что у instance есть ID
    if not instance.id:
        # Если ID нет, сохраним объект, чтобы получить ID
        instance.save()
    return f'events/{instance.id}/main_photo/{filename}'

def event_additional_image_path(instance, filename):
    """Динамический путь для дополнительных изображений"""
    # Убедимся, что у event есть ID
    if not instance.event_id:
        # Если у связанного события нет ID, сохраним его
        instance.event.save()
    return f'events/{instance.event.id}/additional_images/{filename}'

class ActivityEventManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return (super().get_queryset(*args, **kwargs).
                filter(Q(date_start__lte=Now()) & Q(date_end__gte=Now())))


def get_default_organizer():
    return CustomUser.objects.get(username='default_remove_user').id



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
        null=True,
        verbose_name='Место проведения мероприятия оффлайн'
    )
    city = models.CharField(
        max_length=300,
        blank=True,
        null=True,
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
        upload_to = event_main_photo_path,
        processors=[ResizeToFit(800, 600)],
        format='JPEG',
        options={'quality': 70},
        blank=True,
        verbose_name='Фото для обложки'
    )

    objects = models.Manager()
    active = ActivityEventManager()

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
                        (Q(location_offline__isnull=True) & Q(location_online__isnull=False)) |
                        (Q(location_offline__isnull=False) & Q(location_online__isnull=True))
                ),
                name='check_location'
            )
        ]

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        baseslug = slugify(unidecode(self.title))
        if not self.slug or not self.slug.startswith(baseslug):
            slug = f'{baseslug}-{get_random_string()}'
            while Event.objects.filter(slug=slug).exists():
                slug = f'{baseslug}-{get_random_string()}'
            self.slug = slug

        # Сохранение объекта для получения ID (без main_photo)
        if self.main_photo:
            temp_photo = self.main_photo
            self.main_photo = None
            super().save(*args, **kwargs)
            self.main_photo = temp_photo
        else:
            super().save(*args, **kwargs)

        # Создание каталога после сохранения объекта
        event_dir = os.path.join(settings.MEDIA_ROOT, f'events/{self.id}')
        main_photo_dir = os.path.join(event_dir, 'main_photo')
        additional_images_dir = os.path.join(event_dir, 'additional_images')

        os.makedirs(main_photo_dir, exist_ok=True)
        os.makedirs(additional_images_dir, exist_ok=True)

        if self.main_photo:
            super().save(*args, **kwargs)

    # Удаление каталога мероприятия перед удалением объекта
    def delete(self, *args, **kwargs):
        event_dir = os.path.join(settings.MEDIA_ROOT, f'events/{self.id}')
        if os.path.exists(event_dir):
            shutil.rmtree(event_dir)
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


    # def save(self, *args, **kwargs):
    #     # Проверка, что связанное событие сохранено и имеет ID
    #     if not self.event_id:
    #         self.event.save()
    #     # Создадим каталоги, если они ещё не существуют
    #     event_dir = os.path.join(settings.MEDIA_ROOT, f'events/{self.event.id}')
    #     additional_images_dir = os.path.join(event_dir, 'additional_images')
    #     os.makedirs(additional_images_dir, exist_ok=True)
    #     super().save(*args, **kwargs)
