from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime as dt
from .models import UserProfile, OfficeHours, CourseOfficeHours
from PIL import Image
import json
import logging

logger = logging.getLogger(__name__)

class ProfileForm(forms.ModelForm):
    """Form for editing user profile information."""
    class Meta:
        model = UserProfile
        fields = ['title', 'preferred_name', 'pronouns', 'phone', 'bio', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'phone': forms.TextInput(attrs={'placeholder': '(123) 456-7890'}),
        }

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if not image:
            return image
            
        try:
            # Open the image
            img = Image.open(image)
            
            # Check file size
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("Image file too large. Size should not exceed 5MB.")
                
            # Check dimensions
            max_size = (800, 800)
            if img.height > max_size[1] or img.width > max_size[0]:
                raise ValidationError(
                    f"Image too large. Maximum dimensions are {max_size[0]}x{max_size[1]} pixels."
                )
                
            # Verify it's an acceptable format
            if img.format.lower() not in ['jpeg', 'jpg', 'png']:
                raise ValidationError(
                    "Unsupported file format. Please use JPEG or PNG images."
                )
                
            return image
            
        except Exception as e:
            raise ValidationError(f"Error processing image: {str(e)}")

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any non-digit characters
            phone = ''.join(filter(str.isdigit, phone))
            
            # Validate length
            if len(phone) != 10:
                raise ValidationError("Phone number must be 10 digits.")
                
            # Format as (XXX) XXX-XXXX
            phone = f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
            
        return phone

class OfficeHoursForm(forms.ModelForm):
    """Form for editing office hours settings."""
    class Meta:
        model = OfficeHours
        fields = ['semester', 'scheduling_link', 'is_public', 'time_slots']
        widgets = {
            'scheduling_link': forms.URLInput(
                attrs={'placeholder': 'https://calendar.google.com/...'}
            ),
            'time_slots': forms.HiddenInput()
        }

    def clean_time_slots(self):
        try:
            time_slots = self.cleaned_data.get('time_slots', '[]')
            if isinstance(time_slots, str):
                time_slots = json.loads(time_slots)
            if not isinstance(time_slots, list):
                raise ValidationError("Time slots must be a list")
            
            # Validate each time slot
            for slot in time_slots:
                if not isinstance(slot, dict):
                    raise ValidationError("Each time slot must be an object")
                
                required_fields = {'day', 'startTime', 'endTime'}
                missing_fields = required_fields - set(slot.keys())
                if missing_fields:
                    raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
                
                # Validate day
                valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                if slot['day'] not in valid_days:
                    raise ValidationError(f"Invalid day: {slot['day']}")
                
                # Validate time format and range
                try:
                    start_time = dt.strptime(slot['startTime'], '%H:%M').time()
                    end_time = dt.strptime(slot['endTime'], '%H:%M').time()
                    
                    if end_time <= start_time:
                        raise ValidationError(f"End time must be after start time for {slot['day']}")
                except ValueError:
                    raise ValidationError("Invalid time format")
            
            return time_slots
            
        except json.JSONDecodeError:
            raise ValidationError("Invalid time slot format")
    
class CourseOfficeHoursForm(forms.ModelForm):
    """Form for managing course-specific office hours."""
    time_slots = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = CourseOfficeHours
        fields = ['course_name', 'course_description', 'time_slots']
        widgets = {
            'course_description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_time_slots(self):
        try:
            time_slots = self.cleaned_data.get('time_slots', '[]')
            if isinstance(time_slots, str):
                time_slots = json.loads(time_slots)
            if not isinstance(time_slots, list):
                raise ValidationError("Time slots must be a list")
            
            print(f"Cleaning time slots data: {time_slots}")
            
            # Validate each time slot
            for slot in time_slots:
                if not isinstance(slot, dict):
                    raise ValidationError("Each time slot must be an object")
                
                if 'day' not in slot or 'startTime' not in slot or 'endTime' not in slot:
                    raise ValidationError("Each time slot must have a day, start time, and end time")
                
                # Validate day
                valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                if slot['day'] not in valid_days:
                    raise ValidationError(f"Invalid day: {slot['day']}")
                
                # Validate time format and range
                try:
                    start_time = dt.strptime(slot['startTime'], '%H:%M').time()
                    end_time = dt.strptime(slot['endTime'], '%H:%M').time()
                    
                    if end_time <= start_time:
                        raise ValidationError(f"End time must be after start time for {slot['day']}")
                except ValueError:
                    raise ValidationError("Invalid time format")
            
            return time_slots
            
        except json.JSONDecodeError:
            raise ValidationError("Invalid time slot format")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.time_slots = self.cleaned_data.get('time_slots', [])
        if commit:
            instance.save()
        return instance

class BulkOfficeHoursUpdateForm(forms.Form):
    """Form for updating multiple users' office hours semester at once."""
    old_semester = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        required=True,
        label="Current Semester"
    )
    new_semester = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        required=True,
        label="New Semester"
    )
    notify_users = forms.BooleanField(
        required=False,
        initial=True,
        label="Send email notification to affected users"
    )

    def __init__(self, *args, **kwargs):
        semester_choices = kwargs.pop('semester_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['old_semester'].choices = semester_choices
        self.fields['new_semester'].choices = semester_choices

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('old_semester') == cleaned_data.get('new_semester'):
            raise ValidationError("New semester must be different from the old semester")
        return cleaned_data
