from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
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
