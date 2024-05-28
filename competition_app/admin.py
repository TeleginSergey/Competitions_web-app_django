from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Competition, CompetitionSport, Sport, Stage, Client

class CompetitionSportInline(admin.TabularInline):
    model = CompetitionSport
    extra = 1


@admin.register(CompetitionSport)
class CompetitionSportAdmin(admin.ModelAdmin):
    model = CompetitionSport


class HaveDateFilter(admin.SimpleListFilter):
    title = _('Date')
    parameter_name = 'date'


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    model = Competition
    inlines = (CompetitionSportInline,)


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    model = Sport
    inlines = (CompetitionSportInline,)


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    model = Stage

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    model = Client
