from django import forms
from userApp.models import CustomUser


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(), label="Имя пользователя")
    password = forms.CharField(widget=forms.PasswordInput(), label="Пароль")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            try:
                user = CustomUser.objects.get(username=username)
                if user.check_password(password):
                    self.cleaned_data['user'] = user
                else:
                    raise forms.ValidationError('Неверное имя пользователя или пароль')
            except CustomUser.DoesNotExist:
                raise forms.ValidationError('Отсутствует аккаунт')
        return cleaned_data

    def get_user(self):
        return self.cleaned_data['user']