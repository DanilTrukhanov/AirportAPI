from django.db import transaction
from rest_framework import serializers

from airport.models import (
    Country,
    City,
    Airport,
    Route,
    Flight,
    Crew,
    AirplaneType,
    Airplane,
    Order,
    Ticket,
)


class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CityListSerializer(serializers.ModelSerializer):
    country = serializers.StringRelatedField()
    airports = serializers.SlugRelatedField(
        slug_field="name", many=True, read_only=True
    )

    class Meta:
        model = City
        fields = ("id", "name", "country", "airports")


class CityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name", "country")


class AirportListSerializer(serializers.ModelSerializer):
    city = serializers.StringRelatedField()
    country = serializers.SerializerMethodField()

    class Meta:
        model = Airport
        fields = ("id", "name", "city", "country")

    def get_country(self, obj):
        return obj.city.country.name


class AirportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "city")


class AirportCityNameField(serializers.PrimaryKeyRelatedField):
    def display_value(self, instance):
        return f"{instance.name} ({instance.city.name})"


class RouteSerializer(serializers.ModelSerializer):
    source = AirportCityNameField(
        queryset=Airport.objects.select_related("city")
    )
    destination = AirportCityNameField(
        queryset=Airport.objects.select_related("city")
    )
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        read_only=True,
        slug_field="city.name",
    )
    destination = serializers.SlugRelatedField(
        read_only=True,
        slug_field="city.name",
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance", "flights")


class RouteRetrieveSerializer(RouteListSerializer):
    source = AirportListSerializer()
    destination = AirportListSerializer()


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")

    def get_full_name(self, obj):
        return str(obj)


class RouteField(serializers.PrimaryKeyRelatedField):
    def display_value(self, instance):
        return f"{instance.source.city.name} -> {instance.destination.city.name}"


class FlightSerializer(serializers.ModelSerializer):
    route = RouteField(
        queryset=Route.objects.select_related(
            "source", "destination", "source__city", "destination__city"
        )
    )

    def validate(self, data):
        data = super(FlightSerializer, self).validate(data)
        Flight.validate_time(data["departure_time"], data["arrival_time"])
        return data

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField()
    airplane = serializers.StringRelatedField()
    crew = serializers.StringRelatedField(many=True)
    available_tickets = serializers.SerializerMethodField(read_only=True)

    def get_available_tickets(self, obj):
        return obj.airplane.capacity - obj.tickets.count()

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "tickets",
            "crew",
            "available_tickets",
        )


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "capacity")


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.StringRelatedField()

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "capacity",
            "flights",
        )


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneTypeListSerializer(serializers.ModelSerializer):
    airplanes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )

    class Meta:
        model = AirplaneType
        fields = ("id", "name", "airplanes")


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, data):
        data = super(TicketSerializer, self).validate(data)
        Ticket.validate_ticket(data["flight"], data["row"], data["seat"])
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket in tickets:
                Ticket.objects.create(order=order, **ticket)
            return order
