from rest_framework import generics, viewsets

from airport.models import Country, City, Airport
from airport.serializers import CountryListSerializer, CityListSerializer, AirportListSerializer


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountryListSerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CityListSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportListSerializer

    def get_queryset(self):
        return self.queryset.select_related("city__country")