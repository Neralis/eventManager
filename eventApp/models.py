from django.db import models
from django.db.models import Q, F, SET_DEFAULT, SET_NULL
from django.db.models.functions import Now
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFit
from userApp.models import CustomUser


class Category(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title

class ActivityEventManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(Q(date_start__lte=Now()) & Q(date_end__gte=Now()))

# def get_default_organizer():
#    return CustomUser.objects.get_or_create(username="пустой профиль")[0].email

class Event(models.Model):
    EVENT_FORMAT = [
        ('Online', 'Онлайн'),
        ('Offline', 'Оффлайн'),
    ]

    title = models.CharField(max_length=250)
    category = models.ManyToManyField(Category, related_name='events')
    description = models.TextField()
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    organizer = models.ForeignKey(CustomUser, blank=True, on_delete=SET_NULL, null=True,related_name='events')

    format = models.CharField(max_length=7, choices=EVENT_FORMAT)
    registration_status = models.BooleanField(default=False)

    participants_limit = models.PositiveIntegerField(default=1)
    age_limit = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=300)

    main_photo = ProcessedImageField(upload_to='main_images/', processors=[ResizeToFit(800, 600)],
                             format='JPEG', options={'quality': 70})

    objects = models.Manager()
    active = ActivityEventManager()

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['date_start', 'date_end']),
        ]
        constraints = [
            models.CheckConstraint(check=Q(date_end__gt=F('date_start')), name='check_data')
        ]

    def __str__(self):
        return f'{self.title} {self.registration_status}'

    @property
    def activity_status(self):
        if self.date_end and self.date_end < Now():
            return 'завершенно'
        return 'актуально'


class EventImages(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_images')
    image = ProcessedImageField(upload_to='images/', processors=[ResizeToFit(800, 600)],
                             format='JPEG', options={'quality': 70})


