from __future__ import absolute_import, unicode_literals

# Это позволит убедиться, что приложение всегда импортируется, когда запускается Django
from .celery import app as celery

__all__ = ('celery')