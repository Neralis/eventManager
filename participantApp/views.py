from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView
from .forms import RegistrationParticipantsForm
from .models import NotAuthUser, Event, Participants
from .permissions import OrganizerPermissionMixin


class ListParticipantsOnEvent(OrganizerPermissionMixin, ListView):
    model = Participants
    template_name = 'participantApp/participants_list.html'
    context_object_name = 'participants'

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return Participants.objects.filter(event__id=event_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_id'] = self.kwargs.get('event_id')
        return context


class DeleteParticipants(OrganizerPermissionMixin, DeleteView):
    model = Participants
    template_name = 'participantApp/delete_participants_confirm.html'

    def get_object(self, queryset=None):
        event_id = self.kwargs.get('event_id')
        participant_id = self.kwargs.get('participant_id')
        return get_object_or_404(Participants, id=participant_id, event__id=event_id)

    def get_success_url(self):
        event_id = self.kwargs['event_id']
        return reverse_lazy('participants_list', kwargs={'event_id': event_id})


class RegistrationParticipantsView(CreateView):
    model = Participants
    form_class = RegistrationParticipantsForm
    template_name = 'participantApp/register_participants.html'
    success_url = reverse_lazy('index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not self.request.user.is_authenticated:
            kwargs['user'] = None
        else:
            kwargs['user'] = self.request.user
        event = get_object_or_404(Event, id=self.kwargs['event_id'])
        kwargs['event'] = event
        return kwargs

    def form_valid(self, form):
        event = form.event

        if event.available_places <= 0:
            form.add_error(None,  'Места дла данного мероприятия закончились')
            return self.form_invalid(form)

        form.instance.event = event

        with transaction.atomic():
            if self.request.user.is_authenticated:
                form.instance.user = self.request.user
            else:
                email = form.cleaned_data.get('email')
                phone = form.cleaned_data.get('phone')

                not_auth_user, _ = NotAuthUser.objects.get_or_create(email=email, phone=phone)
                form.instance.not_auth_user = not_auth_user

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = Event.objects.get(id=self.kwargs['event_id'])
        return context


class FavouriteParticipants(OrganizerPermissionMixin, ListView):
    model = Participants
    template_name = 'participantApp/favourite_participants.html'
    paginate_by = 20

    def get_statistics_favourite_participant(self):
        participants = Participants.objects.filter(event__organizer=self.request.user)
        favourite_participants = (
            participants
            .values('not_auth_user__email', 'user__email')
            .annotate(registration_count=Count('id'))
            .filter(registration_count__gt=3)
        )
        return favourite_participants

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favourite'] = self.get_statistics_favourite_participant()
        return context


def index(request):
    return HttpResponse('sex')








