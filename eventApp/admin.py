from .models import Event, Category
from django.contrib import admin

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass