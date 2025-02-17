# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from .models import EncryptedUser
import csv
import io

class EncryptedUserCreationForm(UserCreationForm):
    """Form for creating a new user with encrypted fields."""
    email = forms.EmailField(
        required=True,
        help_text='Required. Must be a valid ETSU email address.',
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
    
    class Meta:
        model = EncryptedUser
        fields = ('email', 'first_name', 'last_name')
        
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if not email.endswith('@etsu.edu'):
            raise ValidationError("Please use your ETSU email address.")
        if EncryptedUser.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = None  # Ensure username is not used
        if commit:
            user.save()
        return user

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

class UserQuickCreateForm(forms.ModelForm):
    """Form for quickly creating a single user with minimal fields."""
    class Meta:
        model = EncryptedUser
        fields = ('email', 'first_name', 'last_name')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = True
            
    def save(self, commit=True):
        user = super().save(commit=False)
        # Generate a random password
        temp_password = get_random_string(12)
        user.set_password(temp_password)
        
        if commit:
            user.save()
            
        return user, temp_password

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
