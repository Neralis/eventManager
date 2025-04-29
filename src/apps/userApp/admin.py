from django.contrib import admin
from unfold.admin import TabularInline, ModelAdmin
from src.apps.userApp.models import CustomUser, NotAuthUser, Notification, UserProfile


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

    def save_model(self, request, obj, form, change):
        if 'password' in form.cleaned_data:
            raw_password = form.cleaned_data['password']
            if not raw_password.startswith('pbkdf2_sha256$'):
                obj.set_password(raw_password)
        super().save_model(request, obj, form, change)


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = [
        'user',
        'description'
    ]


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

