from django.db import models

class UserData(models.Model):
    user_id = models.CharField(max_length=6)
    date = models.DateField()
    data = models.TextField()
