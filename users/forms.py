from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import EncryptedUser
import csv
import io

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = EncryptedUser
        fields = ('email', 'first_name', 'last_name')

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('File must be a CSV')
        
        required_fields = {'email', 'first_name', 'last_name', 'classification'}
        
        try:
            csv_file.seek(0)
            reader = csv.DictReader(io.StringIO(csv_file.read().decode('utf-8')))
            headers = set(reader.fieldnames)
            
            if not required_fields.issubset(headers):
                missing = required_fields - headers
                raise forms.ValidationError(f'Missing required fields: {", ".join(missing)}')
                
        except Exception as e:
            raise forms.ValidationError(f'Error processing CSV file: {str(e)}')
            
        return csv_file
    