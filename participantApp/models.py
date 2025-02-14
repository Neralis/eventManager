from django.db import models
from django.db.models import Q
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
