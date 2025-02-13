from django.db import models
from eventApp.models import Event
from participantApp.models import Participants


class Review(models.Model):
    participant = models.OneToOneField(
        Participants,
        on_delete=models.CASCADE
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField(blank=True)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])

    def __str__(self):
        return f'{self.participant} оставил комментарий на {self.event.title}'
