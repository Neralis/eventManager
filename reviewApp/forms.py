from django import forms
from django.core.exceptions import ValidationError
from reviewApp.models import Review


class ReviewCreateForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)
    rating = forms.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = ['text', 'rating']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.email = kwargs.pop('email')
        self.event = kwargs.pop('event')

    def clean(self):
        cleaned_data = self.cleaned_data

        if not self.event:
            raise ValidationError('Отсутствует мероприятие')

        if not self.email:
            raise ValidationError('Отсутсвует участник мероприятия')

        text = cleaned_data.get('text')
        rating = cleaned_data.get('rating')

        if not text or not rating:
            raise ValidationError('Не все поля были заполнены')
        return cleaned_data
