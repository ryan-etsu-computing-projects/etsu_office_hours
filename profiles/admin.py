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
    list_display = ['user', 'title', 'phone']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

@admin.register(OfficeHours)
class OfficeHoursAdmin(admin.ModelAdmin):
    list_display = ['user', 'semester', 'is_public', 'updated_at']
    list_filter = ['semester', 'is_public']
    search_fields = ['user__email']
