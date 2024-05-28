from typing import Any
from django.db import models
from uuid import uuid4
from datetime import datetime, timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf.global_settings import AUTH_USER_MODEL
from rest_framework import exceptions, status

from . import config


def get_datetime() -> datetime:
    return datetime.now(timezone.utc)


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True



def check_modified(dt: datetime) -> None:
    if dt > get_datetime():
        raise ValidationError(
            _('Date and time is bigger than current!'),
            params={'modified': dt},
        )


def check_created(dt: datetime) -> None:
    if dt > get_datetime():
        raise ValidationError(
            _('Date and time is bigger than current!'),
            params={'created': dt},
        )


class CreatedMixin(models.Model):
    created = models.DateTimeField(
        _('created'), null=True, blank=True,
        default=get_datetime, validators=[check_created]
    )

    class Meta:
        abstract = True


class ModifiedMixin(models.Model):
    modified = models.DateTimeField(
        _('modified'), null=True, blank=True,
        default=get_datetime, validators=[check_modified]
    )

    class Meta:
        abstract = True


def check_dates_order(first_date: datetime, second_date: datetime, message):
    if first_date and second_date and second_date < first_date:
        raise ValidationError(_(message))


class CompetitionManager(models.Manager):
    def create(self, **kwargs: Any) -> Any:
        if ('date_of_start' in kwargs.keys()) and ('date_of_end' in kwargs.keys()):
            check_dates_order(kwargs['date_of_start'], kwargs['date_of_end'], config.MESSAGE_COMPETITION_DATES_INCORRECT_ORDER)
        return super().create(**kwargs)


class Competition(UUIDMixin, CreatedMixin, ModifiedMixin):
    title = models.TextField(_('title'), null=False, blank=False, unique=True, max_length=200)
    date_of_start = models.DateField(_('date_of_start'), null=True, blank=True)
    date_of_end = models.DateField(_('date_of_end'), null=True, blank=True)

    sports = models.ManyToManyField('Sport', verbose_name='sport', through='CompetitionSport')
    objects = CompetitionManager()
    
    def save(self, *args, **kwargs):
        check_created(self.created)
        check_modified(self.modified)
        check_dates_order(self.created, self.modified, config.MESSAGE_CREATED_MODIFIED_INCORRECT_ORDER)
        if self.date_of_start and self.date_of_end:
            check_dates_order(self.date_of_start, self.date_of_end, config.MESSAGE_COMPETITION_DATES_INCORRECT_ORDER)

        return super().save(*args, **kwargs)

    def clean(self):
        if self.date_of_start and self.date_of_end:
            check_dates_order(self.date_of_start, self.date_of_end, config.MESSAGE_COMPETITION_DATES_INCORRECT_ORDER)

    def __str__(self) -> str:
        return f'{self.title}'

    class Meta:
        db_table = '"competition_schema"."competition"'
        ordering = ['date_of_start', 'title']
        verbose_name = _('competition')
        verbose_name_plural = _('competitions')


class Sport(UUIDMixin, CreatedMixin, ModifiedMixin):
    title = models.TextField(_('title'), null=False, blank=False, unique=True, max_length=200)
    description = models.TextField(_('description'), null=True, blank=True, max_length=1000)

    competitions = models.ManyToManyField(Competition, verbose_name='competitions', through='CompetitionSport')
    
    def save(self, *args, **kwargs) -> None:
        check_created(self.created)
        check_modified(self.modified)
        check_dates_order(self.created, self.modified, config.MESSAGE_CREATED_MODIFIED_INCORRECT_ORDER)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.title}'

    class Meta:
        db_table = '"competition_schema"."sport"'
        ordering = ['title']
        verbose_name = _('sport')
        verbose_name_plural = _('sports')


class CompetitionSport(UUIDMixin, CreatedMixin):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, verbose_name=_('competition'))
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, verbose_name=_('sport'))
    
    def save(self, *args, **kwargs) -> None:
        check_created(self.created)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'Competition:{self.competition}\nSport:{self.sport}'

    class Meta:
        unique_together = (
            ('competition', 'sport'),
        )
        db_table = '"competition_schema"."competition_sport"'
        verbose_name = _('relationship_competition_sport')
        verbose_name_plural = _('relationships_competition_sport')



class StageManager(models.Manager):
    def create(self, **kwargs: Any) -> Any:
        if 'date' in kwargs.keys() and 'competition_sport' in kwargs.keys():
            competition_sport = CompetitionSport.objects.get(id=kwargs['competition_sport'].id)
            competition_end_date = competition_sport.competition.date_of_end
            competition_start_date = competition_sport.competition.date_of_start

            check_dates_order(competition_start_date, kwargs['date'], "Stage's date is after the end date of the competition!")
            check_dates_order(kwargs['date'], competition_end_date, "Stage's date is before the start date of the competition!")

        return super().create(**kwargs)


class Stage(UUIDMixin, CreatedMixin, ModifiedMixin):
    title = models.TextField(_('title'), null=False, blank=False, max_length=200)
    date = models.DateField(_('date'), null=True, blank=True)
    place = models.TextField(_('place'), null=True, blank=True)
    competition_sport = models.ForeignKey(CompetitionSport, on_delete=models.CASCADE, verbose_name=('competition_sport'))

    objects = StageManager()

    def save(self, *args, **kwargs) -> None:
        check_created(self.created)
        check_modified(self.modified)
        check_dates_order(self.created, self.modified, config.MESSAGE_CREATED_MODIFIED_INCORRECT_ORDER)
        if self.date and self.competition_sport:
            if self.competition_sport.competition:
                competition_end_date = self.competition_sport.competition.date_of_end
                competition_start_date = self.competition_sport.competition.date_of_start

                if competition_end_date and self.date > competition_end_date:
                    raise ValidationError(_("Stage's date is after the end date of the competition!"))

                if competition_start_date and self.date < competition_start_date:
                    raise ValidationError(_("Stage's date is before the start date of the competition!"))
            else:
                raise ValidationError("Stage's competition_sport has no competition associated.")
        return super().save(*args, **kwargs)


    def __str__(self) -> str:
        return f'{self.title}'

    class Meta:
        unique_together = (
            ('title', 'competition_sport'),
        )
        db_table = '"competition_schema"."stage"'
        verbose_name = _('stage')
        verbose_name_plural = _('stages')



class Client(UUIDMixin, CreatedMixin, ModifiedMixin):
    user = models.OneToOneField(
        AUTH_USER_MODEL, verbose_name=_('user'),
        null=False, blank=False, 
        unique=True, on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs) -> None:
        check_created(self.created)
        check_modified(self.modified)
        check_dates_order(self.created, self.modified, config.MESSAGE_CREATED_MODIFIED_INCORRECT_ORDER)
        return super().save(*args, **kwargs)

    class Meta:
        db_table = '"competition_schema"."client"'
        verbose_name = _('client')
        verbose_name_plural = _('clients')

    @property
    def username(self) -> str:
        return self.user.username
    
    @property
    def first_name(self) -> str:
        return self.user.first_name
    
    @property
    def last_name(self) -> str:
        return self.user.last_name
    
    @property
    def email(self) -> str:
        return self.user.email
    
    def __str__(self) -> str:
        return f'{self.username} {self.first_name} {self.last_name}'
