# profiles/admin.py
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from .models import UserProfile, OfficeHours, CourseOfficeHours

class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['action_time', 'user', 'content_type', 'object_repr', 'action_flag']
    list_filter = ['action_flag', 'action_time']
    search_fields = ['object_repr', 'user__email']
    date_hierarchy = 'action_time'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(LogEntry, LogEntryAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'honorific', 'phone']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

    def has_add_permission(self, request):
        """Prevent creating profiles through the admin interface."""
        return False

@admin.register(OfficeHours)
class OfficeHoursAdmin(admin.ModelAdmin):
    list_display = ['user', 'semester', 'is_public', 'updated_at']
    list_filter = ['semester', 'is_public']
    search_fields = ['user__email']

    def has_add_permission(self, request):
        """Office hours should only be created through the profile interface."""
        return False

@admin.register(CourseOfficeHours)
class CourseOfficeHoursAdmin(admin.ModelAdmin):
    list_display = ['office_hours', 'course_name']
    search_fields = ['office_hours__user__email', 'course_name']

    def has_add_permission(self, request):
        """Course hours should only be created through the profile interface."""
        return False