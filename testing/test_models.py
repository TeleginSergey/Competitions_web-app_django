from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import datetime, timezone, timedelta

from competition_app import models

def create_test(data_change):
    def new_test(self):
        data = self._creation_attrs.copy()
        for attr, value in data_change.items():
            data[attr] = value
        with self.assertRaises(ValidationError):
            self._model_class.objects.create(**data)
    return new_test


def create_test_save(data_change):
    def new_test(self):
        data = self._creation_attrs.copy()
        instance = self._model_class.objects.create(**data)
        for attr, value in data_change.items():
            setattr(instance, attr, value)
        with self.assertRaises(ValidationError):
            instance.save()
    return new_test


def create_model_test(model_class, creation_attrs, tests):
    class ModelTest(TestCase):
        _model_class = model_class
        _creation_attrs = creation_attrs

        def test_successful_creation(self):
            self._model_class.objects.create(**self._creation_attrs)

    for num, test in enumerate(tests):
        test_name = ''
        change_fields = dict()
        for attr, value in test:
            change_fields[attr] = value
            test_name = attr + '_' 
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

competition_tests = (
    (
        ('created', datetime.now(timezone.utc) + timedelta(days=1)),
    ),
    (
        ('modified', datetime.now(timezone.utc) + timedelta(days=1)),
    ),
    (
        ('date_of_start', datetime.now(timezone.utc).date() + timedelta(days=1)),
        ('date_of_end', datetime.now(timezone.utc).date()),
    ),
    (
        ('created', datetime.now(timezone.utc) + timedelta(days=1)),
        ('modified', datetime.now(timezone.utc)),
    ),
)

sport_tests = (
    (
        ('created', datetime.now(timezone.utc) + timedelta(days=1)),
    ),
    (
        ('modified', datetime.now(timezone.utc) + timedelta(days=1)),
    ),
    (
        ('created', datetime.now(timezone.utc) + timedelta(days=1)),
        ('modified', datetime.now(timezone.utc)),
    ),
)

competition_sport_tests = (
    (
        ('created', datetime.now(timezone.utc) + timedelta(days=1)),
    ),
    (
        ('modified', datetime.now(timezone.utc) + timedelta(days=1)),
    ),
    (
        ('created', datetime.now(timezone.utc) + timedelta(days=1)),
        ('modified', datetime.now(timezone.utc)),
    ),
)

client_tests = (
    (
        ('created', datetime.now(timezone.utc) + timedelta(days=1)),
    ),
    (
        ('modified', datetime.now(timezone.utc) + timedelta(days=1)),
    ),
    (
        ('created', datetime.now(timezone.utc) + timedelta(days=1)),
        ('modified', datetime.now(timezone.utc)),
    ),
)

CompetitionModelTest = create_model_test(models.Competition, competition_attrs, competition_tests)
SportModelTest = create_model_test(models.Sport, sport_attrs, sport_tests)
CompetitionSportModelTest = create_model_test(models.CompetitionSport, {}, competition_tests)
ClientModelTest = create_model_test(models.Client, {}, client_tests)




class StageModelTest(TestCase):
    _model_class = models.Stage
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tests = (
            (
                ('created', datetime.now(timezone.utc) + timedelta(days=1)),
            ),
            (
                ('modified', datetime.now(timezone.utc) + timedelta(days=1)),
            ),
            (
                ('created', datetime.now(timezone.utc) + timedelta(days=1)),
                ('modified', datetime.now(timezone.utc)),
            ),
            (
                ('date', datetime.now(timezone.utc).date() + timedelta(days=1)),
            ),
            (
                ('date', datetime.now(timezone.utc).date() - timedelta(days=1)),
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
        competition_sport_obj = models.CompetitionSport.objects.get(competition=competition, sport=sport)

        cls.stage_attrs = {
            'title': 'stage_test_stage',
            'date': datetime.today().date(),
            'competition_sport': competition_sport_obj,
        }

        for num, test in enumerate(cls.tests):
            test_name = ''
            change_fields = dict()
            for attr, value in test:
                change_fields[attr] = value
                test_name = attr + '_' 
            setattr(cls, f'test_create_{test_name}{num}', create_test(change_fields))
            setattr(cls, f'test_save_{test_name}{num}', create_test_save(change_fields))

    def test_successful_creation(self):
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
    if valid:
        return lambda _: validator(value)
    def test(self):
        with self.assertRaises(ValidationError):
            validator(value)
    return test

valid_methods = {
    f'test_valid_{args[0].__name__}': create_validation_test(*args) for args in valid_tests
}
invalid_methods = {
    f'test_invalid_{args[0].__name__}': create_validation_test(*args, valid=False) for args in invalid_tests
}

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
    def test(self):
        if model == models.Stage:
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
            competition_sport_obj = models.CompetitionSport.objects.get(competition=competition, sport=sport)
            attrs['competition_sport'] = competition_sport_obj
        self.assertEqual(str(model.objects.create(**attrs)), expected)
    return test

test_str_methods = {f'test_{args[0].__name__}': create_str_test(*args) for args in test_str_data}
TestStr = type('TestStr', (TestCase,), test_str_methods)


class TestLinks(TestCase):
    def test_competition_sport(self):
        competition = models.Competition.objects.create(**competition_attrs)
        sport = models.Sport.objects.create(**sport_attrs)
        competition.sports.add(sport)

        link = models.CompetitionSport.objects.get(competition=competition, sport=sport)

        self.assertEqual(str(link), f'Competition:{competition}\nSport:{sport}')
