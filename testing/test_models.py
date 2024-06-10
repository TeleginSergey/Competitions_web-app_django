"""Module of testing models."""
from datetime import datetime, timedelta, timezone

from django.core.exceptions import ValidationError
from django.test import TestCase

from competition_app import models


def create_test(data_change):
    """
    Generate test that ensures ValidationError is raised when creating instance with modified data.

    Args:
        data_change (dict): A dictionary specifying the changes.

    Returns:
        function: A test function.
    """
    def new_test(self):
        """Test that checks if ValidationError is raised when creating an instance with modified data.

        Args:
            self: test case instance
        """
        data = self._creation_attrs.copy()
        for attr, value in data_change.items():
            data[attr] = value
        with self.assertRaises(ValidationError):
            self._model_class.objects.create(**data)
    return new_test


def create_test_save(data_change):
    """
    Generate test that ensures ValidationError is raised when saving instance with modified data.

    Args:
        data_change (dict): A dictionary specifying the changes.

    Returns:
        function: A test function.
    """
    def new_test(self):
        """Generate test that ensures ValidationError is raised when saving an instance with modified data.

        Args:
            self: test case instance
        """
        data = self._creation_attrs.copy()
        instance = self._model_class.objects.create(**data)
        for attr, value in data_change.items():
            setattr(instance, attr, value)
        with self.assertRaises(ValidationError):
            instance.save()
    return new_test


def create_model_test(model_class, creation_attrs, tests):
    """
    Create test cases for a model class with specified creation attributes and test configurations.

    Args:
        model_class (Model): The model class to be tested.
        creation_attrs (dict): The attributes to use for creating instances of the model.
        tests (list): A list of test configurations specifying changes to be made for test case.
    """
    class ModelTest(TestCase):
        """Test case class for the specified model."""

        _model_class = model_class
        _creation_attrs = creation_attrs

        def test_successful_creation(self):
            """Test successful creation of model instances."""
            self._model_class.objects.create(**self._creation_attrs)

    underscore = '_'
    for num, test in enumerate(tests):
        test_name = ''
        change_fields = {}
        for attr, value in test:
            change_fields[attr] = value
            test_name = attr + underscore
        setattr(ModelTest, f'test_create_{test_name}{num}', create_test(change_fields))
        setattr(ModelTest, f'test_save_{test_name}{num}', create_test_save(change_fields))


competition_attrs = {
    'title': 'ABCD',
    'date_of_start': datetime.today().date(),
    'date_of_end': datetime.today().date(),
}

sport_attrs = {
    'title': 'abcde',
    'description': 'Hello, world!',
}

tomorrow_datetime = datetime.now(timezone.utc) + timedelta(days=1)
today_datetime = datetime.now(timezone.utc)
tomorrow_date = datetime.now(timezone.utc).date() + timedelta(days=1)
today_date = datetime.now(timezone.utc).date()
yesterday_datetime = datetime.now(timezone.utc) - timedelta(days=1)
yesterday_date = datetime.now(timezone.utc).date() - timedelta(days=1)

competition_tests = (
    (
        ('created', tomorrow_datetime),
    ),
    (
        ('modified', tomorrow_datetime),
    ),
    (
        ('date_of_start', tomorrow_date),
        ('date_of_end', today_date),
    ),
    (
        ('created', today_datetime),
        ('modified', yesterday_datetime),
    ),
)

sport_tests = (
    (
        ('created', tomorrow_datetime),
    ),
    (
        ('modified', tomorrow_datetime),
    ),
    (
        ('created', today_datetime),
        ('modified', yesterday_datetime),
    ),
)

competition_sport_tests = (
    (
        ('created', tomorrow_datetime),
    ),
    (
        ('modified', tomorrow_datetime),
    ),
    (
        ('created', today_datetime),
        ('modified', yesterday_datetime),
    ),
)

client_tests = (
    (
        ('created', tomorrow_datetime),
    ),
    (
        ('modified', tomorrow_datetime),
    ),
    (
        ('created', today_datetime),
        ('modified', yesterday_datetime),
    ),
)

CompetitionModelTest = create_model_test(models.Competition, competition_attrs, competition_tests)
SportModelTest = create_model_test(models.Sport, sport_attrs, sport_tests)
CompetitionSportModelTest = create_model_test(models.CompetitionSport, {}, competition_tests)
ClientModelTest = create_model_test(models.Client, {}, client_tests)


