from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import UserProfile, OfficeHours, CourseOfficeHours
from .forms import ProfileForm, OfficeHoursForm, CourseOfficeHoursForm
import logging
import json
import os

logger = logging.getLogger(__name__)

def home(request):
    # Start with all profiles
    profiles_list = UserProfile.objects.select_related('user').all()

    # Get filter parameters if present
    classification_filter = request.GET.get('classification', '')
    sort_direction = request.GET.get('sort', 'asc')  # Default to ascending
    search_query = request.GET.get('search', '').strip()

    # Apply classification filter if specified
    if classification_filter in ['Faculty', 'Staff']:
        profiles_list = profiles_list.filter(
            user__groups__name=classification_filter
        )

    if search_query:
        # Log the search query for debugging
        logger.debug(f"Search query: '{search_query}'")

        # Split query into tokens
        tokens = [token.strip().lower() for token in search_query.split() if token.strip()]
        logger.debug(f"Search tokens: {tokens}")

        # If we have tokens, search each one
        if tokens:
            # Start with all profiles
            token_results = profiles_list

            # For each token, filter the results
            for token in tokens:
                # Create a filter for this token
                token_filter = (
                    # Unencrypted fields
                    models.Q(user__first_name__icontains=token) |
                    models.Q(user__last_name__icontains=token) |
                    models.Q(user__email__icontains=token) |

                    # Encrypted fields
                    models.Q(job_title__icontains=token) |
                    models.Q(department__icontains=token) |
                    models.Q(college__icontains=token) |
                    models.Q(honorific__icontains=token) |
                    models.Q(preferred_name__icontains=token) |

                    # Special cases for department/college
                    models.Q(department__icontains=f"Department of {token}") |
                    models.Q(college__icontains=f"College of {token}")
                )

                # Filter the results with this token
                token_results = token_results.filter(token_filter)

            # Use the filtered results
            profiles_list = token_results.distinct()
            logger.debug(f"Tokenized search found {profiles_list.count()} results")

            # If no results from DB query, try Python filtering
            if profiles_list.count() == 0:
                logger.debug("No results from tokenized database query, trying Python filtering")
                all_profiles = list(UserProfile.objects.select_related('user').all())
                filtered_profiles = []

                for profile in all_profiles:
                    # For each profile, check if it matches all tokens
                    matches_all_tokens = True

                    for token in tokens:
                        # Build a list of fields to check
                        fields_to_check = [
                            profile.user.first_name.lower(),
                            profile.user.last_name.lower(),
                            profile.user.email.lower(),
                            getattr(profile, 'job_title', '').lower(),
                            getattr(profile, 'department', '').lower(),
                            getattr(profile, 'college', '').lower(),
                            getattr(profile, 'honorific', '').lower(),
                            getattr(profile, 'preferred_name', '').lower(),
                        ]

                        # Special cases for department/college
                        department = getattr(profile, 'department', '').lower()
                        if department:
                            fields_to_check.append(department.replace('department of ', ''))

                        college = getattr(profile, 'college', '').lower()
                        if college:
                            fields_to_check.append(college.replace('college of ', ''))

                        # Check if any field matches this token
                        token_match = any(token in field for field in fields_to_check if field)

                        if not token_match:
                            matches_all_tokens = False
                            break

                    # If the profile matches all tokens, add it to results
                    if matches_all_tokens:
                        filtered_profiles.append(profile)

                # Use the Python-filtered results
                profiles_list = filtered_profiles
                logger.debug(f"Python filtering found {len(filtered_profiles)} results")


    # Convert to list if it's a queryset
    if hasattr(profiles_list, 'all'):
        profiles_count = profiles_list.count()
        # Apply sorting
        if sort_direction == 'desc':
            profiles_list = profiles_list.order_by('-user__first_name')
            logger.debug('Results sorted descending')
        else:  # asc
            profiles_list = profiles_list.order_by('user__first_name')
            logger.debug('Results sorted ascending')
        profiles_list = list(profiles_list)
    else:
        logger.warning('Unable to sort the results because they are not a queryset')
        profiles_count = len(profiles_list)

    # Number of profiles per page
    per_page = 12

    # Create paginator instance
    paginator = Paginator(profiles_list, per_page)

    # Get page number from request
    page = request.GET.get('page', 1)

    try:
        profiles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        profiles = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        profiles = paginator.page(paginator.num_pages)

    return render(request, 'profiles/home.html', {
        'profiles': profiles,
        'search_query': search_query,
        'total_results': profiles_count,
    })

