from reviewApp.models import Review
from .models import Event, Category, EventImages
from django.contrib import admin


class EventsOfCategoryInLine(admin.StackedInline):
    model = Event.category.through
    extra = 0

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'title'
    ]
    search_fields = [
        'title'
    ]
    inlines = [
        EventsOfCategoryInLine
    ]


class ReviewOnEventInLine(admin.TabularInline):
    model = Review
    extra = 0
    ordering = [
        '-rating'
    ]

class AdditionalImagesInline(admin.StackedInline):
    model = EventImages
    extra = 0

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        field.name for field in Event._meta.fields
    ]
    list_filter = [
        'category',
        'date_start',
        'date_end',
        'organizer',
        'event_format',
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
    inlines = [
        AdditionalImagesInline,
        ReviewOnEventInLine,
    ]



@admin.register(EventImages)
class EventImagesAdmin(admin.ModelAdmin):
    list_display = [
        'event',
        'image'
    ]
    search_fields = [
        'event'
    ]


