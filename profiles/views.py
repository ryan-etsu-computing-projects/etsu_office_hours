from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, OfficeHours, CourseOfficeHours
from .forms import ProfileForm, OfficeHoursForm, CourseOfficeHoursForm
import json
import logging

logger = logging.getLogger(__name__)

def home(request):
    profiles = UserProfile.objects.select_related('user').all()
    return render(request, 'profiles/home.html', {'profiles': profiles})

def profile_detail(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    office_hours = OfficeHours.objects.filter(user=profile.user).first()
    course_hours = CourseOfficeHours.objects.filter(office_hours=office_hours) if office_hours else None
    
    # Debug logging
    if course_hours:
        for course in course_hours:
            print(f"Course: {course.course_name}")
            print(f"Time slots: {course.time_slots}")
    
    return render(request, 'profiles/profile_detail.html', {
        'profile': profile,
        'office_hours': office_hours,
        'course_hours': course_hours,
    })

@login_required
def profile_edit(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
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
        form = OfficeHoursForm(instance=office_hours)
    
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
            print(f"Loading time slots: {course_hours.time_slots}")

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
    print(f"Loading time slots: {course_hours.time_slots}")
    
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
