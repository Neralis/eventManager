from django.db.models.signals import post_save
from django.urls import reverse
from django.dispatch import receiver
from reviewApp.models import Review
from userApp.models import Notification


@receiver(post_save, sender=Review)
def create_notifications_about_review(sender, instance, created, **kwargs):
	if created:
		if not instance.event:
			print('Отзыв не привязан к событию')
			return
		if not instance.event.organizer:
			print('У события нет организатора')
			return
		url = reverse('review_delete_success')
		try:
			Notification.objects.create(
				user=instance.event.organizer,
				text=f'На ваше мероприятия был оставлен отзыв',
				url_event=url
			)
			print('Успешно создано уведомление')
		except Exception as e:
			print(f'error: {e}')