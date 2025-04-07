from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, FormView, ListView, UpdateView, CreateView, DetailView
from src.apps.eventApp.models import Event, EventImages, Category
from src.apps.eventApp.forms import ReasonForDeleteEventForm, EventForm
from src.apps.tasksApp.tasks import send_mail_with_reason_task
from src.utils.mixins import EventMixin
from src.apps.eventApp.utils import search_event


class ReasonForDeleteEventView(EventMixin, FormView):
    """Представление для обработки формы ReasonForDeleteEventForm и удаления мероприятия."""
    form_class = ReasonForDeleteEventForm
    template_name = 'eventApp/reason_form.html'
    success_url = reverse_lazy('success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.event = self.get_event()
        context['event'] = self.event
        return context

    def form_valid(self, form):
        reason = form.cleaned_data['reason']
        email_list = [participant.get_email() for participant in self.event.participants.all()]
        event_title = self.event.title
        self.event.delete()
        send_mail_with_reason_task.delay(email_list, event_title, reason)
        return super().form_valid(form)


class DeleteEventView(DeleteView):
    model = Event
    template_name = 'eventApp/event_delete.html'
    pk_url_kwarg = 'event_id'

    def delete(self, request, *args, **kwargs):
        event = self.get_object()
        if event.is_active:
            return redirect('reason_for_delete_event', event_id=event.id)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('event_list')


# -----------------------------


class EventListView(EventMixin, ListView):
    model = Event
    template_name = 'eventApp/event_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.queryset_filter(queryset)
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
                                                          ).exclude(id=self.object.id)[:6]

        return context


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'eventApp/event_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        # context['event_format'] = self.request.POST.get('event_format', 'Offline')  # что за хуйня?
        return context

    def form_valid(self, form):
        images = self.request.FILES.getlist('event_images')
        try:
            for image in images:
                EventImages.objects.create(event=self.object, image=image)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        return self.form_valid(form)

    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'event_id': self.object.pk})


class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'eventApp/event_update.html'
    pk_url_kwarg = 'event_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        # context['event_format'] = self.request.POST.get('event_format', 'Offline')  # опять же, что за хуйня?
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
        query = self.request.GET.get('query')
        queryset = search_event(query) if query else Event.objects.all()
        queryset = self.queryset_filter(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['cities'] = Event.objects.exclude(city="").values_list("city", flat=True).distinct()
        context['event_count'] = self.get_queryset().count()
        return context
