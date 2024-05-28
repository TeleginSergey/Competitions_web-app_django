from rest_framework.serializers import HyperlinkedModelSerializer, PrimaryKeyRelatedField, BaseSerializer

from .models import Competition, Stage, Sport, CompetitionSport

class CompetitionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Competition
        fields = ['id', 'date_of_start', 'date_of_end', 'title', 'sports']


class SportSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Sport
        fields = ['id', 'description', 'title', 'competitions']


class CompetitionSportSerializer(HyperlinkedModelSerializer):
    competition = PrimaryKeyRelatedField(queryset=Competition.objects.all())
    sport = PrimaryKeyRelatedField(queryset=Sport.objects.all())
    class Meta:
        model = CompetitionSport
        fields = '__all__'


class StageSerializer(HyperlinkedModelSerializer):
    competition_sport = PrimaryKeyRelatedField(queryset=CompetitionSport.objects.all())

    class Meta:
        model = Stage
        fields = ['id', 'competition_sport', 'place', 'date', 'title']
