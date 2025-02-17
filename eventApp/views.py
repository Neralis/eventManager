from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView
from .models import Event

# Create your views here.
class EventListView(ListView):
    model = Event
    template_name = 'event_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context['event_count'] = Event.objects.count()


        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'event_detail.html'

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)

        context['count_place'] = self.object.participants_limit - self.object.participants.count()
        return context

class EventCreateView(CreateView):
    model = Event
    fields = ['title', 'category', 'event_format', 'participants_limit', 'registration_status', 'age_limit',
              'date_start', 'date_end', 'location_offline', 'location_online', 'description', 'main_photo']
    template_name = 'event_form.html'
    success_url = reverse_lazy('event_list')

class EventUpdateView(UpdateView):
    model = Event
    fields = ['title', 'category', 'event_format', 'participants_limit', 'registration_status', 'age_limit', 'date_start', 'date_end', 'location_offline', 'location_online', 'description', 'main_photo']
    template_name = 'event_form.html'

    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'pk':self.object.pk})








