from django.core.exceptions import PermissionDenied
from src.apps.eventApp.models import Event


class OrganizerPermissionMixin:
    def dispatch(self, request, *args, **kwargs):
        """
        Проверка прав пользователя.
        Он должен быть организатором мероприятия, чтобы взаимодействовать c участниками этого мероприятия:
            - просматривать
            - удалять
            - получать статистику участников
        """

        event_id = kwargs.get('event_id')
        if event_id is not None:
            try:
                event = Event.objects.get(id=event_id)
            except:
                raise PermissionDenied(f'Такое события (id={event_id}) не найдено.')

            if event.organizer != request.user:
                raise PermissionDenied('Только организатор имеет на это право.')
        return super().dispatch(request, *args, **kwargs)

