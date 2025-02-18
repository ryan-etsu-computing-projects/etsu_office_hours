from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import csv
import io
from .forms import *
from .models import EncryptedUser
from profiles.models import UserProfile

def is_admin(user):
    return user.is_staff

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('profiles:home'))

@user_passes_test(is_admin)
def user_management(request):
    users = EncryptedUser.objects.all().order_by('-date_joined')
    context = {
        'users': users,
        'now': timezone.now()  # Add current time to context
    }
    return render(request, 'users/management.html', context)

@user_passes_test(is_admin)
def create_user(request):
    if request.method == 'POST':
        form = UserWithProfileCreationForm(request.POST)
        if form.is_valid():
            user, password = form.save()
            messages.success(request, f'User account created for {user.email}')

            # Set classification
            classification = form.cleaned_data['classification'].lower()
            if classification == 'faculty':
                group, _created = Group.objects.get_or_create(name='Faculty')
            else:
                group, _created = Group.objects.get_or_create(name='Staff')
            user.groups.add(group)
            user.save()

            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Construct reset URL
            reset_url = request.build_absolute_uri(
                reverse('users:password_reset_confirm', kwargs={
                    'uidb64': uid,
                    'token': token
                })
            )

            # Send welcome email with password reset link
            context = {
                'user': user,
                'password': password,
                'password_reset_url': reset_url
            }
            html_message = render_to_string('users/email/welcome.html', context)
            plain_message = strip_tags(html_message)

            '''
            send_mail(
                'Welcome to ETSU Office Hours System',
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            '''

            return redirect('users:manage')
    else:
        form = UserWithProfileCreationForm()
    
    return render(request, 'users/create_user.html', {'form': form})


@user_passes_test(is_admin)
def toggle_active(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(EncryptedUser, id=user_id)
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.email} has been {status}')
    return redirect('users:manage')


@user_passes_test(is_admin)
def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            
            for row in csv_data:
                try:
                    # Generate random password
                    password = EncryptedUser.objects.make_random_password()
                    
                    # Create user
                    user = EncryptedUser.objects.create_user(
                        email=row['email'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        password=password
                    )

                    # Set classification
                    classification = row['classification'].lower()
                    if classification == 'faculty':
                        group, _created = Group.objects.get_or_create(name='Faculty')
                    else:
                        group, _created = Group.objects.get_or_create(name='Staff')
                    user.groups.add(group)
                    user.save()
                    
                    # Create associated profile
                    profile = UserProfile.objects.create(user=user)

                    # Process optional profile fields
                    if 'honorific' in row and row['honorific']:
                        profile.honorific = row['honorific']
                    if 'job_title' in row and row['job_title']:
                        profile.job_title = row['job_title']
                    if 'department' in row and row['department']:
                        profile.department = row['department']
                    if 'college' in row and row['college']:
                        profile.college = row['college']
                    if 'office_building' in row and row['office_building']:
                        profile.office_building = row['office_building']
                    if 'office_room' in row and row['office_room']:
                        profile.office_room = row['office_room']

                    profile.save()

                    # Generate password reset token
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    
                    # Construct reset URL
                    reset_url = request.build_absolute_uri(
                        reverse('users:password_reset_confirm', kwargs={
                            'uidb64': uid,
                            'token': token
                        })
                    )

                    # Send welcome email with password reset link
                    context = {
                        'user': user,
                        'password': password,
                        'password_reset_url': reset_url
                    }
                    html_message = render_to_string('users/email/welcome.html', context)
                    plain_message = strip_tags(html_message)
                    
                    send_mail(
                        'Welcome to ETSU Office Hours System',
                        plain_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    
                except Exception as e:
                    messages.error(request, f'Error processing row for {row.get("email")}: {str(e)}')
                    continue
                    
            messages.success(request, 'CSV file processed successfully')
            return redirect('users:manage')
    else:
        form = CSVUploadForm()
    
    return render(request, 'users/upload_csv.html', {'form': form})
