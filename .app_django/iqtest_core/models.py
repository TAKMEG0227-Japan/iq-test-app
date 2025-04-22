from django.db import models

class Result(models.Model):
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    question_id = models.CharField(max_length=10)
    selected = models.CharField(max_length=1)
    correct = models.CharField(max_length=1)
    is_correct = models.BooleanField()
    datetime = models.DateTimeField(auto_now_add=True)
