from django.contrib import admin
from .models import Review
from unfold.admin import StackedInline, TabularInline, ModelAdmin


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
