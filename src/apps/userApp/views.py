from django.utils.timezone import now
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import View, DetailView
from django.views.generic.edit import UpdateView, CreateView
from src.apps.userApp.models import CustomUser
from src.apps.userApp.forms import LoginForm, CustomUserCreationForm, CustomUserProfileEditForm, \
    CustomPasswordChangeForm
from src.apps.userApp.utils import generate_token_for_user, validate_token_for_user, generate_unique_url_for_user
from src.apps.tasksApp.tasks import send_mail_for_activate_account_task


class LoginUserView(LoginView):
    """Представление для авторизации."""
    template_name = 'userApp/login.html'
    form_class = LoginForm

    def form_valid(self, form):
        """Если аккаунт пользователя не активен, то его данные сохраняются в сессии для восстановления аккаунта."""
        user = form.get_user()
        if not user.is_active:
            user_data = {
                'user_id': user.id,
                'email': user.email,
            }
            self.request.session['user_data'] = user_data
            messages.error(self.request, 'Ваш аккаунт был удален, его необходимо восстановить')
            return self.form_invalid(form)
        login(self.request, user)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('event_list')


class RestoreUserAccountRequestView(View):
    """
    Представление для восстановления аккаунта:
        - генерации токена
        - генерации url
        - отправки задачи celery для отправкии сообщения на почту
    """

    def get(self, request, *args, **kwargs):
        user_data = request.session['user_data']
        if not user_data:
            messages.error(request, 'Данные пользователя отсутствуют')
            return redirect('login')
        token = generate_token_for_user(user_data['email'], user_data['user_id'])
        unique_url = generate_unique_url_for_user(token)
        send_mail_for_activate_account_task.delay(user_data['email'], unique_url)
        messages.success(request, 'На вашу почту отправлено сообщение для восстановления аккаунта')
        del request.session['user_data']
        return redirect('login')


class ActivateUserView(View):
    """Представление для восстановления(активации) аккаунта пользователя."""
    template_name = 'userApp/activate_user.html'

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        email, user_id = validate_token_for_user(token)
        if email is None or user_id is None:
            messages.error(request, 'Ссылка недействительна или истек ее срок действия')
            return render(request, self.template_name)
        try:
            user = CustomUser.objects.get(id=user_id)
            if not user.is_active:
                user.is_active = True
                user.save()
                messages.success(request, 'Аккаунт восстановлен, рады снова вас видеть!')
            else:
                messages.info(request, 'Аккаунт уже активен')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
        return render(request, self.template_name)


class DeactivateUserView(LoginRequiredMixin, UpdateView):
    """Представление для удаления(деактивации) аккаунта пользователя."""
    model = CustomUser
    template_name = 'userApp/delete_user.html'
    fields = ['is_active']

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save(update_fields=['is_active'])
        request.session.flush()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('event_list')


# --------------------------------------------

class RegisterView(CreateView):
    """Представление для регистрации пользователя."""
    form_class = CustomUserCreationForm
    template_name = 'userApp/register.html'
    success_url = reverse_lazy('event_list')


class UserLogoutView(LoginRequiredMixin, LogoutView):
    """Представление для выхода пользователя."""
    next_page = reverse_lazy('event_list')


class ProfileView(DetailView):
    """Представление для отображения профиля пользователя."""
    model = CustomUser
    template_name = 'userApp/detail_user.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = self.object.events.all()
        context['profile'] = self.object.profile
        context['now'] = now()
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля."""
    model = CustomUser
    form_class = CustomUserProfileEditForm
    template_name = 'userApp/edit_user.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_profile'] = self.request.user.profile
        return kwargs

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('profile')


class PasswordChangeCustomView(LoginRequiredMixin, PasswordChangeView):
    """Представление для смены пароля."""
    form_class = CustomPasswordChangeForm
    template_name = 'userApp/password_change.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        update_session_auth_hash(self.request, form.user)
        return response

    def get_success_url(self):
        return reverse_lazy('profile')