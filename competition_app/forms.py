"""
Module for defining forms used in the Django project.

This module contains form classes for handling user registration, login,
data input, and other form-related functionalities within the Django project.
"""
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import CharField


class RegistrationForm(UserCreationForm):
    """Form for user registration with username, first name, last name, email and password."""

    first_name = CharField(max_length=100, required=True)
    last_name = CharField(max_length=100, required=True)
    email = CharField(max_length=100, required=True)

    class Meta:
        """Meta class specifying the model and fields to be included in the form."""

        model = User
        fields = [
            'username', 'first_name', 'last_name',
            'email', 'password1', 'password2',
        ]
