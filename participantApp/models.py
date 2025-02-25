from django.core.mail import send_mail
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from eventApp.models import *
from eventApp.models import Event
from userApp.models import NotAuthUser


class Participants(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name='participants',
        blank=True,
        null=True
    )
    not_auth_user = models.ForeignKey(
        NotAuthUser,
        on_delete=models.SET_NULL,
        related_name='participants',
        blank=True,
        null=True
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                        (Q(user__isnull=True) & Q(not_auth_user__isnull=False)) |
                        (Q(user__isnull=False) & Q(not_auth_user__isnull=True))
                ),
                name='check_user_and_not_auth_user'
            )
        ]

    def __str__(self):
        if self.user:
            return f'{self.user.first_name} {self.user.last_name}'
        return self.not_auth_user.email

    def get_email(self):
        if self.user:
            return self.user.email
        return self.not_auth_user.email


@receiver(post_save, sender=Participants)
def registration_on_event(sender, instance, **kwargs):
    send_mail(
        f'Вы зарегестрировались на мероприятие {instance.title}',
        'Спасибо за вашу активность!',
        'example@gmail.com',
        [instance.get_email()],
        fail_silently=False,
    )