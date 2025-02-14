from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.timezone import now
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    otchestvo = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    date_birthday = models.DateField(
        blank=True,
        null=True
    )
    phone = PhoneNumberField(unique=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_users",
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_users_permissions",
        blank=True,
    )

    def __str__(self):
        return f'({self.username}) {self.first_name} {self.last_name} {self.email}'


@receiver(pre_delete, sender=CustomUser)
def block_delete_user(sender, instance, **kwargs):
    from eventApp.models import Event

    events = Event.objects.filter(
        organizer=instance,
        date_start__lte=now(),
        date_end__gte=now()
    )
    if events.exists():
        raise Exception('Пользователь с активными мероприятиями не может быть удален')


@receiver(pre_delete, sender=CustomUser)
def delete_users_events_(sender, instance, **kwargs):
    from eventApp.models import Event

    events = Event.objects.filter(
        organizer=instance,
        date_start__gt=now()
    )
    events.delete()


class NotAuthUser(models.Model):
    email = models.EmailField()
    phone = PhoneNumberField()

    class Meta:
        indexes = [
            models.Index(fields=['email']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'phone'],
                name='unique_email_phone'
            )
        ]

    def __str__(self):
        return self.email
