from django.forms import CharField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    first_name = CharField(max_length=100, required=True)
    last_name = CharField(max_length=100, required=True)
    email = CharField(max_length=100, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name',
            'email', 'password1', 'password2',
        ]
