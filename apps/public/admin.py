from django.contrib import admin
from .models import Feedback, News


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('public_id', 'name', 'subject', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('public_id', 'created_at')


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'is_published')
    list_filter = ('is_published',)
