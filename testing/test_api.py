"""Module for testing website's rest api."""
from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from competition_app import models


def create_apitest(model_class, model_url, creation_attrs):
    """
    Dynamically create a custom TestCase class for testing API endpoints.

    Args:
        model_class (class): The model class to be tested.
        model_url (str): The URL endpoint for the model.
        creation_attrs (dict): Dictionary containing args for creating instances of the model.

    Returns:
        APITest (class): Custom TestCase class for testing API endpoints.
    """
    class APITest(TestCase):
        """Custom TestCase class for testing API endpoints."""

        _user_creds = {'username': 'abc', 'password': 'abc'}
        _superuser_creds = {
            'username': 'def',
            'password': 'def',
            'is_superuser': True,
        }

        @classmethod
        def setUpClass(cls):
            """Set up method to prepare common data for the test cases."""
            super().setUpClass()
            competition_attrs = {
                'title': 'stage_test_comp',
                'date_of_start': datetime.today().date(),
                'date_of_end': datetime.today().date(),
            }
            sport_attrs = {
                'title': 'stage_test_sport',
                'description': 'Hello, world!',
            }
            competition = models.Competition.objects.create(**competition_attrs)
            sport = models.Sport.objects.create(**sport_attrs)
            sport.competitions.add(competition)
            cls._competition_sport_obj = models.CompetitionSport.objects.get(
                competition=competition,
                sport=sport,
            )

        def setUp(self):
            """Set up method to prepare data required for each individual test case."""
            self.client = APIClient()
            self.user = User.objects.create(**self._user_creds)
            self.user_token = Token.objects.create(user=self.user)
            self.superuser = User.objects.create(**self._superuser_creds)
            self.superuser_token = Token.objects.create(user=self.superuser)

        def get(self, user: User, token: Token):
            """
            Test method to perform GET request on the API endpoint.

            Args:
                user (User): User object for authentication.
                token (Token): Token object for authentication.
            """
            self.client.force_authenticate(user=user, token=token)
            response = self.client.get(model_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        def test_get_user(self):
            """Test case for performing GET request as a regular user."""
            self.get(self.user, self.user_token)

        def test_get_superuser(self):
            """Test case for performing GET request as a superuser."""
            self.get(self.superuser, self.superuser_token)

        def manage(
            self,
            user: User,
            token: Token,
            post_status: int,
            put_status: int,
            delete_status: int,
        ):
            """
            Test method to manage CRUD operations on the API endpoint.

            Args:
                user (User): User object for authentication.
                token (Token): Token object for authentication.
                post_status (int): Expected status code for POST request.
                put_status (int): Expected status code for PUT request.
                delete_status (int): Expected status code for DELETE request.
            """
            self.client.force_authenticate(user=user, token=token)

            if model_class == models.Stage:
                creation_attrs['competition_sport'] = self._competition_sport_obj.id

            response = self.client.post(model_url, creation_attrs)
            self.assertEqual(response.status_code, post_status)

            if post_status == status.HTTP_201_CREATED:
                created_obj = model_class.objects.get(**creation_attrs)
                url = f'{model_url}{created_obj.id}/'
            else:
                url = f'{model_url}1/'

            response = self.client.put(url, creation_attrs)
            self.assertEqual(response.status_code, put_status)

            response = self.client.delete(url)
            self.assertEqual(response.status_code, delete_status)

        def test_manage_user(self):
            """Test case for managing CRUD operations as a regular user."""
            self.manage(
                self.user, self.user_token,
                status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN,
            )

        def test_manage_superuser(self):
            """Test case for managing CRUD operations as a superuser."""
            self.manage(
                self.superuser, self.superuser_token,
                status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_204_NO_CONTENT,
            )

    return APITest


CompetitionApiTest = create_apitest(
    models.Competition,
    '/api/competitions/',
    {'title': 'unique_competition_title'},
)
SportApiTest = create_apitest(models.Sport, '/api/sports/', {'title': 'unique_sport_title'})
StageApiTest = create_apitest(models.Stage, '/api/stages/', {'title': 'unique_stage_title'})
