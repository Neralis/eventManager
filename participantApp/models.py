from django.utils.timezone import now
from django.db import models, transaction
from django.db.models import Q, Count, QuerySet
from django.core.exceptions import ValidationError
from eventApp.models import Event
from userApp.models import NotAuthUser, CustomUser
from utils.constants.participants_constants import FAVOURITE_PARTICIPANT_THRESHOLD


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

    def clean(self):
        """Валидация данных перед сохранением"""
        if self.user and self.user == self.event.organizer:
            raise ValidationError('Организатор не может зарегистрироваться на свое же мероприятие.')

        if self.event.registration_status and self.user:
            participant_date_birthday = self.user.date_birthday
            today = now().date()
            age = today.year - participant_date_birthday.year
            if (today.month, today.day) < (participant_date_birthday.month, participant_date_birthday.day):
                age -= 1
            if age < self.event.age_limit:
                raise ValidationError('Возрастное ограничение: вы не достигли необходимого возраста.')

        if not self.event.is_active or self.event.date_start < now():
            raise ValidationError('Нельзя зарегистрироваться на прошедшее или уже начавшееся событие.')

        if self.event.available_places <= 0:
            raise ValidationError('Нет свободных мест для регистрации на мероприятие.')

        if self.event.registration_status and self.not_auth_user:
            raise ValidationError(
                'Неавторизованный пользователь не может записаться на мероприятие с обязательной регистрацией.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def is_registered(cls, event: 'Event', user=None, email=None, phone=None) -> bool:
        """Проверяет, зарегистрирован ли пользователь(авторизованный или нет) как участник этого мероприятия."""
        if user:
            return cls.objects.filter(event=event, user=user).exists()
        if email and phone:
            if cls.objects.filter(event=event, user__email=email).exists():
                return True
            return cls.objects.filter(event=event, not_auth_user__email=email, not_auth_user__phone=phone).exists()
        return False

    @classmethod
    def create_participant(cls, event: 'Event', user=None, email=None, phone=None) -> 'Participants':
        """Создает участника для мероприятия. Возвращает созданного участника."""
        if event.available_places <= 0:
            raise ValueError('Свободные места для данного мероприятия закончились.')

        if cls.is_registered(event, user, email, phone):
            raise ValueError('Данный пользователь уже зарегестрирован на данное мероприятие.')

        with transaction.atomic():
            if user:
                participant = cls(event=event, user=user)
            else:
                not_auth_user, _ = NotAuthUser.objects.get_or_create(email=email, phone=phone)
                participant = cls(event=event, not_auth_user=not_auth_user)
            participant.save()
            return participant

    @classmethod
    def get_statistics_favourite_participant(cls, organizer_id: int) -> QuerySet:
        """
        Находит избранных участников для организатора мероприятий.
        Для этого пользователю надо поучаствовать в мероприятиях организатора больше раз,
        чем FAVOURITE_PARTICIPANT_THRESHOLD.
        """

        participants = cls.objects.filter(event__organizer__id=organizer_id)
        favourite_participants = (
            participants
            .values('not_auth_user__email', 'user__email')
            .annotate(registration_count=Count('id'))
            .filter(registration_count__gt=FAVOURITE_PARTICIPANT_THRESHOLD)
        )
        return favourite_participants