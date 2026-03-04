from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'size', 'assigned_to', 'is_completed', 'deadline', 'created_at')
    list_filter = ('priority', 'is_completed')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)
