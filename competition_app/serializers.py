"""Module with serializers for different models."""
from rest_framework.serializers import HyperlinkedModelSerializer, PrimaryKeyRelatedField

from .models import Competition, CompetitionSport, Sport, Stage


class CompetitionSerializer(HyperlinkedModelSerializer):
    """Serializer for the Competition model."""

    class Meta:
        model = Competition
        fields = ['id', 'date_of_start', 'date_of_end', 'title', 'sports']


class SportSerializer(HyperlinkedModelSerializer):
    """Serializer for the Sport model."""

    class Meta:
        model = Sport
        fields = ['id', 'description', 'title', 'competitions']


class CompetitionSportSerializer(HyperlinkedModelSerializer):
    """Serializer for the CompetitionSport model."""

    competition = PrimaryKeyRelatedField(queryset=Competition.objects.all())
    sport = PrimaryKeyRelatedField(queryset=Sport.objects.all())

    class Meta:
        model = CompetitionSport
        fields = '__all__'


class StageSerializer(HyperlinkedModelSerializer):
    """Serializer for the Stage model."""

    competition_sport = PrimaryKeyRelatedField(queryset=CompetitionSport.objects.all())

    class Meta:
        model = Stage
        fields = ['id', 'competition_sport', 'place', 'date', 'title']
