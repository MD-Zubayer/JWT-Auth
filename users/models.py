from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    username = None
    password = models.CharField(max_length=128)
    REQUIRED_FIELDS = []

    objects = UserManager()