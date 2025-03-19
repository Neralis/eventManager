from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DeleteView
from eventApp.models import Event
from reviewApp.models import Review
from tasksApp.utils import validate_token
from userApp.models import CustomUser
from reviewApp.forms import ReviewCreateForm


class ReviewListView(ListView):
    model = Review
    paginate_by = 8
    template_name = 'reviewApp/review_list.html'

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(CustomUser, id=user_id)  # Находим пользователя или выдаём 404, если его нет
        events = Event.objects.filter(organizer=user)  # Получаем все события, организованные этим пользователем

        return (Review.objects.filter(event__in=events)
                .select_related('participant__user', 'participant__not_auth_user'))  # Фильтруем отзывы по этим событиям


class ReviewListViewOnEvent(ListView):
    model = Review
    paginate_by = 8
    template_name = 'reviewApp/review_list_on_event.html'

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, id=event_id)

        return Review.objects.filter(event=event).select_related('participant__user', 'participant__not_auth_user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, id=event_id)
        context['event'] = event  # Добавляем объект event в контекст
        return context


class ReviewCreateView(CreateView):
    model = Review
    form_class = ReviewCreateForm
    template_name = 'reviewApp/review_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        email, event_id = validate_token(self.kwargs['token'])
        self.event = get_object_or_404(Event, id=event_id)
        kwargs['event'] = self.event
        kwargs['email'] = email
        return kwargs

    def form_valid(self, form):
        event = form.event
        email = form.email
        try:
            participant = Review.get_participant(event, email)
            try:
                review = Review.create_review(
                    event=event,
                    participant=participant,
                    text=form.cleaned_data['text'],
                    rating=form.cleaned_data['rating'],
                )
                form.instance = review
                return HttpResponseRedirect(self.get_success_url())
            except ValidationError as e:
                form.add_error(None, e)
                return self.form_invalid(form)
            except ValueError as e:
                form.add_error(None, str(e))
                return self.form_invalid(form)
        except ValueError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context

    def get_success_url(self):
        return reverse_lazy('success')


class ReviewDeleteView(DeleteView):
    model = Review
    success_url = reverse_lazy('success')


def index(request):
    return HttpResponse("SUCCESS")
