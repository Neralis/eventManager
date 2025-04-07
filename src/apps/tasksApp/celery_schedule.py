import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule


def setup_short_periodic_tasks() -> None:
    """
    Регистрация временного интервала в 3 минуты для celery-функций.
    Добавляем временной интервал для функций:
        - send_email_for_participants_before_event,
        - check_actual_date_event
    """

    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=3,
        period=IntervalSchedule.MINUTES
    )
    PeriodicTask.objects.update_or_create(
        name='send_email_for_participants_before_event',
        defaults={
            'interval': schedule,
            'task': 'src.apps.tasksApp.tasks.send_email_for_participants_before_event',
            'args': json.dumps([])
        }
    )
    PeriodicTask.objects.update_or_create(
        name='check_actual_date_event',
        defaults={
            'interval': schedule,
            'task': 'src.apps.tasksApp.tasks.check_actual_date_event',
            'args': json.dumps([])
        }
    )


def setup_daily_tasks() -> None:
    """
    Регистрация временного интервала в 1 день для celery-функций.
    Добавляем временной интервал для функций:
        - remove_notifications
    """

    schedule_day, _ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.DAYS
    )
    PeriodicTask.objects.update_or_create(
        name='remove_notifications',
        defaults={
            'interval': schedule_day,
            'task': 'src.apps.tasksApp.tasks.remove_notifications',
            'args': json.dumps([])
        }
    )


def setup_periodic_tasks() -> None:
    setup_short_periodic_tasks()
    setup_daily_tasks()