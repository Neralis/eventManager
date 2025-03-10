from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import StackedInline, TabularInline, ModelAdmin
from userApp.models import CustomUser, NotAuthUser
from userApp.models import CustomUser, NotAuthUser, Notification


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = [
        'user',
        'text',
        'url_event',
        'created',
        'is_read'
    ]
    list_filter = [
        'user',
        'created'
    ]
    ordering = ['-created']


class NotificationInline(TabularInline):
    model = Notification
    extra = 0
    readonly_fields = [
        'user',
        'url_event',
        'created'
    ]
    can_delete = False
    verbose_name = 'Уведомление'
    verbose_name_plural = 'Уведомления'

    
@admin.register(CustomUser)
class CustomUser(ModelAdmin):
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
    inlines = [NotificationInline]


@admin.register(NotAuthUser)
class NotAuthUserAdmin(ModelAdmin):
    list_display = [
        'email',
        'phone'
    ]
    search_fields = [
        'email',
        'phone'
    ]
    ordering = [
      'email'
    ]

