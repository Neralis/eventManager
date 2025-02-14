from django.contrib import admin
from  .models import  Participants


@admin.register(Participants)
class ParticipantsAdmin(admin.ModelAdmin):
    list_display = [
        'event',
        'user',
        'not_auth_user',
        'created'
    ]
    list_filter = [
        'event',
        'created'
    ]
    ordering = ['created']
    readonly_fields = ['created']
    search_fields = ['event']
