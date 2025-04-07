from django.db import models
from src.apps.eventApp.models import Event
from src.apps.participantApp.models import Participants


class Review(models.Model):
    participant = models.OneToOneField(
        Participants,
        on_delete=models.CASCADE,
        verbose_name='Участник'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Мероприятие'
    )
    text = models.TextField(
        blank=True,
        verbose_name='Текст отзыва'
    )
    rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Оценка мероприятия'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        indexes = [
            models.Index(fields=['event']),
        ]

    def __str__(self):
        return f'{self.participant} оставил комментарий на {self.event.title}'

    @classmethod
    def get_participant(cls, event: 'Event', email: str) -> 'Participants':
        """Проверяет, есть ли действительно такой участник."""
        try:
            participant = Participants.objects.get(event=event, user__email=email)
        except Participants.DoesNotExist:
            try:
                participant = Participants.objects.get(event=event, not_auth_user__email=email)
            except Participants.DoesNotExist:
                raise ValueError('Вы не зарегистрированы как участник этого мероприятия')
        return participant

    @classmethod
    def create_review(cls, event: 'Event', participant: 'Participants', text: str, rating: int) -> 'Review':
        """Создает отзыв и проверяет наличие отзыва для данного мероприятия от этого участника"""
        if cls.objects.filter(event=event, participant=participant).exists():
            raise ValueError('Вы уже оставили отзыв на это мероприятие')
        else:
            review = cls(event=event, participant=participant, text=text, rating=rating)
            review.save()
            return review
