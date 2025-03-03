import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule


def setup_periodic_tasks():
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.MINUTES
    )
    PeriodicTask.objects.update_or_create(
        name='send_email_for_users_before_event',
        defaults={
            'interval': schedule,
            'task': 'tasksApp.tasks.send_email_for_users_before_event',
            'args': json.dumps([])
        }
    )
    PeriodicTask.objects.update_or_create(
        name='check_actual_date_event',
        defaults={
            'interval': schedule,
            'task': 'tasksApp.tasks.check_actual_date_event',
            'args': json.dumps([])
        }
    )
