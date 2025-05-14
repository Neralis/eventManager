from abc import abstractmethod
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import DeleteView, FormView


class OnlyOrganizer(LoginRequiredMixin):
    """
    Миксин для проверки, что текущий пользователь является организатором мероприятия.
    Предназначен для работы со связными сущностями Event:
        - Participant
        - Review
    """

    def dispatch(self, request, *args, **kwargs):
        allowed_methods = ['GET', 'DELETE']
        if isinstance(self, DeleteView) or isinstance(self, FormView):
            allowed_methods.append('POST')
        if request.method not in allowed_methods:
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
