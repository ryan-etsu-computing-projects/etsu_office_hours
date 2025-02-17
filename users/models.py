# users/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField
from django.utils import timezone
from dateutil.relativedelta import relativedelta

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class EncryptedUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    first_name = EncryptedCharField(max_length=150)
    last_name = EncryptedCharField(max_length=150)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def should_deactivate(self):
        if not self.last_login:
            return False
        return (timezone.now() - self.last_login) > relativedelta(months=18)

    def should_notify(self):
        if not self.last_login:
            return False
        return (timezone.now() - self.last_login) > relativedelta(years=1)
