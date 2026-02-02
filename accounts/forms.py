from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignupForm(UserCreationForm):
    """
    User registration form.
    We extend Django's built-in UserCreationForm to add an email field.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")