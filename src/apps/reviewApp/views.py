from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView
from src.apps.eventApp.models import Event
from src.apps.reviewApp.models import Review
from src.apps.reviewApp.utils import validate_token_for_review
from src.apps.reviewApp.forms import ReviewCreateForm
from src.utils.mixins import EventMixin
from src.utils.permissions import OnlyOrganizer


class ReviewListView(OnlyOrganizer, ListView):
    """
    Представление для отображения списка всех комментариев для организатора.
    """

    model = Review
    paginate_by = 8
    template_name = 'reviewApp/review_list.html'

    def get_event_for_permission(self):
        """Возвращает мероприятие или None для проверки прав."""
        return None

    def get_queryset(self):
        return (Review.objects.filter(event__organizer=self.request.user)
                .select_related('participant__user', 'participant__not_auth_user'))  # Фильтруем отзывы по этим событиям


class ReviewListViewOnEvent(OnlyOrganizer, EventMixin, ListView):
    model = Review
    paginate_by = 8
    template_name = 'reviewApp/review_list_on_event.html'

    def get_event_for_permission(self):
        """Возвращает мероприятие или None для проверки прав."""
        return self.get_event()

    def get_queryset(self):
        return Review.objects.filter(event=self.get_event()
                                     ).select_related('participant__user', 'participant__not_auth_user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.get_event()
        return context


class ReviewCreateView(CreateView):
    model = Review
    form_class = ReviewCreateForm
    template_name = 'reviewApp/review_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        email, event_id = validate_token_for_review(self.kwargs['token'])
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
                return redirect(self.get_success_url())
            except (ValidationError, ValueError) as e:
                form.add_error(None, e)
                return self.form_invalid(form)
        except ValueError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context

    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'event_id': self.event.id})


class ReviewDeleteView(OnlyOrganizer, DeleteView):
    model = Review
    pk_url_kwarg = 'review_id'

    def get_event_for_permission(self):
        """Возвращает мероприятие или None для проверки прав."""
        review_id = self.kwargs.get('review_id')
        self.event = get_object_or_404(Review, id=review_id).event
        return self.event

    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'event_id': self.event.id})