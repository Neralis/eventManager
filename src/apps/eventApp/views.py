from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, FormView, ListView, UpdateView, CreateView, DetailView
from django.db import transaction

from src.apps.eventApp.models import Event, EventImages, Category
from src.apps.eventApp.forms import ReasonForDeleteEventForm, EventForm
from src.apps.tasksApp.tasks import send_mail_with_reason_task
from src.utils.mixins import EventMixin
from src.apps.eventApp.utils import search_event
from src.utils.permissions import OwnerPermission


class ReasonForDeleteEventView(EventMixin, FormView):
    """Представление для обработки формы ReasonForDeleteEventForm и удаления мероприятия."""
    form_class = ReasonForDeleteEventForm
    template_name = 'eventApp/reason_form.html'
    success_url = reverse_lazy('event_list')

    def form_valid(self, form):
        event = self.get_event()
        reason = form.cleaned_data['reason']
        email_list = [participant.get_email() for participant in event.participants.all()]
        event_title = event.title
        event.delete()
        send_mail_with_reason_task.delay(email_list, event_title, reason)
        return super().form_valid(form)


class DeleteEventView(OwnerPermission, DeleteView):
    model = Event
    template_name = 'eventApp/event_delete.html'
    pk_url_kwarg = 'event_id'

    def get(self, request, *args, **kwargs):
        event = self.get_object()
        if event.is_active and event.participants.exists():
            return redirect('reason_for_delete_event', event_id=event.id)
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('event_list')


# -----------------------------


class EventListView(EventMixin, ListView):
    model = Event
    template_name = 'eventApp/event_list.html'
    paginate_by = 20

    def get_queryset(self):
        """
        Сортировка и фильтрация. Сортировка происходит по среднему рейтингу пользователей,
        чем выше рейтинг организатора(пользователя), тем выше он будет в итоговой выдаче.
        """

        queryset = super().get_queryset()
        queryset = self.queryset_filter(queryset)
        queryset = queryset.select_related('organizer__profile'
                                           ).order_by('-organizer__profile__average_rating', '-date_start')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['cities'] = Event.objects.exclude(city="").values_list("city", flat=True).distinct()
        context['event_count'] = self.get_queryset().count()
        return context


class EventDetailView(DetailView):
    model = Event
    template_name = 'eventApp/event_detail.html'
    pk_url_kwarg = 'event_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['count_place'] = self.object.available_places
        context['event_images'] = self.object.event_images.all()  # Это QuerySet изображений
        context['organizer_phone'] = self.object.organizer.phone
        context['organizer_events'] = Event.objects.filter(organizer=self.object.organizer
                                                           ).exclude(id=self.object.id)[:6]
        context['reviews'] = self.object.reviews.all()
        context['similiar_events'] = Event.objects.filter(category__in=self.object.category.all()
                                                          ).exclude(id=self.object.id).distinct()[:6]

        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'eventApp/event_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = form.save(commit=False)
                self.object.organizer = self.request.user
                self.object.save()

                images = self.request.FILES.getlist('event_images')
                for image in images:
                    self.object.images.create(image=image)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'event_id': self.object.pk})


class EventUpdateView(OwnerPermission, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'eventApp/event_update.html'
    pk_url_kwarg = 'event_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['images'] = EventImages.objects.filter(event=self.object)
        return context

    def form_valid(self, form):
        images = self.request.FILES.getlist('event_images')
        try:
            for image in images:
                EventImages.objects.create(event=self.object, image=image)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'event_id': self.object.pk})

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class SearchResultView(EventMixin, ListView):
    model = Event
    template_name = 'eventApp/event_search.html'
    context_object_name = 'event_list'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q')
        queryset = search_event(query) if query else Event.objects.all()
        queryset = self.queryset_filter(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['cities'] = Event.objects.exclude(city="").values_list("city", flat=True).distinct()
        context['event_count'] = self.get_queryset().count()
        return context
