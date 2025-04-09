from abc import abstractmethod
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class OnlyOrganizer(LoginRequiredMixin):
    """
    Миксин для проверки, что текущий пользователь является организатором мероприятия.
    Предназначен для работы со связными сущностями Event:
        - Participant
        - Review
    """

    def dispatch(self, request, *args, **kwargs):
        if request.method not in ['GET', 'DELETE']:
            raise PermissionDenied('Другие операции не доступны')
        event = self.get_event_for_permission()
        if event and request.user != event.organizer:
            raise PermissionDenied('Только организатор мероприятия имеет на это право')
        return super().dispatch(request, *args, **kwargs)

    @abstractmethod
    def get_event_for_permission(self):
        """Метод должен возвращать объект Event или None."""
        pass


class OwnerPermission(LoginRequiredMixin):
    """Миксин для проверки, что только владелец мероприятия может изменять его данные."""
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.organizer != request.user:
            raise PermissionDenied('Только организатор мероприятия имеет на это право')
        return super().dispatch(request, *args, **kwargs)
