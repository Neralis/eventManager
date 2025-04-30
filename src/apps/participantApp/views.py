import logging

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView
from django.core.exceptions import ValidationError

from src.apps.eventApp.models import Event
from src.apps.participantApp.forms import RegistrationParticipantsForm
from src.apps.participantApp.models import Participants
from src.utils.utils import user_is_authenticated
from src.utils.mixins import EventMixin
from src.utils.permissions import OnlyOrganizer

logger = logging.getLogger(__name__)


class ListParticipantsOnEvent(OnlyOrganizer, EventMixin, ListView):
    """
    Представление для отображения списка участников для конкретного мероприятия.
    Доступно только организатору мероприятия.
    """

    model = Participants
    template_name = 'participantApp/participants_list.html'
    context_object_name = 'participants'

    def get_event_for_permission(self):
        """Возвращает мероприятие или None для проверки прав."""
        return self.get_event()

    def get_queryset(self):
        """Возвращает QuerySet участников для мероприятия, указанного в URL."""
        return Participants.objects.filter(event=self.get_event()).select_related('user')

    def get_context_data(self, **kwargs):
        """Передает в контекст данные о мероприятии."""
        context = super().get_context_data(**kwargs)
        context['event'] = self.get_event()
        return context


class DeleteParticipants(OnlyOrganizer, EventMixin, DeleteView):
    """
    Представление для удаления участников для конкретного мероприятия.
    Доступно только организатору мероприятия.
    """

    model = Participants
    template_name = 'participantApp/delete_participants_confirm.html'

    def get_event_for_permission(self):
        """Возвращает мероприятие или None для проверки прав."""
        return self.get_event()

    def get_object(self, queryset=None):
        """Возвращает участника для удаления или вызывает 404, если участник не найден."""
        participant_id = self.kwargs.get('participant_id')
        return get_object_or_404(Participants, id=participant_id, event=self.get_event())

    def get_success_url(self):
        return reverse_lazy('participants_list', kwargs={'event_id': self.get_event_id()})


class RegistrationParticipantsView(EventMixin, CreateView):
    """
    Представление для регистрации участников на мероприятие.
    Поддерживает регистрацию как авторизованных, так и неавторизованных пользователей.
    """

    model = Participants
    form_class = RegistrationParticipantsForm
    template_name = 'participantApp/register_participants.html'

    def get_event(self):
        """Метод из миксина для получения мероприятия, оптимизирован для получения данных об организаторе."""
        return get_object_or_404(Event.objects.select_related('organizer'), id=self.get_event_id())

    def get_form_kwargs(self):
        """Передает текущего пользователя и мероприятие в форму."""
        kwargs = super().get_form_kwargs()
        if not user_is_authenticated(self.request):
            kwargs['user'] = None
        else:
            kwargs['user'] = self.request.user
        kwargs['event'] = self.get_event()
        return kwargs

    def form_valid(self, form):
        """Обрабатывает успешную отправку формы. Создает участника мероприятия."""
        event = form.event
        try:
            participant = Participants.create_participant(
                event=event,
                user=self.request.user if user_is_authenticated(self.request) else None,
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
            )
            form.instance = participant
            return redirect(self.get_success_url())
        except (ValidationError, ValueError) as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        """Передает в контекст данные о мероприятии."""
        context = super().get_context_data(**kwargs)
        context['event'] = self.get_event()
        return context

    def get_success_url(self):
        """Перенаправляет на страничку ..."""
        return reverse_lazy('event_detail', kwargs={'event_id': self.get_event_id()})


class FavouriteParticipants(OnlyOrganizer, ListView):
    """Отображает список избранных участников для организатора."""
    model = Participants
    template_name = 'participantApp/favourite_participants.html'
    paginate_by = 20

    def get_event_for_permission(self):
        """Возвращает мероприятие или None для проверки прав."""
        return None

    def get_context_data(self, **kwargs):
        """Добавляет список избранных участников в контекст шаблона."""
        context = super().get_context_data(**kwargs)
        context['favourite'] = Participants.get_statistics_favourite_participant(self.request.user.id)
        return context