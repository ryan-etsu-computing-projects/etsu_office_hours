# profiles/urls.py
from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/<int:pk>/', views.profile_detail, name='profile_detail'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('office-hours/edit/', views.office_hours_edit, name='office_hours_edit'),
    path('course-hours/add/', views.course_hours_add, name='course_hours_add'),
    path('course-hours/edit/<int:pk>/', views.course_hours_edit, name='course_hours_edit'),
    path('course-hours/delete/<int:pk>/', views.course_hours_delete, name='course_hours_delete'),
]
