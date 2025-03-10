from django.db.models.signals import post_save
from django.urls import reverse
from django.dispatch import receiver
from reviewApp.models import Review
from userApp.models import Notification


@receiver(post_save, sender=Review)
def create_notifications_about_review(sender, instance, created, **kwargs):
	"""Сигнал для создания уведомления для организатора мероприятия, если на его мероприятие оставили отзыв."""
	if created:
		if not instance.event:
			raise ValueError('Отзыв не привязан к событию.')
		if not instance.event.organizer:
			raise ValueError('У события нет организатора.')
		url = reverse('review_delete_success')
		try:
			Notification.objects.create(
				user=instance.event.organizer,
				text=f'На ваше мероприятия был оставлен отзыв.',
				url_event=url
			)
		except Exception as e:
			print(f'error: {e}')