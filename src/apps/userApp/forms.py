import random
import string
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm, AuthenticationForm
from src.apps.userApp.models import CustomUser


class LoginForm(AuthenticationForm):
    """Форма для авторизации."""
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
        label="Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
        label="Пароль"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(self.request, email=username, password=password)
            if self.user_cache is None:
                try:
                    user = CustomUser.objects.get(email=username)
                    if not user.is_active:
                        self.user_cache = user
                except CustomUser.DoesNotExist:
                    raise forms.ValidationError(
                        self.error_messages['invalid_login'],
                        code='invalid_login',
                        params={'username': 'Email'},
                    )
            if self.user_cache:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        pass


class BaseCustomUserForm(forms.ModelForm):
    """Базовая форма."""
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Фамилия', 'class': 'form-control'}),
        label='Фамилия',
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Имя', 'class': 'form-control'}),
        label='Имя',
    )
    otchestvo = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Отчество (необязательно)', 'class': 'form-control'}),
        label='Отчество',
        required=False,
    )
    date_birthday = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Дата рождения',
        required=False,
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': '+7 ___ ___-___-__',
            'pattern': r'\+7 \d{3} \d{3}-\d{2}-\d{2}',
            'title': 'Введите номер в формате +7 ___ ___-___-__',
            'class': 'form-control'
        }),
        label='Телефон',
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}),
        label='Email',
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'otchestvo', 'date_birthday', 'phone', 'email']


class CustomUserCreationForm(BaseCustomUserForm, UserCreationForm):
    """Форма для регистрации пользователя."""
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль', 'class': 'form-control'}),
        label='Пароль',
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтверждение пароля', 'class': 'form-control'}),
        label='Подтверждение пароля',
        help_text='Повторите пароль',
    )

    class Meta(BaseCustomUserForm.Meta):
        fields = BaseCustomUserForm.Meta.fields + ['password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = f"user{''.join(random.choices(string.digits, k=5))}"
        if commit:
            user.save()
        return user


class CustomUserProfileEditForm(BaseCustomUserForm):
    """Форма для редактирования профиля."""
    avatar = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),
        label='Фото профиля',
        required=False,
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'О себе'}),
        label='О себе',
        required=False,
    )

    class Meta(BaseCustomUserForm.Meta):
        fields = BaseCustomUserForm.Meta.fields + ['avatar', 'description']

    def __init__(self, *args, **kwargs):
        self.user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)
        if self.user_profile:
            self.fields['avatar'].initial = self.user_profile.avatar
            self.fields['description'].initial = self.user_profile.description

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if self.user_profile:
                self.user_profile.avatar = self.cleaned_data['avatar']
                self.user_profile.description = self.cleaned_data['description']
                self.user_profile.save()
        return user


class CustomPasswordChangeForm(PasswordChangeForm):
    """Форма для смены пароля."""
    old_password = forms.CharField(
        label="Старый пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Старый пароль"}),
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Новый пароль"}),
    )
    new_password2 = forms.CharField(
        label="Подтвердите новый пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Подтвердите новый пароль"}),
    )