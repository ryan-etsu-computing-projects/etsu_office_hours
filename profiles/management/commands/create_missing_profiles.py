# profiles/management/commands/create_missing_profiles.py
from django.core.management.base import BaseCommand
from users.models import EncryptedUser
from profiles.models import UserProfile

class Command(BaseCommand):
    help = 'Creates UserProfile objects for users that don\'t have them'

    def handle(self, *args, **options):
        users_without_profiles = EncryptedUser.objects.filter(userprofile__isnull=True)
        count = 0
        
        for user in users_without_profiles:
            UserProfile.objects.create(user=user)
            count += 1
            self.stdout.write(f'Created profile for {user.email}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} user profiles'))