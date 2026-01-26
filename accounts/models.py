from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Custom user model.
    # Inheriting from AbstractUser keeps Django's default auth fields
    # and allows us to extend later (bio, avatar, etc.).
    pass