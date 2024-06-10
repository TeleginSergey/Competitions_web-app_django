"""
Module for defining Django models related to competitions, sports, stages, and clients.

This module contains various models including Competition, Sport, CompetitionSport, Stage, and
Client along with related mixins, managers, and utility functions.
These models define the structure and relationships between different entities in the system
for managing competitions and related data.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from django.conf.global_settings import AUTH_USER_MODEL
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import config


def get_datetime() -> datetime:
    """
    Get the current datetime in UTC timezone.

    Returns:
        datetime: Current datetime object.
    """
    return datetime.now(timezone.utc)


class UUIDMixin(models.Model):
    """Mixin class to add a UUID primary key field to models."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


def check_modified(dt: datetime) -> None:
    """
    Validate if the given datetime is greater than the current datetime.

    Args:
        dt (datetime): Datetime object to check.

    Raises:
        ValidationError: If the given datetime is greater than the current datetime.
    """
    if dt > get_datetime():
        raise ValidationError(
            _('Date and time is bigger than current!'),
            params={'modified': dt},
        )


def check_created(dt: datetime) -> None:
    """
    Validate if the given datetime is greater than the current datetime.

    Args:
        dt (datetime): Datetime object to check.

    Raises:
        ValidationError: If the given datetime is greater than the current datetime.
    """
    if dt > get_datetime():
        raise ValidationError(
            _('Date and time is bigger than current!'),
            params={'created': dt},
        )


class CreatedMixin(models.Model):
    """Mixin class to add a created datetime field to models."""

    created = models.DateTimeField(
        _('created'), null=True, blank=True,
        default=get_datetime, validators=[check_created],
    )

    class Meta:
        abstract = True


class ModifiedMixin(models.Model):
    """Mixin class to add a modified datetime field to models."""

    modified = models.DateTimeField(
        _('modified'), null=True, blank=True,
        default=get_datetime, validators=[check_modified],
    )

    class Meta:
        abstract = True


def check_dates_order(first_date: datetime, second_date: datetime, message):
    """
    Check the order of two date values and raise a ValidationError if the order is incorrect.

    Args:
        first_date (datetime): The first date value to compare.
        second_date (datetime): The second date value to compare.
        message: The error message to be raised if the order is incorrect.

    Raises:
        ValidationError: if the date order is incorrect
    """
    if first_date and second_date and second_date < first_date:
        raise ValidationError(_(message))


class CompetitionManager(models.Manager):
    """Custom manager for the Competition model."""

    def create(self, **kwargs: Any) -> Any:
        """
        Create a new Competition instance with validation checks on date_of_start and date_of_end.

        Args:
            kwargs: Keyword arguments for creating the Competition instance.

        Returns:
            Any: The created Competition instance.
        """
        if ('date_of_start' in kwargs.keys()) and ('date_of_end' in kwargs.keys()):
            check_dates_order(
                kwargs['date_of_start'],
                kwargs['date_of_end'],
                config.MESSAGE_COMPETITION_DATES_INCORRECT_ORDER,
            )
        return super().create(**kwargs)


class Competition(UUIDMixin, CreatedMixin, ModifiedMixin):
    """Model representing a competition in the system."""

    title = models.TextField(_('title'), null=False, blank=False, unique=True, max_length=200)
    date_of_start = models.DateField(_('date_of_start'), null=True, blank=True)
    date_of_end = models.DateField(_('date_of_end'), null=True, blank=True)

    sports = models.ManyToManyField('Sport', verbose_name='sport', through='CompetitionSport')
    objects = CompetitionManager()

    def save(self, *args, **kwargs):
        """
        Save method for the Competition model.

        Args:
            args: Additional arguments.
            kwargs: Additional keyword arguments.
        """
        check_created(self.created)
        check_modified(self.modified)
        check_dates_order(
            self.created,
            self.modified,
            config.MESSAGE_CREATED_MODIFIED_INCORRECT_ORDER,
        )
        if self.date_of_start and self.date_of_end:
            check_dates_order(
                self.date_of_start,
                self.date_of_end,
                config.MESSAGE_COMPETITION_DATES_INCORRECT_ORDER,
            )

        return super().save(*args, **kwargs)

    def clean(self):
        """Clean method for the Competition model to perform validation checks."""
        if self.date_of_start and self.date_of_end:
            check_dates_order(
                self.date_of_start,
                self.date_of_end,
                config.MESSAGE_COMPETITION_DATES_INCORRECT_ORDER,
            )

    def __str__(self) -> str:
        """
        Return the string representation of the Competition instance.

        Returns:
            str: String representation of the object.
        """
        return f'{self.title}'

    class Meta:
        db_table = '"competition_schema"."competition"'
        ordering = ['date_of_start', 'title']
        verbose_name = _('competition')
        verbose_name_plural = _('competitions')


