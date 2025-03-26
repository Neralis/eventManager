from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import View
from django.views.generic.edit import UpdateView
from userApp.models import CustomUser
from userApp.forms import LoginForm
from userApp.utils import generate_token_for_user, validate_token_for_user, generate_unique_url_for_user
from tasksApp.tasks import send_mail_for_activate_account_task


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
            messages.error(self.request, 'Ваш аккаунт не доступен, вы можете его восстановить')
            return self.form_invalid(form)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('success')


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


class DeactivateUserView(UpdateView):
    """Представление для удаления(деактивации) аккаунта пользователя."""
    model = CustomUser
    template_name = 'userApp/delete_user.html'
    fields = ['is_active']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save(update_fields=['is_active'])
        messages.success(request, 'Пользователь удален. По желанию вы можете его восстановить.')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('success')


def index(request):
    return HttpResponse("SUCCESS")

