from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from userApp.models import CustomUser


class DeactivateUserView(UpdateView):
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