def profile_detail(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    office_hours = OfficeHours.objects.filter(user=profile.user).first()
    course_hours = CourseOfficeHours.objects.filter(office_hours=office_hours) if office_hours else None
    
    return render(request, 'profiles/profile_detail.html', {
        'profile': profile,
        'office_hours': office_hours,
        'course_hours': course_hours,
    })

@login_required
def profile_edit(request):
    profile = request.user.userprofile
    old_image_path = None
    
    # Store the path to the old image if it exists
    if profile.profile_image:
        old_image_path = profile.profile_image.path if hasattr(profile.profile_image, 'path') else None
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Handle the case where the user is changing their profile image
            if 'profile_image' in request.FILES and old_image_path and os.path.isfile(old_image_path):
                try:
                    # Delete the old file manually as a backup
                    os.remove(old_image_path)
                except Exception as e:
                    # Log the error but continue with saving the form
                    print(f"Error removing old profile image: {e}")
            
            # Save the form with new data
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profiles:profile_detail', pk=profile.pk)
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'profiles/profile_edit.html', {'form': form})

@login_required
def office_hours_edit(request):
    office_hours, created = OfficeHours.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = OfficeHoursForm(request.POST, instance=office_hours)
        if form.is_valid():
            form.save()
            messages.success(request, 'Office hours updated successfully')
            return redirect('profiles:profile_detail', pk=request.user.userprofile.pk)
    else:
        # Prepare initial data safely handling missing time_slots
        initial_data = {
            'semester': office_hours.semester,
            'scheduling_link': office_hours.scheduling_link,
            'is_public': office_hours.is_public,
            'time_slots': json.dumps(office_hours.time_slots or []) # Time slots optional
        }
        form = OfficeHoursForm(instance=office_hours, initial=initial_data)
    
    return render(request, 'profiles/office_hours_edit.html', {'form': form})

@login_required
@login_required
def course_hours_add(request):
    office_hours, created = OfficeHours.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = CourseOfficeHoursForm(request.POST)
        if form.is_valid():
            course_hours = form.save(commit=False)
            course_hours.office_hours = office_hours

            course_hours.save()
            messages.success(request, 'Course office hours added successfully')
            return redirect('profiles:profile_detail', pk=request.user.userprofile.pk)
    else:
        form = CourseOfficeHoursForm(initial={'time_slots': '[]'})
    
    return render(request, 'profiles/course_hours_form.html', {
        'form': form,
        'action': 'Add'
    })

@login_required
def course_hours_edit(request, pk):
    course_hours = get_object_or_404(CourseOfficeHours, pk=pk)
    
    # Ensure user can only edit their own course hours
    if course_hours.office_hours.user != request.user:
        messages.error(request, "You don't have permission to edit these course hours.")
        return redirect('profiles:profile_detail', pk=request.user.userprofile.pk)
    
    if request.method == 'POST':
        form = CourseOfficeHoursForm(request.POST, instance=course_hours)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course office hours updated successfully')
            return redirect('profiles:profile_detail', pk=request.user.userprofile.pk)
    else:
        # Convert the time slots to JSON string for the form
        initial_data = {
            'course_name': course_hours.course_name,
            'course_description': course_hours.course_description,
            'time_slots': json.dumps(course_hours.time_slots)
        }
        form = CourseOfficeHoursForm(instance=course_hours, initial=initial_data)
    
    return render(request, 'profiles/course_hours_form.html', {
        'form': form,
        'action': 'Edit'
    })

@login_required
def course_hours_delete(request, pk):
    course_hours = get_object_or_404(CourseOfficeHours, pk=pk)
    
    # Ensure user can only delete their own course hours
    if course_hours.office_hours.user != request.user:
        messages.error(request, "You don't have permission to delete these course hours.")
        return redirect('profiles:profile_detail', pk=request.user.userprofile.pk)
    
    if request.method == 'POST':
        course_hours.delete()
        messages.success(request, 'Course office hours deleted successfully')
        return redirect('profiles:profile_detail', pk=request.user.userprofile.pk)
    
    return render(request, 'profiles/course_hours_confirm_delete.html', {
        'course_hours': course_hours
    })
