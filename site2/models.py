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






class QuizQuestion(models.Model):
    _id = models.ObjectIdField(primary_key = True)
    category = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=10)
    question = models.TextField()
    option_a = models.TextField(default='')
    option_b = models.TextField(default='')
    option_c = models.TextField(default='')
    option_d = models.TextField(default='')
    answer = models.CharField(max_length=1)  # Assuming answer is a single character (a, b, c, or d)

    def __str__(self):
        return f"{self.category} - {self.difficulty} - {self.question}"



class Question(models.Model):
    q_text = models.CharField(max_length=255)
    is_correct = models.BooleanField() 
    

class QuizHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    domain = models.CharField(max_length=255)
    score = models.IntegerField()
    submission_time = models.DateTimeField(auto_now_add=True)
    attempted_questions = models.ManyToManyField(Question)

    def __str__(self):
        return f"{self.user.username}'s Quiz History"
