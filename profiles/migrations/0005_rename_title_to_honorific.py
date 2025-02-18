from django.db import migrations, models

def forward_func(apps, schema_editor):
    """Transfer data from title to honorific."""
    UserProfile = apps.get_model('profiles', 'UserProfile')
    for profile in UserProfile.objects.all():
        profile.honorific = profile.title
        profile.save()

def reverse_func(apps, schema_editor):
    """Transfer data from honorific back to title."""
    UserProfile = apps.get_model('profiles', 'UserProfile')
    for profile in UserProfile.objects.all():
        profile.title = profile.honorific
        profile.save()

class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_alter_userprofile_profile_image'),  # Replace with the last migration
    ]

    operations = [
        # First add the new honorific field
        migrations.AddField(
            model_name='userprofile',
            name='honorific',
            field=models.CharField(blank=True, max_length=50),
        ),
        # Transfer data
        migrations.RunPython(forward_func, reverse_func),
        # Remove the old title field
        migrations.RemoveField(
            model_name='userprofile',
            name='title',
        ),
    ]