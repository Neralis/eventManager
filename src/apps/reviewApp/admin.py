from django.contrib import admin
from src.apps.reviewApp.models import Review
from unfold.admin import ModelAdmin


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = [
        'participant',
        'event',
        'text',
        'rating'
    ]
    list_filter = [
        'event',
        'rating'
    ]
    ordering = ['rating']
    search_fields = ['event']
