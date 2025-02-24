from django import forms
from .models import Event, EventImages

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'category', 'event_format', 'participants_limit', 
                  'registration_status', 'age_limit', 'date_start', 'date_end', 
                  'location_offline', 'location_online', 'description', 'main_photo']

class EventImagesForm(forms.ModelForm):
    class Meta:
        model = EventImages
        fields = ['image']
