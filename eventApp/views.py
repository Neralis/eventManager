from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, FormView
from eventApp.models import Event
from eventApp.forms import ReasonForDeleteEventForm
from tasksApp.tasks import send_mail_with_reason_task


class ReasonForDeleteEventView(FormView):
    """Представление для обработки формы ReasonForDeleteEventForm и удаления мероприятия."""
    form_class = ReasonForDeleteEventForm
    template_name = 'eventApp/reason_form.html'
    success_url = reverse_lazy('success')

    def get_instance(self):
        event_id = self.kwargs.get('event_id')
        return get_object_or_404(Event, id=event_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.get_instance()
        return context

    def form_valid(self, form):
        event = self.get_instance()
        reason = form.cleaned_data['reason']
        email_list = [participant.get_email() for participant in event.participants.all()]
        event_title = event.title
        event.delete()
        send_mail_with_reason_task.delay(email_list, event_title, reason)
        return super().form_valid(form)


class DeleteEventView(DeleteView):
    model = Event
    template_name = 'eventApp/delete_event.html'
    pk_url_kwarg = 'event_id'

    def get(self, request, *args, **kwargs):
        event = self.get_object()
        if event.is_active:
            return redirect('reason_for_delete_event', event_id=event.id)
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('success')
