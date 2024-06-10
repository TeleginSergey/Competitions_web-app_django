"""Admin Panel."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Client, Competition, CompetitionSport, Sport, Stage


class CompetitionSportInline(admin.TabularInline):
    """Inline configuration for CompetitionSport model."""

    model = CompetitionSport
    extra = 1


@admin.register(CompetitionSport)
class CompetitionSportAdmin(admin.ModelAdmin):
    """Admin configuration for CompetitionSport model."""

    model = CompetitionSport


class HaveDateFilter(admin.SimpleListFilter):
    """Custom filter for date field."""

    title = _('Date')
    parameter_name = 'date'


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    """Admin configuration for Competition model."""

    model = Competition
    inlines = (CompetitionSportInline,)


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    """Admin configuration for Sport model."""

    model = Sport
    inlines = (CompetitionSportInline,)


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    """Admin configuration for Stage model."""

    model = Stage


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Admin configuration for Client model."""

    model = Client
