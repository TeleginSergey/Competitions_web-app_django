"""Module with various views, viewsets, and helpers for handling models."""
from typing import Any

from django.contrib.auth import decorators, mixins
from django.core import exceptions
from django.core import paginator as django_paginator
from django.shortcuts import redirect, render
from django.views.generic import ListView
from rest_framework import permissions, response, status, viewsets

from . import serializers
from .forms import RegistrationForm
from .models import Client, Competition, CompetitionSport, Sport, Stage


def main(request):
    """Render the index page with competition and sport counts.

    Args:
        request: HttpRequest object representing the request made to the server.

    Returns:
        HttpResponse object: Rendered index.html page.
    """
    return render(
        request,
        'index.html',
        context={
            'competitions': Competition.objects.count(),
            'sports': Sport.objects.count(),
        },
    )


def create_listview(model_class, plural_name, template):
    """Create a ListView with pagination for a given model class.

    Args:
        model_class (type): class of the model
        plural_name (str): plural name of view to name listview
        template (str): path to template for listview

    Returns:
        type: class, which is created dynamic
    """
    class CustomListView(mixins.LoginRequiredMixin, ListView):
        """Class, which is created dynamic, for view list of some model."""

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
    """
    Create a view function for displaying a single instance of a model.

    Args:
        model: The model class to retrieve the instance from.
        model_name: The name to use for the context variable containing the instance.
        template: The template to render for displaying the instance.
        redirect_page: The URL to redirect to if the instance is not found.

    Returns:
        A view function that requires login and renders the template with the model.
    """
    @decorators.login_required
    def view(request):
        """
        Render a specific model instance based on the given id.

        Args:
            request (HttpRequest): the HTTP request object

        Returns:
            HttpResponse: rendered template with the context containing the model instance
        """
        id_ = request.GET.get('id', None)
        if not id_:
            return redirect(redirect_page)
        try:
            target = model.objects.get(id=id_) if id_ else None
        except exceptions.ValidationError:
            return redirect(redirect_page)
        if not target:
            return redirect(redirect_page)
        context = {model_name: target}
        return render(
            request,
            template,
            context,
        )
    return view


competition_view = create_view(
    Competition,
    'competition',
    'entities/competition.html',
    'competitions',
)
sport_view = create_view(Sport, 'sport', 'entities/sport.html', 'sport')
stage_view = create_view(Stage, 'stage', 'entities/stage.html', 'stages')


class APIPermission(permissions.BasePermission):
    """Permission class for API views to control access."""

    _safe_methods = ['GET', 'HEAD', 'OPTIONS']
    _unsafe_methods = ['POST', 'PUT', 'DELETE']

    def has_permission(self, request, _):
        """
        Check if the requesting user has permission to access the view based on the request method.

        Args:
            request (HttpRequest): The incoming request object.
            _: Unused parameter.

        Returns:
            bool: True if the user has permission. False otherwise.
        """
        if request.user and request.user.is_authenticated:
            if request.method in self._safe_methods:
                return True
            if request.method in self._unsafe_methods and request.user.is_superuser:
                return True
        return False


def create_viewset(model_class, serializer):
    """
    Create a custom ViewSet class for the given model and serializer.

    Args:
        model_class (type): The model class for which the ViewSet is being created.
        serializer (type): The serializer class to be used with the ViewSet.

    Returns:
        CustomViewSet: A custom ViewSet class that extends viewsets.ModelViewSet.
    """
    class CustomViewSet(viewsets.ModelViewSet):
        """Custom ViewSet class for handling CRUD operations on the provided model."""

        queryset = model_class.objects.all()
        serializer_class = serializer
        permission_classes = [APIPermission]

        def create(self, request, *args, **kwargs):
            """
            Create a new instance of the model.

            Args:
                request: The incoming request object.
                args: Additional positional arguments.
                kwargs: Additional keyword arguments.

            Returns:
                Response: Response object with the serialized data and appropriate status code.
            """
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return response.Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers,
                )
            except exceptions.ValidationError as exc:
                return response.Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        def update(self, request, *args, **kwargs):
            """
            Update an existing instance of the model.

            Args:
                request: The incoming request object.
                args: Additional positional arguments.
                kwargs: Additional keyword arguments.

            Returns:
                Response: Response object with the updated serialized data.
            """
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                self.perform_update(serializer)
            except exceptions.ValidationError as exc:
                return response.Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            return response.Response(serializer.data)

    return CustomViewSet


CompetitionViewSet = create_viewset(Competition, serializers.CompetitionSerializer)
SportViewSet = create_viewset(Sport, serializers.SportSerializer)
StageViewSet = create_viewset(Stage, serializers.StageSerializer)
CompetitionSportViewSet = create_viewset(CompetitionSport, serializers.CompetitionSportSerializer)


def register(request):
    """
    View for user registration.

    This view handles the registration process where a user can submit their registration details.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A rendered HTML page displaying the registration form.
    """
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
            'errors': errors,
        },
    )


@decorators.login_required
def profile(request):
    """
    View function for displaying user profile details.

    Args:
        request: HttpRequest object containing metadata about the request

    Returns:
        Rendered response with user profile data
    """
    if request.user.is_superuser:
        client_data = {'٩(◕‿◕｡)۶': 'You are superuser! What do you want to see there? (ノಠ益ಠ)ノ彡'}
    else:
        client = Client.objects.get(user=request.user)
        attrs = 'username', 'first_name', 'last_name', 'email'
        client_data = {attr: getattr(client, attr) for attr in attrs}

    return render(
        request,
        'pages/profile.html',
        {
            'client_data': client_data,
        },
    )
