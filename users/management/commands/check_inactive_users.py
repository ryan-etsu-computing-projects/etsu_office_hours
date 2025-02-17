from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from users.models import EncryptedUser

class Command(BaseCommand):
    help = 'Check for inactive users and send notifications'

    def handle(self, *args, **kwargs):
        users = EncryptedUser.objects.filter(is_active=True)
        
        for user in users:
            if user.should_deactivate():
                user.is_active = False
                user.save()
                self.stdout.write(f'Deactivated user: {user.email}')
                
            elif user.should_notify():
                send_mail(
                    'Account Inactivity Notice',
                    'Please log in to keep your account active.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                self.stdout.write(f'Sent notification to: {user.email}')
