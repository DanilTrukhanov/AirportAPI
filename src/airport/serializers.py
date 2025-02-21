from rest_framework import serializers

from airport.models import Country, City, Airport


class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CityListSerializer(serializers.ModelSerializer):
    country = serializers.StringRelatedField()
    class Meta:
        model = City
        fields = ("id", "name", "country")


class AirportListSerializer(serializers.ModelSerializer):
    city = serializers.StringRelatedField()
    class Meta:
        model = Airport
        fields = ("id", "name", "city")