class StageModelTest(TestCase):
    """Test case class for testing the Stage model."""

    _model_class = models.Stage

    @classmethod
    def setUpClass(cls):
        """Set up test data and create test cases for the Stage model class."""
        super().setUpClass()
        cls.tests = (
            (
                ('created', tomorrow_datetime),
            ),
            (
                ('modified', tomorrow_datetime),
            ),
            (
                ('created', today_datetime),
                ('modified', yesterday_datetime),
            ),
            (
                ('date', tomorrow_date),
            ),
            (
                ('date', yesterday_date),
            ),
        )
        cls.competition_attrs = {
            'title': 'stage_test_comp',
            'date_of_start': datetime.today().date(),
            'date_of_end': datetime.today().date(),
        }
        cls.sport_attrs = {
            'title': 'stage_test_sport',
            'description': 'Hello, world!',
        }
        competition = models.Competition.objects.create(**cls.competition_attrs)
        sport = models.Sport.objects.create(**cls.sport_attrs)
        sport.competitions.add(competition)
        competition_sport_obj = models.CompetitionSport.objects.get(
            competition=competition,
            sport=sport,
        )

        cls.stage_attrs = {
            'title': 'stage_test_stage',
            'date': datetime.today().date(),
            'competition_sport': competition_sport_obj,
        }
        underscore = '_'
        for num, test in enumerate(cls.tests):
            test_name = ''
            change_fields = {}
            for attr, value in test:
                change_fields[attr] = value
                test_name = attr + underscore
            setattr(cls, f'test_create_{test_name}{num}', create_test(change_fields))
            setattr(cls, f'test_save_{test_name}{num}', create_test_save(change_fields))

    def test_successful_creation(self):
        """Test the successful creation of a Stage instance."""
        self._model_class.objects.create(**self.stage_attrs)


# Validators

PAST_YEAR = 2007
FUTURE_YEAR = 3000

valid_tests = (
    (models.check_created, datetime(PAST_YEAR, 1, 1, 1, 1, 1, 1, tzinfo=timezone.utc)),
    (models.check_modified, datetime(PAST_YEAR, 1, 1, 1, 1, 1, 1, tzinfo=timezone.utc)),
)
invalid_tests = (
    (models.check_created, datetime(FUTURE_YEAR, 1, 1, 1, 1, 1, 1, tzinfo=timezone.utc)),
    (models.check_modified, datetime(FUTURE_YEAR, 1, 1, 1, 1, 1, 1, tzinfo=timezone.utc)),
)


def create_validation_test(validator, value, valid=True):
    """
    Create a validation test function based on the provided validator, value, and validity flag.

    Args:
        validator: The validator function to test.
        value: The value to be validated by the validator function.
        valid (bool): Flag indicating whether the value should pass validation.

    Returns:
        A test function that validates the value using the provided validator.
    """
    if valid:
        return lambda _: validator(value)

    def test(self):
        with self.assertRaises(ValidationError):
            validator(value)
    return test


valid_methods = {
    f'test_valid_{args[0].__name__}': create_validation_test(*args) for args in valid_tests
}
invalid_methods = {}

for args in invalid_tests:
    invalid_methods[f'test_invalid_{args[0].__name__}'] = create_validation_test(*args, valid=False)

TestValidators = type('TestValidators', (TestCase,), valid_methods | invalid_methods)


# __str__ methods

stage_attrs = {
    'title': 'BBBB',
    'date': datetime.today().date(),
}

test_str_data = (
    (models.Competition, competition_attrs, 'ABCD'),
    (models.Sport, sport_attrs, 'abcde'),
    (models.Stage, stage_attrs, 'BBBB'),
)


def create_str_test(model, attrs, expected):
    """
    Create a test function for checking the string representation of a model instance.

    Args:
        model: The model class for which the string representation is being tested.
        attrs (dict): Dictionary of attributes to create the model instance.
        expected (str): The expected string representation of the model instance.

    Returns:
        A test that creates a model instance with the attrs and checks its string representation.
    """
    def test(self):
        """
        Test the string representation of the model instance.

        This function creates a model instance with the provided attributes and asserts
        that its string representation matches the expected value.

        Args:
            self: test case instance
        """
        if model == models.Stage:
            local_competition_attrs = {
                'title': 'stage_test_comp',
                'date_of_start': today_date,
                'date_of_end': today_date,
            }
            local_sport_attrs = {
                'title': 'stage_test_sport',
                'description': 'Hello, world!',
            }
            competition = models.Competition.objects.create(**local_competition_attrs)
            sport = models.Sport.objects.create(**local_sport_attrs)
            sport.competitions.add(competition)
            competition_sport_obj = models.CompetitionSport.objects.get(
                competition=competition,
                sport=sport,
            )
            attrs['competition_sport'] = competition_sport_obj
        self.assertEqual(str(model.objects.create(**attrs)), expected)
    return test


test_str_methods = {}
for args in test_str_data:
    test_str_methods[f'test_{args[0].__name__}'] = create_str_test(*args)

TestStr = type('TestStr', (TestCase,), test_str_methods)


class TestLinks(TestCase):
    """Test of linking Competition and Sport models through CompetitionSport model."""

    def test_competition_sport(self):
        """Test the links between the Competition and Sport model instance."""
        competition = models.Competition.objects.create(**competition_attrs)
        sport = models.Sport.objects.create(**sport_attrs)
        competition.sports.add(sport)

        link = models.CompetitionSport.objects.get(competition=competition, sport=sport)

        self.assertEqual(str(link), f'Competition:{competition}\nSport:{sport}')
