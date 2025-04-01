from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm, CustomUserLoginForm, PasswordChangeCustomForm, CustomUserProfile, \
    CustomUserProfileEdit
from .models import CustomUser
import random
import string

def generate_random_username():
    return "user" + "".join(random.choices(string.digits, k=5))

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = generate_random_username()
            user.set_password(form.cleaned_data["password1"])
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.otchestvo = form.cleaned_data.get("otchestvo", "")
            user.date_birthday = form.cleaned_data.get("date_birthday", None)
            user.phone = form.cleaned_data["phone"]
            try:
                user.save()
                return redirect("event_list")
            except Exception as e:
                print(e)
        else:
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        form = CustomUserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("event_list")
    else:
        form = CustomUserLoginForm()
    return render(request, "registration/login.html", {"form": form})

class Profile(generic.DetailView):
    model = CustomUser
    template_name = "userApp/customuser_detail.html"
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["events"] = self.object.events.all()
        return context

class ProfileEdit(generic.UpdateView):
    model = CustomUser
    form_class = CustomUserProfileEdit
    template_name = "userApp/customuser_edit.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=self.object)

        if form.is_valid():
            form.save()
            old_password = request.POST.get("old_password")
            new_password1 = request.POST.get("new_password1")
            new_password2 = request.POST.get("new_password2")

            if old_password and new_password1 and new_password2:
                if new_password1 == new_password2:
                    if self.object.check_password(old_password):
                        self.object.set_password(new_password1)
                        self.object.save()
                        update_session_auth_hash(request, self.object)
                    else:
                        return self.form_invalid(form)
                else:
                    return self.form_invalid(form)
            return redirect(reverse_lazy("profile", kwargs={"pk": self.object.pk}))
        return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("profile", kwargs={"pk": self.object.pk})