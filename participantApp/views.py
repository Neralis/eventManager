from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView
from django.core.exceptions import ValidationError
from eventApp.models import Event
from participantApp.forms import RegistrationParticipantsForm
from participantApp.models import Participants
from participantApp.permissions import OrganizerPermissionMixin


class ListParticipantsOnEvent(OrganizerPermissionMixin, ListView):
    """
    Представление для отображения списка участников для конкретного мероприятия.
    Доступно только организатору мероприятия.
    """

    model = Participants
    template_name = 'participantApp/participants_list.html'
    context_object_name = 'participants'

    def get_instance(self):
        event_id = self.kwargs.get('event_id')
        return event_id

    def get_queryset(self):
        """Возвращает QuerySet участников для мероприятия, указанного в URL."""
        event_id = self.kwargs.get('event_id')
        return Participants.objects.filter(event__id=event_id)

    def get_context_data(self, **kwargs):
        """Передает в контекст данные о мероприятии(id)."""
        context = super().get_context_data(**kwargs)
        context['event_id'] = self.kwargs.get('event_id')
        return context


class DeleteParticipants(OrganizerPermissionMixin, DeleteView):
    """
    Представление для удаления участников для конкретного мероприятия.
    Доступно только организатору мероприятия.
    """

    model = Participants
    template_name = 'participantApp/delete_participants_confirm.html'

    def get_object(self, queryset=None):
        """Возвращает участника для удаления или вызывает 404, если участник не найден."""
        event_id = self.kwargs.get('event_id')
        participant_id = self.kwargs.get('participant_id')
        return get_object_or_404(Participants, id=participant_id, event__id=event_id)

    def get_success_url(self):
        event_id = self.kwargs['event_id']
        return reverse_lazy('participants_list', kwargs={'event_id': event_id})


class RegistrationParticipantsView(CreateView):
    """
    Представление для регистрации участников на мероприятие.
    Поддерживает регистрацию как авторизованных, так и неавторизованных пользователей.
    """

    model = Participants
    form_class = RegistrationParticipantsForm
    template_name = 'participantApp/register_participants.html'

    def get_instance(self):
        event_id = self.kwargs.get('event_id')
        return event_id

    def get_form_kwargs(self):
        """Передает текущего пользователя и мероприятие в форму."""
        kwargs = super().get_form_kwargs()
        if not self.request.user.is_authenticated:
            kwargs['user'] = None
        else:
            kwargs['user'] = self.request.user
        kwargs['event'] = get_object_or_404(Event, id=self.kwargs['event_id'])
        return kwargs

    def form_valid(self, form):
        """Обрабатывает успешную отправку формы. Создает участника мероприятия."""
        event = form.event
        try:
            participant = Participants.create_participant(
                event=event,
                user=self.request.user if self.request.user.is_authenticated else None,
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
            )
            form.instance = participant
            return HttpResponseRedirect(self.get_success_url())
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        except ValueError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Обнаружена ошибка {error}')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Передает в контекст данные о мероприятии."""
        context = super().get_context_data(**kwargs)
        context['event'] = get_object_or_404(Event, id=self.kwargs['event_id'])
        return context

    def get_success_url(self):
        """Перенаправляет на страничку ..."""
        return reverse_lazy('register_participant', kwargs={'event_id': self.get_instance()})


class FavouriteParticipants(OrganizerPermissionMixin, ListView):
    """Отображает список избранных участников для организатора."""
    model = Participants
    template_name = 'participantApp/favourite_participants.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        """Добавляет список избранных участников в контекст шаблона."""
        context = super().get_context_data(**kwargs)
        context['favourite'] = Participants.get_statistics_favourite_participant(self.request.user.id)
        return context