from django.contrib import admin
from unfold.admin import ModelAdmin
from participantApp.models import Participants


@admin.register(Participants)
class ParticipantsAdmin(ModelAdmin):
    list_display = [
        'id',
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
