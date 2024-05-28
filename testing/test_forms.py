from django.test import TestCase
from django.contrib.auth.models import User

from competition_app.forms import RegistrationForm


class RegistrationFormTest(TestCase):
    _valid_data = {
        'username': 'username',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email@email.com',
        'password1': 'Azpm1029!',
        'password2': 'Azpm1029!',
    }

    def test_valid(self):
        self.assertTrue(RegistrationForm(data=self._valid_data).is_valid())

    def invalid(self, invalid_data):
        data = self._valid_data.copy()
        for field, value in invalid_data:
            data[field] = value
        self.assertFalse(RegistrationForm(data=data).is_valid())

    def test_short_password(self):
        self.invalid(
            (
                ('password1', 'abc'),
                ('password2', 'abc'),
            )
        )

    def test_common_password(self):
        self.invalid(
            (
                ('password1', 'abcdef123'),
                ('password2', 'abcdef123'),
            )
        )

    def test_different_passwords(self):
        self.invalid(
            (
                ('password1', 'ASDksdjn9734'),
                ('password2', 'LKKJdfnalnd234329'),
            )
        )
    
    def test_invalid_email(self):
        self.invalid(
            (
                ('email', 'abc'),
            )
        )

    def test_existing_user(self):
        username, password = 'username', 'password'
        User.objects.create(username=username, password=password)
        self.invalid(
            (
                ('username', username),
                ('password', password),
            )
        )
