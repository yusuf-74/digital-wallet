from datetime import timedelta

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utils.data_generators import generate_otp
from wallets.models import Tier

numeric_validator = RegexValidator(r'^\d{6}$', _('Enter a 6-digit numeric password.'))


class UsersManager(BaseUserManager):
    def _create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone number field must be set')
        try:
            numeric_validator(password)
        except Exception:
            raise ValueError('Password must be a 6-digit numeric value.')

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # User identification
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, unique=True)
    password = models.CharField(
        _("password"), max_length=128, validators=[numeric_validator], help_text=_("Enter a 6-digit numeric password.")
    )
    date_of_birth = models.DateField()
    tier = models.ForeignKey(
        Tier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user',
        help_text=_('The tier assigned to the user for transaction limits'),
    )

    # Roles and status
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UsersManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'date_of_birth']

    def has_perm(self, perm) -> bool:
        if super().has_perm(perm):
            return True
        all_perms = self.get_all_permissions()
        all_perms = set([p.split('.')[1] for p in all_perms])
        return perm in all_perms

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes')
    code = models.CharField(max_length=6, validators=[numeric_validator])
    is_used = models.BooleanField(default=False, help_text="Indicates if the OTP has been used")
    expires_at = models.DateTimeField(help_text="OTP expiration time")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.user.phone_number} - {self.code}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_otp()
            max_attempts = 6
            while OTP.objects.filter(code=self.code).exists() and max_attempts:
                self.code = generate_otp()
                max_attempts -= 1
            if max_attempts == 0:
                raise ValueError("Failed to generate a unique OTP after multiple attempts.")
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() > self.expires_at

    def mark_as_used(self):
        self.is_used = True
        self.save()

    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"
        ordering = ['-created_at']  # Newest OTPs first
