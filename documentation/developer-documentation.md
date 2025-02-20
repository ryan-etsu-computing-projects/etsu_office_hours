# ETSU Office Hours Directory - Developer Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Setup and Installation](#setup-and-installation)
4. [Database Models](#database-models)
5. [User Management](#user-management)
6. [Profile Management](#profile-management)
7. [Office Hours Management](#office-hours-management)
8. [Search Functionality](#search-functionality)
9. [Security Features](#security-features)
10. [Management Commands](#management-commands)
11. [Customization](#customization)
12. [Troubleshooting](#troubleshooting)

## Overview

The ETSU Office Hours System is a Django-based web application designed to allow faculty and staff at East Tennessee State University to maintain profiles with their contact information and office hours. The system supports:

- User authentication with email-based login
- Profile management with personal and professional information
- Office hours scheduling with semester tracking
- Course-specific office hours
- Advanced search capabilities
- Bulk user uploads via CSV
- Administrative tools for user management

## System Architecture

The application follows a standard Django project structure with the following main components:

```
etsu_office_hours/
├── manage.py
├── etsu_office_hours/  # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/             # User authentication & management
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   └── templatetags/
├── profiles/          # Profile & office hours management
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   └── management/commands/
└── templates/         # HTML templates
    ├── base.html
    ├── users/
    └── profiles/
```

The application uses:
- **Django** as the web framework
- **django-encrypted-model-fields** for data security
- **Bootstrap** for frontend styling
- **SQLite** (development) or a production database like PostgreSQL

## Setup and Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)
- Git

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd etsu_office_hours
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate a new secret key**
   ```python
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```
   Copy the output and update the SECRET_KEY in settings.py

5. **Setup the database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin user (a UserProfile will be created automatically)

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```
   The application will be available at http://127.0.0.1:8000/

### Production Deployment Considerations

For production deployment:

1. **Update settings.py**
   - Set `DEBUG = False`
   - Update `ALLOWED_HOSTS`
   - Configure a production database (PostgreSQL recommended)
   - Setup proper email settings
   - Configure static files serving

2. **Set up a web server**
   - Use Gunicorn or uWSGI as the application server
   - Configure Nginx or Apache as the web server
   - Set up HTTPS with Let's Encrypt

3. **Create .env file**
   - Store sensitive settings like SECRET_KEY and database credentials
   - Use django-environ to load settings from .env

## Database Models

### User Models

#### EncryptedUser (users/models.py)
Extends Django's AbstractUser with email-based authentication:
- `email` (unique, used as username)
- `first_name` (encrypted)
- `last_name` (encrypted)
- Standard Django user fields (is_active, is_staff, etc.)

### Profile Models

#### UserProfile (profiles/models.py)
Contains user's personal and professional information:
- `user` (OneToOneField to EncryptedUser)
- `preferred_name` (encrypted, optional)
- `honorific` (encrypted, optional) - e.g., Dr., Prof., Mr., Ms.
- `pronouns` (encrypted, optional)
- `bio` (encrypted, optional)
- `phone` (encrypted, optional)
- `profile_image` (optional)
- `job_title` (encrypted, optional)
- `department` (encrypted, optional)
- `college` (encrypted, optional)
- `office_building` (encrypted, optional)
- `office_room` (encrypted, optional)

#### OfficeHours (profiles/models.py)
Stores general office hours information:
- `user` (OneToOneField to EncryptedUser)
- `semester` (e.g., "Spring 2025")
- `scheduling_link` (optional URL)
- `is_public` (boolean, default True)
- `time_slots` (JSONField storing days/times)
- `created_at`, `updated_at` (timestamps)

#### CourseOfficeHours (profiles/models.py)
Stores course-specific office hours:
- `office_hours` (ForeignKey to OfficeHours)
- `course_name`
- `course_description` (optional)
- `time_slots` (JSONField storing days/times)

## User Management

### Creating Users

#### Method 1: Admin Interface
1. Navigate to http://127.0.0.1:8000/admin/
2. Log in with a superuser account
3. While direct user creation in admin is disabled, you can edit existing users

#### Method 2: User Management Interface
1. Navigate to http://127.0.0.1:8000/users/manage/
2. Click "Add Single User"
3. Fill in the required information
4. The user will receive an email with login instructions

#### Method 3: CSV Upload
1. Navigate to http://127.0.0.1:8000/users/manage/
2. Click "Bulk Upload CSV"
3. Prepare a CSV file with columns:
   - email (required)
   - first_name (required)
   - last_name (required)
   - classification (required: "Faculty" or "Staff")
   - honorific (optional)
   - job_title (optional)
   - department (optional)
   - college (optional)
   - office_building (optional)
   - office_room (optional)
4. Upload the CSV
5. Users will receive emails with login instructions

### User Lifecycle Management

- **Account Activation**: Users can activate their account via password reset link
- **Inactivity Handling**: Accounts inactive for over 18 months are automatically deactivated
- **Notifications**: Users inactive for 12 months receive reminders to log in
- **Password Reset**: Self-service password reset via email

## Profile Management

### Profile Editing

Users can update their profiles at http://127.0.0.1:8000/profile/edit/

Fields include:
- Honorific (Dr., Prof., etc.)
- Preferred name
- Pronouns
- Phone number
- Bio
- Profile image
- Job title
- Department
- College
- Office building and room

### Profile Images

Profile images:
- Are automatically renamed using a standardized format
- Use the custom `OverwriteStorage` class to replace old images
- Support common formats (JPEG, PNG)
- Have file size and dimension limits

## Office Hours Management

### General Office Hours

Users can manage their general office hours at http://127.0.0.1:8000/office-hours/edit/

Features:
- Set time slots with day, start time, and end time
- Mark hours as public or private
- Set the semester (Spring, Summer, Fall, Winter)
- Add scheduling links (e.g., Calendly, Microsoft Booking)

### Course-Specific Office Hours

Users can add course-specific office hours at http://127.0.0.1:8000/course-hours/add/

Features:
- Associate hours with specific courses
- Add course descriptions
- Set different time slots for each course
- Edit or delete course hours

## Search Functionality

The system includes an advanced search system:

### Search Features

- **Token-based searching**: Handles multi-word queries (e.g., "ryan haas computing")
- **Field flexibility**: Searches across multiple fields (name, email, department, etc.)
- **Prefix handling**: Intelligently handles department/college prefixes
- **Case insensitivity**: All searches are case-insensitive
- **Pagination**: Results are paginated for performance
- **Fallback mechanism**: Uses Python-based filtering as a backup

### Search Implementation

The search combines database queries with Python filtering to handle encrypted fields properly:
1. Splits search query into tokens
2. Progressively filters results by each token
3. Falls back to Python filtering if database queries return no results

## Security Features

### Data Encryption

- User personal data is encrypted using django-encrypted-model-fields
- Fields like names, contact details, and profile information are stored encrypted in the database

### Authentication

- Email-based authentication instead of usernames
- Password reset tokens with limited validity
- Automatic account deactivation for long-term inactive users

### Permission Controls

- Staff-only access to user management features
- Users can only edit their own profiles and office hours
- Token-based password reset for security

## Management Commands

### create_missing_profiles

Creates UserProfile objects for users that don't have them:

```bash
python manage.py create_missing_profiles
```

Use this command if you have users created outside the normal flow (e.g., via Django shell).

### check_inactive_users

Checks for inactive users and sends notifications:

```bash
python manage.py check_inactive_users
```

This command:
- Deactivates users inactive for 18+ months
- Sends notification emails to users inactive for 12+ months

It should be run as a scheduled task (e.g., daily cron job).

## Customization

### Adding New Fields

To add new profile fields:

1. Update the UserProfile model in profiles/models.py
2. Create and run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
3. Update the ProfileForm in profiles/forms.py
4. Update templates to display the new fields

### Styling Customization

The application uses Bootstrap for styling:
- Main templates extend base.html
- CSS customizations can be added to static/css/custom.css
- Bootstrap classes are used throughout for consistent styling

## Troubleshooting

### Common Issues

#### Search Not Working Properly
- Check if encrypted fields are properly indexed
- Verify that django-encrypted-model-fields is properly configured
- Enable DEBUG logging to see SQL queries

#### Image Upload Issues
- Check MEDIA_ROOT and MEDIA_URL settings
- Ensure the media directory is writable
- Verify the OverwriteStorage class is working correctly

#### Email Sending Failures
- Check EMAIL_* settings in settings.py
- Verify SMTP server connectivity
- Check spam filters if emails aren't being received

### Logging

Enable detailed logging by adding to settings.py:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'profiles': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'users': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
```

### Getting Help

If you encounter issues:
1. Check the logs for error messages
2. Review the Django documentation
3. Check for database migration issues
4. Contact the project maintainer at [haasrr@etsu.edu](mailto:haasrr@etsu.edu)
