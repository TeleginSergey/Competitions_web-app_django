"""Module, which manage routes in our website."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'competitions', views.CompetitionViewSet)
router.register(r'sports', views.SportViewSet)
router.register(r'stages', views.StageViewSet)
router.register(r'competition_sport', views.CompetitionSportViewSet)

urlpatterns = [
    path('', views.main, name='homepage'),
    path('api/', include(router.urls)),
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api-auth/', include('rest_framework.urls'), name='rest_framework'),
    path('profile/', views.profile, name='profile'),
    path('competitions/', views.CompetitionListView.as_view(), name='competitions'),
    path('competition/', views.competition_view, name='competition'),
    path('sports/', views.SportListView.as_view(), name='sports'),
    path('sport/', views.sport_view, name='sport'),
    path('stages/', views.StageListView.as_view(), name='stages'),
    path('stage/', views.stage_view, name='stage'),
]
