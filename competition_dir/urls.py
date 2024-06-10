"""URL configuration for competition_dir project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('competition_app.urls')),
]
