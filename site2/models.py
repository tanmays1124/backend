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


from django.db import models

class QuizQuestion(models.Model):
    # Assuming _id is an ObjectId in MongoDB, you can use Django's AutoField
    # to automatically generate a unique ID for each question.
    _id = models.AutoField(primary_key=True)

    category = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=10)
    question = models.TextField()
    options = models.JSONField(default=list)  # Use JSONField for storing the list of options
    answer = models.IntegerField()

    def __str__(self):
        return f"{self.category} - {self.difficulty} - {self.question}"
