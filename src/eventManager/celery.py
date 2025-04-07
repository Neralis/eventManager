from __future__ import absolute_import
import os
import sys
import django
from celery import Celery

sys.path.append('/app')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.eventManager.settings')

app = Celery("eventManager")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

django.setup()

app.autodiscover_tasks(['src.apps.tasksApp'])


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
