
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    mobile = models.CharField(max_length=10, unique=True, validators=[RegexValidator(
        regex=r"^\d{10}", message="Phone number must be 10 digits only.")])
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['name', 'first_name', 'last_name']

    email = models.EmailField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    spend_available = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    is_partner = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class AuthOTP(models.Model):
    mobile = models.CharField(max_length=10, validators=[RegexValidator(
        regex=r"^\d{10}", message="Phone number must be 10 digits only.")])
    otp = models.CharField(max_length=6)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.otp
