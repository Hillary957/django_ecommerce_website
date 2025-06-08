# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string
from django import forms

class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    email = models.EmailField(null=True)
    attempts = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
   



    def __str__(self):
        return f"OTP for {self.user.username}"

    @staticmethod
    def generate_otp():
        return ''.join(random.choices(string.digits, k=6))

    def is_expired(self):
        return timezone.now() > self.expires_at
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True, default="1234567890")  

    def __str__(self):
        return self.user.email
    


   