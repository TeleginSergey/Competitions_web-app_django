"""Module that tests forms."""
from django.contrib.auth.models import User
from django.test import TestCase

from competition_app.forms import RegistrationForm


class RegistrationFormTest(TestCase):
    """Test case for the RegistrationForm class."""

    _valid_data = {
        'username': 'username',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email@email.com',
        'password1': 'Azpm1029!',
        'password2': 'Azpm1029!',
    }

    def test_valid(self):
        """Test for validating the registration form with valid data."""
        self.assertTrue(RegistrationForm(data=self._valid_data).is_valid())

    def invalid(self, invalid_data):
        """
        Test for validating the registration form with invalid data.

        Args:
            invalid_data: A tuple containing field-value pairs of invalid data.
        """
        data = self._valid_data.copy()
        for field, value in invalid_data:
            data[field] = value
        self.assertFalse(RegistrationForm(data=data).is_valid())

    def test_short_password(self):
        """Test for validating the registration form with a short password."""
        self.invalid(
            (
                ('password1', 'abc'),
                ('password2', 'abc'),
            ),
        )

    def test_common_password(self):
        """Test for validating the registration form with a common password."""
        self.invalid(
            (
                ('password1', 'abcdef123'),
                ('password2', 'abcdef123'),
            ),
        )

    def test_different_passwords(self):
        """Test for validating the registration form with different passwords."""
        self.invalid(
            (
                ('password1', 'ASDksdjn9734'),
                ('password2', 'LKKJdfnalnd234329'),
            ),
        )

    def test_invalid_email(self):
        """Test for validating the registration form with an invalid email."""
        self.invalid(
            (
                ('email', 'abc'),
            ),
        )

    def test_existing_user(self):
        """Test for validating the registration form with an existing user."""
        username, password = 'username', 'password'
        User.objects.create(username=username, password=password)
        self.invalid(
            (
                ('username', username),
                ('password', password),
            ),
        )
