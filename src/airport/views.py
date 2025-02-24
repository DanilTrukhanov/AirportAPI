from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser

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
    FlightRetrieveSerializer,
    OrderSerializer,
)

from permissions import ReadOnlyUserOrIsAdminPermission


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountryListSerializer
    permission_classes = (ReadOnlyUserOrIsAdminPermission,)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    permission_classes = (ReadOnlyUserOrIsAdminPermission,)

    def get_queryset(self):
        return self.queryset.select_related("country").prefetch_related("airports")

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return CityCreateSerializer
        return CityListSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    permission_classes = (ReadOnlyUserOrIsAdminPermission,)

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return AirportCreateSerializer
        return AirportListSerializer

    def get_queryset(self):
        queryset = self.queryset
        return queryset.select_related("city__country")


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (ReadOnlyUserOrIsAdminPermission,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "retrieve":
            return queryset.select_related(
                "source__city__country", "destination__city__country"
            )
        return queryset.select_related(
            "source", "destination", "source__city", "destination__city"
        )


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminUser,)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneTypeListSerializer
        return AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
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
    viewsets.GenericViewSet
):
    queryset = Flight.objects.select_related(
        "route",
        "route__source",
        "route__destination",
        "route__source__city",
        "route__destination__city",
        "airplane",
    ).prefetch_related("crew").all()
    permission_classes = (ReadOnlyUserOrIsAdminPermission,)

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Order.objects.all().prefetch_related("tickets")
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        return OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
