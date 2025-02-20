# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import EncryptedUser
import csv
import io
from profiles.models import UserProfile

class UserWithProfileCreationForm(UserCreationForm):
    """Form for creating a new user with initial profile information."""

    CLASSIFICATION_CHOICES = (
        ('Faculty', 'Faculty'),
        ('Staff', 'Staff'),
    )

    # Profile fields
    classification = forms.CharField(widget=forms.Select(choices=CLASSIFICATION_CHOICES), label='Classification')
    honorific = forms.CharField(max_length=50, required=False, label='Title/Honorific (e.g., Dr., Prof., Mr., Ms.)')
    phone = forms.CharField(required=False, label='Phone',widget=forms.TextInput(attrs={'placeholder': '(423) 439-1234'}))
    job_title = forms.CharField(max_length=100, required=False, label='Job Title')
    department = forms.CharField(max_length=100, required=False, label='Department (e.g., Department of Computing)')
    college = forms.CharField(max_length=100, required=False, label='College (e.g., College of Business and Technology)')
    office_building = forms.CharField(max_length=100, required=False, label='Office Building (e.g., Nicks Hall)')
    office_room = forms.CharField(max_length=50, required=False, label='Office Room Number (e.g., 404)')

    class Meta:
        model = EncryptedUser
        fields = ('email', 'first_name', 'last_name', 'classification', 'honorific',
                  'job_title', 'department', 'college', 'office_building', 'office_room')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password1' in self.fields: del self.fields['password1']
        if 'password2' in self.fields: del self.fields['password2']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if not email.endswith('@etsu.edu'):
            raise ValidationError("Please use your ETSU email address.")
        if EncryptedUser.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            print(">> Got the phone!")
            # Remove any non-digit characters
            phone = ''.join(filter(str.isdigit, phone))

            # Validate length
            if len(phone) != 10:
                raise ValidationError("Phone number must be 10 digits.")

            # Format as (XXX) XXX-XXXX
            phone = f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"

        return phone

    def save(self, commit=True):
        # Calling forms.ModelForm contstructor instead of super().save(...) to bypass
        # the UserCreationForm's save method entirely (requires password1)
        user = super(forms.ModelForm, self).save(commit=False)
        # Generate a random password
        temp_password = EncryptedUser.objects.make_random_password()
        user.set_password(temp_password)

        if commit:
            user.save()

            # Create or update profile with the provided fields
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.honorific = self.cleaned_data.get('honorific', '')
            profile.phone = self.cleaned_data.get('phone', '')
            profile.job_title = self.cleaned_data.get('job_title', '')
            profile.department = self.cleaned_data.get('department', '')
            profile.college = self.cleaned_data.get('college', '')
            profile.office_building = self.cleaned_data.get('office_building', '')
            profile.office_room = self.cleaned_data.get('office_room', '')
            profile.save()

        return user, temp_password

class CSVUploadForm(forms.Form):
    """Form for uploading CSV file containing multiple users."""
    csv_file = forms.FileField(
        label='Select CSV File',
        help_text='File must be in CSV format with required columns: email, first_name, last_name, classification'
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        if not csv_file.name.endswith('.csv'):
            raise ValidationError('File must be a CSV')
        
        required_fields = {'email', 'first_name', 'last_name', 'classification'}
        
        try:
            # Read the CSV file
            csv_data = csv_file.read().decode('utf-8')
            csv_file.seek(0)  # Reset file pointer
            
            # Parse the CSV
            reader = csv.DictReader(io.StringIO(csv_data))
            
            # Verify headers
            headers = set(reader.fieldnames if reader.fieldnames else [])
            missing_fields = required_fields - headers
            if missing_fields:
                raise ValidationError(f'Missing required columns: {", ".join(missing_fields)}')
            
            # Validate each row
            line_number = 1
            emails = set()
            for row in reader:
                line_number += 1
                
                # Check for missing values
                for field in required_fields:
                    if not row.get(field):
                        raise ValidationError(f'Missing {field} in line {line_number}')
                
                # Validate email
                email = row['email'].lower()
                if not email.endswith('@etsu.edu'):
                    raise ValidationError(f'Invalid ETSU email address in line {line_number}: {email}')
                if email in emails:
                    raise ValidationError(f'Duplicate email address in line {line_number}: {email}')
                emails.add(email)
                
                # Validate classification
                classification = row['classification'].lower()
                if classification not in ['faculty', 'staff']:
                    raise ValidationError(
                        f'Invalid classification in line {line_number}. Must be "Faculty" or "Staff"'
                    )
            
            return csv_file
            
        except Exception as e:
            raise ValidationError(f'Error processing CSV file: {str(e)}')

class AdminUserChangeForm(UserChangeForm):
    """Custom form for admin to edit user details."""
    class Meta:
        model = EncryptedUser
        fields = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password', None)  # Remove the password field

class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form that only allows ETSU email addresses."""
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if not email.endswith('@etsu.edu'):
            raise ValidationError("Please use your ETSU email address.")
        return email

class UserToggleActiveForm(forms.Form):
    """Form for toggling user active status."""
    user_id = forms.IntegerField(widget=forms.HiddenInput())
    
    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        try:
            user = EncryptedUser.objects.get(id=user_id)
            return user_id
        except EncryptedUser.DoesNotExist:
            raise ValidationError("User not found")
