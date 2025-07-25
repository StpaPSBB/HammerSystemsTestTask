from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
import string
import secrets

class CustomUserManager(BaseUserManager):
    """
    Creates and saves a User with the given phone number.
    """
    def create_user(self, phone_number, **extra_fields):
        if not phone_number:
            raise ValueError('The phone number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, **extra_fields):
        return self.create_user(phone_number, **extra_fields)

class User(AbstractBaseUser):
    """
    User model for referral system.
    """
    phone_number = models.CharField(max_length=15, unique=True, validators=[RegexValidator(regex=r'^\+\d{9,15}$',
                                                                                            message="Phone number must be in international format (e.g. +79991234567)")])
    self_invite_code = models.CharField(max_length=6, unique=True, blank=True)
    activated_invite_code = models.CharField(max_length=6, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'

    def save(self, *args, **kwargs):
        if not self.self_invite_code:
            self.self_invite_code = self._generate_invite_code()
        super().save(*args, **kwargs)

    def _generate_invite_code(self):
        """
        Generates 6-chars uniq code.
        """
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(alphabet) for _ in range(6))
            if not User.objects.filter(self_invite_code=code).exists():
                return code
            
    class Meta:
        verbose_name='User'
        verbose_name_plural='Users'