class Sport(UUIDMixin, CreatedMixin, ModifiedMixin):
    """Model representing a sport in the system."""

    title = models.TextField(_('title'), null=False, blank=False, unique=True, max_length=200)
    description = models.TextField(_('description'), null=True, blank=True, max_length=1000)

    competitions = models.ManyToManyField(
        Competition,
        verbose_name='competitions',
        through='CompetitionSport',
    )

    def save(self, *args, **kwargs) -> None:
        """
        Save method for the Sport model.

        Args:
            args: Additional arguments.
            kwargs: Additional keyword arguments.
        """
        check_created(self.created)
        check_modified(self.modified)
        check_dates_order(
            self.created,
            self.modified,
            config.MESSAGE_CREATED_MODIFIED_INCORRECT_ORDER,
        )
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Return the string representation of the Sport instance.

        Returns:
            str: String representation of the object.
        """
        return f'{self.title}'

    class Meta:
        db_table = '"competition_schema"."sport"'
        ordering = ['title']
        verbose_name = _('sport')
        verbose_name_plural = _('sports')


class CompetitionSport(UUIDMixin, CreatedMixin):
    """Model representing the relationship between a Competition and a Sport."""

    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        verbose_name=_('competition'),
    )
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, verbose_name=_('sport'))

    def save(self, *args, **kwargs) -> None:
        """
        Save method for the CompetitionSport model.

        Args:
            args: Additional arguments.
            kwargs: Additional keyword arguments.
        """
        check_created(self.created)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Return the string representation of the CompetitionSport instance.

        Returns:
            str: String representation of the object.
        """
        return f'Competition:{self.competition}\nSport:{self.sport}'

    class Meta:
        unique_together = (
            ('competition', 'sport'),
        )
        db_table = '"competition_schema"."competition_sport"'
        verbose_name = _('relationship_competition_sport')
        verbose_name_plural = _('relationships_competition_sport')


class StageManager(models.Manager):
    """Custom manager for the Stage model."""

    def create(self, **kwargs: Any) -> Any:
        """
        Create method for the Stage model.

        Args:
            kwargs: Keyword arguments for creating the Stage object.

        Returns:
            Any: Created Stage object.
        """
        if 'date' in kwargs.keys() and 'competition_sport' in kwargs.keys():
            competition_sport = CompetitionSport.objects.get(id=kwargs['competition_sport'].id)
            competition_end_date = competition_sport.competition.date_of_end
            competition_start_date = competition_sport.competition.date_of_start

            check_dates_order(
                competition_start_date,
                kwargs['date'],
                "Stage's date is after the end date of the competition!",
            )
            check_dates_order(
                kwargs['date'],
                competition_end_date,
                "Stage's date is before the start date of the competition!",
            )

        return super().create(**kwargs)


class Stage(UUIDMixin, CreatedMixin, ModifiedMixin):
    """Model representing a stage in a competition."""

    title = models.TextField(_('title'), null=False, blank=False, max_length=200)
    date = models.DateField(_('date'), null=True, blank=True)
    place = models.TextField(_('place'), null=True, blank=True)
    competition_sport = models.ForeignKey(
        CompetitionSport,
        on_delete=models.CASCADE,
        verbose_name=('competition_sport'),
    )

    objects = StageManager()

    def save(self, *args, **kwargs) -> None:
        """
        Save method for the Stage model.

        Args:
            args: Additional arguments.
            kwargs: Additional keyword arguments.

        Raises:
            ValidationError: if date order is incorrect.
        """
        check_created(self.created)
        check_modified(self.modified)
        check_dates_order(
            self.created,
            self.modified,
            config.MESSAGE_CREATED_MODIFIED_INCORRECT_ORDER,
        )
        if self.date and self.competition_sport:
            if self.competition_sport.competition:
                competition_end_date = self.competition_sport.competition.date_of_end
                competition_start_date = self.competition_sport.competition.date_of_start

                if competition_end_date and self.date > competition_end_date:
                    raise ValidationError(_("Stage's date is after end date of competition!"))

                if competition_start_date and self.date < competition_start_date:
                    raise ValidationError(_("Stage's date is before start date of competition!"))
            else:
                raise ValidationError("Stage's competition_sport has no competition associated.")
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Return the string representation of the Stage object.

        Returns:
            str: String representation of the object.
        """
        return f'{self.title}'

    class Meta:
        unique_together = (
            ('title', 'competition_sport'),
        )
        db_table = '"competition_schema"."stage"'
        verbose_name = _('stage')
        verbose_name_plural = _('stages')


class Client(UUIDMixin, CreatedMixin, ModifiedMixin):
    """Model representing a client associated with a user."""

    user = models.OneToOneField(
        AUTH_USER_MODEL, verbose_name=_('user'),
        null=False, blank=False,
        unique=True, on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs) -> None:
        """
        Save method for the Client model.

        Args:
            args: Additional arguments.
            kwargs: Additional keyword arguments.
        """
        check_created(self.created)
        check_modified(self.modified)
        check_dates_order(
            self.created,
            self.modified,
            config.MESSAGE_CREATED_MODIFIED_INCORRECT_ORDER,
        )
        return super().save(*args, **kwargs)

    class Meta:
        db_table = '"competition_schema"."client"'
        verbose_name = _('client')
        verbose_name_plural = _('clients')

    @property
    def username(self) -> str:
        """
        Get the username of the associated user.

        Returns:
            str: The username of the user.
        """
        return self.user.username

    @property
    def first_name(self) -> str:
        """
        Get the first name of the associated user.

        Returns:
            str: The first name of the user.
        """
        return self.user.first_name

    @property
    def last_name(self) -> str:
        """
        Get the last name of the associated user.

        Returns:
            str: The last name of the user.
        """
        return self.user.last_name

    @property
    def email(self) -> str:
        """
        Get the email of the associated user.

        Returns:
            str: The email of the user.
        """
        return self.user.email

    def __str__(self) -> str:
        """
        Return the string representation of the Client object.

        Returns:
            str: String representation of the object.
        """
        return f'{self.username} {self.first_name} {self.last_name}'
