from django import forms

from src.apps.eventApp.models import Event, EventImages


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'category', 'event_format', 'participants_limit',
                  'registration_status', 'age_limit', 'date_start', 'date_end', 'city',
                  'location_offline', 'location_online', 'description', 'main_photo']


class EventImagesForm(forms.ModelForm):
    class Meta:
        model = EventImages
        fields = ['image']


class ReasonForDeleteEventForm(forms.Form):
    """Форма для заполнения причины удаления мероприятия, если оно активно."""
    reason = forms.CharField(
        widget=forms.Textarea,
        label="Причина отмены(необязательно)",
        required=False
    )