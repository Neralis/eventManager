from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils.timezone import now
from eventApp.models import Event

