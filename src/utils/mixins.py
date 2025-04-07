from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from src.apps.eventApp.models import Event


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

    def queryset_filter(self, queryset):
        """Метод для фильтрации queryset."""
        event_format = self.request.GET.get('event_format')
        if event_format in ["Online", "Offline"]:
            queryset = queryset.filter(event_format=event_format)

        date_start = self.request.GET.get('date_start')
        if date_start:
            parsed_date = parse_date(date_start)  # Преобразуем строку в дату
            if parsed_date:
                queryset = queryset.filter(date_start__date=parsed_date)

        category_id = self.request.GET.get("category")
        if category_id:
            try:
                category_id = int(category_id)  # Преобразуем строку в число
                queryset = queryset.filter(category=category_id)  # category вместо category_id
            except (TypeError, ValueError):
                pass

        city = self.request.GET.get("city")
        if city and city != "all":  # Если city не "all", применяем фильтр
            queryset = queryset.filter(city=city)

        return queryset