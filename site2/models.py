from django.contrib.auth.models import AbstractUser
from djongo import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length = 100, null=True, blank=False,unique=True)
    password = models.CharField(max_length = 100, null=True, blank=False)
    first_name = models.CharField(max_length = 100, null=True, blank=False)
    last_name = models.CharField(max_length = 100, null=True, blank=False)
    # Add custom fields here, if needed

    def __str__(self):
        return self.username
