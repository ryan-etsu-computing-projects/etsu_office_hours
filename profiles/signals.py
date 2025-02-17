# profiles/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import EncryptedUser
from .models import UserProfile

@receiver(post_save, sender=EncryptedUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile whenever an EncryptedUser is created."""
    if created:
        UserProfile.objects.create(user=instance)

# profiles/apps.py
from django.apps import AppConfig

class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles'

    def ready(self):
        import profiles.signals  # Import the signals