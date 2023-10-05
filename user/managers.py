from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, role='user'):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        if len(phone_number)!=10:
            raise ValueError('The Phone Number should be of 10 digits')
        
        user = self.model(phone_number=phone_number, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, password=None,role='admin',is_staff=True):
        return self.create_user(phone_number, password, role=role)