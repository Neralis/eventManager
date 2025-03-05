from django.db import models
from django.db.models import Q
from eventApp.models import Event
from userApp.models import NotAuthUser, CustomUser


class Participants(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name='Мероприятие'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name='participants',
        blank=True,
        null=True,
        verbose_name='Авторизованный пользователь'
    )
    not_auth_user = models.ForeignKey(
        NotAuthUser,
        on_delete=models.SET_NULL,
        related_name='participants',
        blank=True,
        null=True,
        verbose_name='Неавторизованный пользователь'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время регистрации на мероприятие'
    )

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'
        constraints = [
            models.CheckConstraint(
                check=(
                        (Q(user__isnull=True) & Q(not_auth_user__isnull=False)) |
                        (Q(user__isnull=False) & Q(not_auth_user__isnull=True))
                ),
                name='check_user_and_not_auth_user'
            ),
            models.UniqueConstraint(
                fields=('user', 'event'),
                name='unique_user_on_vent'
            ),
            models.UniqueConstraint(
                fields=('not_auth_user', 'event'),
                name='unique_not_auth_user_on_event'
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

