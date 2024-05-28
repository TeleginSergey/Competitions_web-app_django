from typing import Any
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.core import paginator as django_paginator, exceptions
from rest_framework import viewsets, permissions, status, response
from django.contrib.auth import mixins, decorators

from .serializers import CompetitionSerializer, SportSerializer, StageSerializer, CompetitionSportSerializer
from .models import Competition, Stage, Sport, Client, CompetitionSport
from .forms import RegistrationForm


def main(request):
    return render(
        request,
        'index.html',
        context={
            'competitions': Competition.objects.count(),
            'sports': Sport.objects.count(),
        }
    )


def create_listview(model_class, plural_name, template):
    class CustomListView(mixins.LoginRequiredMixin, ListView):
        model = model_class
        template_name = template
        paginate_by = 10
        context_object_name = plural_name
        
        def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
            context = super().get_context_data(**kwargs)
            instances = model_class.objects.all()
            paginator = django_paginator.Paginator(instances, 10)
            page = self.request.GET.get('page')
            page_obj = paginator.get_page(page)
            context[f'{plural_name}_list'] = page_obj
            return context
    return CustomListView


CompetitionListView = create_listview(Competition, 'competitions', 'catalog/competitions.html')
SportListView = create_listview(Sport, 'sports', 'catalog/sports.html')
StageListView = create_listview(Stage, 'stages', 'catalog/stages.html')


def create_view(model, model_name, template, redirect_page):
    @decorators.login_required
    def view(request):
        id_ = request.GET.get('id', None)
        if not id_:
            return redirect(redirect_page)
        try:
            target = model.objects.get(id=id_) if id_ else None
        except exceptions.ValidationError:
            return redirect(redirect_page)
        if not target:
            return redirect_page(redirect_page)
        context = {model_name: target}
        return render(
            request,
            template,
            context,
        )
    return view

competition_view = create_view(Competition, 'competition', 'entities/competition.html', 'competitions')
sport_view = create_view(Sport, 'sport', 'entities/sport.html', 'sport')
stage_view = create_view(Stage, 'stage', 'entities/stage.html', 'stages')


class APIPermission(permissions.BasePermission):
    _safe_methods = ['GET', 'HEAD', 'OPTIONS']
    _unsafe_methods = ['POST', 'PUT', 'DELETE']

    def has_permission(self, request, _):
        if request.method in self._safe_methods and (request.user and request.user.is_authenticated):
            return True
        if request.method in self._unsafe_methods and (request.user and request.user.is_superuser):
            return True
        return False


def create_viewset(model_class, serializer):
    class CustomViewSet(viewsets.ModelViewSet):
        queryset = model_class.objects.all()
        serializer_class = serializer
        permission_classes = [APIPermission]

        def create(self, request, *args, **kwargs):
            try:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            except exceptions.ValidationError as e:
                return response.Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        def update(self, request, *args, **kwargs):
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return response.Response(serializer.data)

    return CustomViewSet


CompetitionViewSet = create_viewset(Competition, CompetitionSerializer)
SportViewSet = create_viewset(Sport, SportSerializer)
StageViewSet = create_viewset(Stage, StageSerializer)
CompetitionSportViewSet = create_viewset(CompetitionSport, CompetitionSportSerializer)


def register(request):
    errors = ''
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Client.objects.create(user=user)
        else:
            errors = form.errors
    else:
        form = RegistrationForm()
    
    return render(
        request,
        'registration/register.html',
        {
            'form': form,
            'errors': errors
        }
    )


@decorators.login_required
def profile(request):
    if not request.user.is_superuser:
        client = Client.objects.get(user=request.user)
        attrs = 'username', 'first_name', 'last_name', 'email'
        client_data = {attr: getattr(client, attr) for attr in attrs}
    else:
        client_data = {'٩(◕‿◕｡)۶': 'You are superuser! What do you want to see there, LOL? (ノಠ益ಠ)ノ彡'}
    
    return render(
        request,
        'pages/profile.html',
        {
            'client_data': client_data,
        }
    )
