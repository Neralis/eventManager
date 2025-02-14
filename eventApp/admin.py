from .models import Event, Category, EventImages
from django.contrib import admin


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Event._meta.fields]
    list_filter = [
        'category',
        'date_start',
        'date_end',
        'organizer',
        'format',
        'registration_status',
    ]
    search_fields = [
        'title',
        'category',
        'organizer',
    ]
    ordering = [
        'date_start',
        'date_end',
        'age_limit',
    ]
    save_on_top = True

@admin.register(EventImages)
class EventImagesAdmin(admin.ModelAdmin):
    list_display = [
        'event',
        'image'
    ]
    search_fields = ['event']
