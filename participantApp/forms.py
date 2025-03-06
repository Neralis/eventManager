from django import forms
from phonenumber_field.formfields import PhoneNumberField
from participantApp.models import Participants


class RegistrationParticipantsForm(forms.ModelForm):
    """Форма для регистрации пользователей на мероприятие."""
    email = forms.EmailField()
    phone = PhoneNumberField()

    class Meta:
        model = Participants
        fields = ['email', 'phone']

    def __init__(self, *args, **kwargs):
        """Получает из URL данные о авторизованном пользователе и мероприятии."""
        self.user = kwargs.pop('user', None)
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)

        if self.user and self.user.is_authenticated:
            self.fields['email'].initial = self.user.email
            self.fields['phone'].initial = self.user.phone

    def clean(self):
        """Валидирует данные."""
        cleaned_data = super().clean()

        if not self.event:
            raise forms.ValidationError('Событие не найдено.')

        if self.event.registration_status and not self.user:
            raise forms.ValidationError('Для участия в данном мероприятии необходимо авторизоваться.')

        email = cleaned_data.get('email', None)
        phone = cleaned_data.get('phone', None)

        if not self.user and (not email or not phone):
            raise forms.ValidationError('Не все поля были заполнены для регистрации.')
        return cleaned_data