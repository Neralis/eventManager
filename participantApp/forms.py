from django import forms
from phonenumber_field.formfields import PhoneNumberField
from participantApp.models import Participants


class RegistrationParticipantsForm(forms.ModelForm):
    email = forms.EmailField()
    phone = PhoneNumberField()

    class Meta:
        model = Participants
        fields = ['email', 'phone']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)

        if self.user and self.user.is_authenticated:
            self.fields['email'].initial = self.user.email
            self.fields['phone'].initial = self.user.phone

    def clean(self):
        cleaned_data = super().clean()

        if not self.event:
            raise forms.ValidationError('Событие не найдено.')

        if self.event.registration_status and not self.user.is_authenticated:
            raise forms.ValidationError('Для участия в данном мероприятии необходимо авторизоваться')
        if self.user:
            if Participants.objects.filter(
                    event=self.event,
                    user=self.user
            ).exists():
                raise forms.ValidationError('Вы уже записаны на данное мероприятие')
        else:
            email = cleaned_data.get('email', None)
            phone = cleaned_data.get('phone', None)

            if not email or not phone:
                raise forms.ValidationError('Не все поля были заполнены для регистрации')
            if Participants.objects.filter(
                    event=self.event,
                    not_auth_user__email=email,
                    not_auth_user__phone=phone
            ).exists():
                raise forms.ValidationError('Вы уже записаны на данное мероприятие')
        return cleaned_data