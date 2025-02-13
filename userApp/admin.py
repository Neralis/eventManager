from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from userApp.models import CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    pass

