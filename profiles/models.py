from django.db import models
from django.conf import settings
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField
from django.utils import timezone
import datetime

class Semester(models.TextChoices):
    FALL = 'FA', 'Fall'
    SPRING = 'SP', 'Spring'
    SUMMER = 'SU', 'Summer'
    WINTER = 'WI', 'Winter'

def get_current_semester():
    month = timezone.now().month
    if month in [1]:  # January
        return Semester.WINTER
    elif month in [2, 3, 4, 5]:  # February to May
        return Semester.SPRING
    elif month in [6, 7, 8]:  # June to August
        return Semester.SUMMER
    else:  # September to December
        return Semester.FALL

def get_semester_choices():
    current_date = timezone.now()
    current_year = current_date.year
    current_semester = get_current_semester()
    
    choices = []
    for year in range(current_year, current_year + 2):
        for semester in Semester.choices:
            choices.append((f"{semester[1]} {year}", f"{semester[1]} {year}"))
    return choices

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    preferred_name = EncryptedCharField(max_length=100, blank=True)
    title = EncryptedCharField(max_length=50, blank=True)
    pronouns = EncryptedCharField(max_length=50, blank=True)
    bio = EncryptedTextField(blank=True)
    phone = EncryptedCharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True)

class OfficeHours(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20, choices=get_semester_choices())
    scheduling_link = models.URLField(blank=True)
    is_public = models.BooleanField(default=True)
    time_slots = models.JSONField(default=list)  # Add this field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_formatted_time_slots(self):
        """Return time slots in a formatted way for display"""
        return sorted(self.time_slots, key=lambda x: (
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].index(x.get('day', '')),
            x.get('startTime', '')
        ))
    
    class Meta:
        verbose_name_plural = 'Office hours'

class CourseOfficeHours(models.Model):
    office_hours = models.ForeignKey(OfficeHours, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=100)
    course_description = models.TextField(blank=True)
    time_slots = models.JSONField(default=list)

    def __str__(self):
        return f"{self.course_name} - {self.office_hours.user.email}"

    def get_formatted_time_slots(self):
        """Return time slots in a formatted way for display"""
        return sorted(self.time_slots, key=lambda x: (
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].index(x.get('day', '')),
            x.get('startTime', '')
        ))
