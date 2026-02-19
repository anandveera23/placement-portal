from django.db import models

# Create your models here.
from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=255)
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text
class CodingQuestion(models.Model):
    title = models.CharField(max_length=200)
    problem_statement = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()

    test_input = models.TextField(default="")
    expected_output = models.TextField(default="")

    def __str__(self):
        return self.title

from django.contrib.auth.models import User

class MCQResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.score}/{self.total}"
