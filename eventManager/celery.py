from __future__ import absolute_import
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventManager.settings')

app = Celery("eventManager")
app.config_from_object('django.conf:settings', namespace='CELERY')
print(f"Using broker: {app.conf.broker_url}")
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
