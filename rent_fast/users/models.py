from django.db import models

# Create your models here.
class Users(models.Model):
username = models.CharField(max_length=150, unique=True)
email = models.EmailField(unique=True)
first_name = models.CharField(max_length=30)
last_name = models.CharField(max_length=30)= models.DateTimeField(auto_now_add=True)
def __str__(self):
return self.username

