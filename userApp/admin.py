from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from userApp.models import CustomUser, NotAuthUser


@admin.register(CustomUser)
class CustomUser(admin.ModelAdmin):
    list_display = [
        'username',
        'first_name',
        'last_name',
        'email',
        'phone',
    ]
    list_filter = [
        'date_birthday',
    ]
    search_fields = [
        'username',
        'email',
        'phone',
    ]
    ordering = [
        'first_name',
        'last_name',
        'date_birthday',
    ]
    save_on_top = True

@admin.register(NotAuthUser)
class NotAuthUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone']
    search_fields = ['email', 'phone']
    ordering = ['email']

