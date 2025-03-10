from reviewApp.models import Review
from unfold.admin import StackedInline, TabularInline, ModelAdmin
from .models import Event, Category, EventImages
from django.contrib import admin
from participantApp.models import Participants
from reviewApp.models import Review


class ParticipantsInLine(admin.TabularInline):
    model = Participants
    extra = 0
    readonly_fields = [
        'user',
        'not_auth_user',
        'created'
    ]
    can_delete = False
    verbose_name = 'Участник'
    verbose_name_plural = 'Участники'


class ReviewsInLine(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = [
        'participant',
        'text',
        'rating'
    ]
    can_delete = False
    verbose_name = 'Отзыв'
    verbose_name_plural = 'Отзывы'


class EventImagesInline(admin.TabularInline):
    model = EventImages
    extra = 0
    readonly_fields = ['image']
    can_delete = False
    verbose_name = 'Изображение'
    verbose_name_plural = 'Изображения'


class EventsOfCategoryInLine(StackedInline):
    model = Event.category.through
    extra = 0

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = [
        'title'
    ]
    search_fields = [
        'title'
    ]
    inlines = [
        EventsOfCategoryInLine
    ]


class ReviewOnEventInLine(TabularInline):
    model = Review
    extra = 0
    tab = True
    ordering = [
        '-rating'
    ]

class AdditionalImagesInline(StackedInline):
    model = EventImages
    extra = 0
    tab = True

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
      field.name for field in Event._meta.fields
    ]
    readonly_fields = [
      'available_places'
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
class EventImagesAdmin(ModelAdmin):
    list_display = [
        'event',
        'image'
    ]
    search_fields = [
        'event'
    ]


