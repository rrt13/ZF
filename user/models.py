from django.db import models
from .managers import CustomUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
import binascii, os

# Create your models here.

role_choices = [('user', 'User'), ('advisor', 'Advisor'), ('admin', 'Admin')]

#Custom User
class User(AbstractBaseUser):
    id = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=150, blank=True,null=True)
    phone_number = models.CharField(max_length=10,unique=True)
    role = models.CharField(choices=role_choices, default='user', max_length=10)

    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['role']

    objects = CustomUserManager()

    class Meta:
        db_table = 'Users'
        
    def __str__(self):
        return self.phone_number

class OTP(models.Model):
    id = models.BigAutoField(primary_key=True)
    phone_number = models.CharField(max_length=15)
    otp_value = models.CharField(max_length=6)
    expiration_time = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    use_case = models.CharField(max_length=60, blank=True,null=True) # (account creation, payment etc) -> future case
    
    def is_expired(self):
        return self.expiration_time < timezone.now()

    def is_valid(self):
        return not self.is_used and not self.is_expired()

    def __str__(self):
        return f'OTP: {self.otp_value} for {self.phone_number}'

# Custom Token Authentication
class Token(models.Model):
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(_("Key"), max_length=40, unique=True)
    user = models.ForeignKey(User, related_name='auth_user', on_delete=models.CASCADE, verbose_name="user")
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    device_key = models.CharField(max_length=450, blank=True, null=True)
    
    class Meta:
        db_table = 'AuthToken'
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")
        unique_together = ['key', 'user', 'device_key']

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
    
class AdvisorClient(models.Model):
    id = models.BigAutoField(primary_key=True)
    advisor = models.ForeignKey(User, related_name='advisor', on_delete=models.CASCADE)
    client = models.ForeignKey(User, related_name='clients', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    #I'll add more fields in the future in order to maintain a history
    #for eg, if an advisor is changed for a client, so when was it, to whom it is shifted etc
    
    class Meta:
        unique_together = ('advisor', 'client')

    def __str__(self):
        return f'{self.advisor.phone_number} - {self.client.phone_number}'