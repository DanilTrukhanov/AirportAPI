from rest_framework import viewsets, mixins, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from airport import filters as custom_filters
from airport.models import (
    Country,
    City,
    Airport,
    Route,
    Crew,
    Airplane,
    AirplaneType,
    Flight,
    Order,
)

import airport.schema_parameters as schema_parameters
from airport.serializers import (
    CountryListSerializer,
    CityListSerializer,
    AirportListSerializer,
    CityCreateSerializer,
    AirportCreateSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    CrewSerializer,
    AirplaneTypeSerializer,
    AirplaneTypeListSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    FlightSerializer,
    FlightListSerializer,
    OrderSerializer,
)
from airport.permissions import ReadOnlyUserOrIsAdminPermission


class CountryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Country.objects.all()
    serializer_class = CountryListSerializer
    permission_classes = (ReadOnlyUserOrIsAdminPermission,)
    filter_backends = (
        DjangoFilterBackend,
        custom_filters.CountrySearchFilter,
        filters.OrderingFilter,
    )
    search_fields = ("name",)
    ordering_fields = ("name",)

    @extend_schema(parameters=schema_parameters.COUNTRY_PARAMETERS)
    def list(self, request, *args, **kwargs):
        """Get list of countries"""
        return super().list(request, *args, **kwargs)


class CityViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = City.objects.all()
    permission_classes = (ReadOnlyUserOrIsAdminPermission,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = ("name", "country__name")
    ordering_fields = ("name", "country__name")

    def get_queryset(self):
        return self.queryset.select_related(
            "country"
        ).prefetch_related("airports")

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return CityCreateSerializer
        return CityListSerializer

    @extend_schema(parameters=schema_parameters.CITY_PARAMETERS)
    def list(self, request, *args, **kwargs):
        """Get list of cities"""
        return super().list(request, *args, **kwargs)


class AirportViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Airport.objects.all()
    permission_classes = (ReadOnlyUserOrIsAdminPermission,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = ("name", "city__name", "city__country__name")
    ordering_fields = ("name",)

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return AirportCreateSerializer
        return AirportListSerializer

    def get_queryset(self):
        queryset = self.queryset
        return queryset.select_related("city__country")

    @extend_schema(parameters=schema_parameters.AIRPORT_PARAMETERS)
    def list(self, request, *args, **kwargs):
        """Get list of airports"""
        return super().list(request, *args, **kwargs)


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (ReadOnlyUserOrIsAdminPermission,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = custom_filters.RouteFilter
    search_fields = ("source__city__name", "destination__city__name")

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteRetrieveSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "retrieve":
            return queryset.select_related(
                "source__city__country", "destination__city__country"
            )
        return queryset.select_related(
            "source",
            "destination",
            "source__city",
            "destination__city",
        ).prefetch_related("flights")

    @extend_schema(parameters=schema_parameters.ROUTE_PARAMETERS)
    def list(self, request, *args, **kwargs):
        """Get list of airports"""
        return super().list(request, *args, **kwargs)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminUser,)


class AirplaneTypeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = AirplaneType.objects.all()
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneTypeListSerializer
        return AirplaneTypeSerializer


class AirplaneViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Airplane.objects.all()
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return AirplaneListSerializer
        return AirplaneSerializer


class FlightViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        Flight.objects.select_related(
            "route",
            "route__source",
            "route__destination",
            "route__source__city",
            "route__destination__city",
            "airplane",
        )
        .prefetch_related("crew", "tickets")
        .all()
    )
    permission_classes = (ReadOnlyUserOrIsAdminPermission,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    filterset_class = custom_filters.FlightFilter
    search_fields = (
        "route__source__city__name",
        "route__destination__city__name"
    )

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return FlightListSerializer
        return FlightSerializer

    @extend_schema(parameters=schema_parameters.FLIGHT_PARAMETERS)
    def list(self, request, *args, **kwargs):
        """Get list of airports"""
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.all().prefetch_related("tickets")
    permission_classes = (IsAuthenticated,)
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("created_at",)

    def get_serializer_class(self):
        return OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(parameters=schema_parameters.ORDER_PARAMETERS)
    def list(self, request, *args, **kwargs):
        """Get list of cities"""
        return super().list(request, *args, **kwargs)
