from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import CustomUser

class CustomUserCreationForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Фамилия'}),
        label='Фамилия',
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Имя'}),
        label='Имя',
    )
    otchestvo = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Отчество'}),
        label='Отчество',
        required=False
    )
    date_birthday = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Дата рождения',
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': '+7 ___ ___-___-__',
            'pattern': r'\+7 \d{3}\ \d{3}-\d{2}-\d{3}',
            'title': 'Введите номер в формате +7 ___ ___-___-__'
        }),
        label='Телефон',
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
        label='Email',
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}),
        label='Пароль',
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтверждение пароля'}),
        label='Подтверждение пароля',
        help_text='Повторите пароль'
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'otchestvo', 'date_birthday', 'phone', 'email']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

class CustomUserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
        label='Email',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}),
        label='Пароль',
    )

class CustomUserProfile(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["avatar", "first_name", "last_name", "description"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Фамилия"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "О себе"}),
            "avatar": forms.FileInput(attrs={"class": "form-control-file"}),
        }


class CustomUserProfileEdit(forms.ModelForm):
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
        required=False
    )
    date_birthday = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Дата рождения',
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': '+7 ___ ___-___-__',
            'pattern': r'\+7 \d{3}\ \d{3}-\d{2}-\d{3}',
            'title': 'Введите номер в формате +7 ___ ___-___-__',
            'class': 'form-control'
        }),
        label='Телефон',
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}),
        label='Email',
    )
    avatar = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),
        label='Фото профиля',
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'otchestvo', 'date_birthday', 'phone', 'email', 'avatar']


class PasswordChangeCustomForm(PasswordChangeForm):
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
