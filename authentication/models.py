from django.contrib.auth.models import AbstractUser
from django.db import models
import string,random
from django.conf import settings
from django.utils import timezone
from datetime import timedelta



class CustomUser(AbstractUser):
    admission_number = models.CharField(max_length=20, unique=True)
    image = models.ImageField(upload_to='profile/pictures/', default='/profile/pictures/prof.png')

     # new field
    has_voted = models.BooleanField(default=False) # to track if user has voted
    is_verified = models.BooleanField(default=False) # to track if user is verified via OTP
    def __str__(self):
        return f"{self.first_name} {self.last_name}-{self.admission_number}"
# voting IDs
def generate_voting_id(length=6):
    """Generate a random voting ID consisting of uppercase letters and digits."""
    characters = list(string.ascii_uppercase + string.digits)
    idn = random.sample(characters, length)
    voting_id = f"BTTI{''.join(idn)}"
    return voting_id



def default_end_datetime():
    return timezone.now() + timedelta(minutes=5)

def TimeStampedModel():
    return timezone.now()

class VotingID(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    voting_id = models.CharField(max_length=20, unique=True,blank=True,null=True)
    created_at = models.DateTimeField(default=TimeStampedModel)
    expires_at = models.DateTimeField(default=default_end_datetime)
    is_active = models.BooleanField(default=True)
    

    def save(self, *args, **kwargs):
        if not self.voting_id:
            self.voting_id = generate_voting_id()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"VotingID for {self.user.username}: {self.voting_id}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
# model to store admssion numbers
class AdmissionNumber(models.Model):
    admission_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.full_name

def generate_otp():
    import random
    return str(random.randint(100000, 999999))
    
class otp(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_otp()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OTP for {self.user.username}: {self.code}"
    
# audit log model
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("REGISTER", "User Registration"),
        ("LOGIN", "User Login"),
        ("LOGOUT", "User Logout"),
        ("VOTE", "Vote Cast"),
        ("OTP_VERIFY", "OTP Verification"),
        ("ADMIN_ACTION", "Admin Action"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=5000, choices=ACTION_CHOICES)
    description = models.TextField()  # Custom message
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"   