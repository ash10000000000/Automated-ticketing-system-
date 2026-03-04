from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_manager', 'specialty', 'is_active', 'is_staff')
    list_filter = ('is_manager', 'is_active', 'is_staff')

    # Add custom fields to the admin form
    fieldsets = UserAdmin.fieldsets + (
        ('Ticketing Info', {'fields': ('is_manager', 'specialty')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Ticketing Info', {'fields': ('is_manager', 'specialty')}),
    )
