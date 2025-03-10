import django_filters
from django_filters import FilterSet
from rest_framework import filters

from airport.models import Flight, Route, Airport


class FlightFilter(FilterSet):
    departure_date = django_filters.DateFilter(
        field_name="departure_time", lookup_expr="date"
    )
    departure_date__gt = django_filters.DateFilter(
        field_name="departure_time", lookup_expr="date__gt"
    )
    departure_date__lt = django_filters.DateFilter(
        field_name="departure_time", lookup_expr="date__lt"
    )

    departure_time = django_filters.TimeFilter(
        field_name="departure_time", lookup_expr="time"
    )
    departure_time__gt = django_filters.TimeFilter(
        field_name="departure_time", lookup_expr="time__gt"
    )
    departure_time__lt = django_filters.TimeFilter(
        field_name="departure_time", lookup_expr="time__lt"
    )

    route = django_filters.ModelChoiceFilter(
        field_name="route",
        queryset=Route.objects.select_related(
            "source",
            "destination",
            "source__city",
            "destination__city",
        ),
    )

    class Meta:
        model = Flight
        fields = []


class RouteFilter(FilterSet):
    source = django_filters.ModelChoiceFilter(
        field_name="source",
        queryset=Airport.objects.select_related("city", "city__country"),
    )
    destination = django_filters.ModelChoiceFilter(
        field_name="destination",
        queryset=Airport.objects.select_related("city", "city__country"),
    )
    has_flights = django_filters.BooleanFilter(
        field_name="flights",
        lookup_expr="isnull",
        exclude=True,
    )

    class Meta:
        model = Route
        fields = []


class CountrySearchFilter(filters.SearchFilter):
    search_param = "country"
