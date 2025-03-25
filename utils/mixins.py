from django.shortcuts import get_object_or_404
from eventApp.models import Event


class EventMixin:
    """Миксин для методов, связанных с Event."""
    def get_event_id(self):
        """Метод для получения id мероприятия из URL."""
        event_id = self.kwargs.get('event_id')
        if event_id is None:
            raise ValueError('ID мероприятия отсутствует в URL параметрах')
        return event_id

    def get_event(self):
        """Метод для получения объекта Event по id."""
        return get_object_or_404(Event, id=self.get_event_id())