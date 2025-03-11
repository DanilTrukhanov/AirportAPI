import datetime
import json

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import (
    Country,
    City,
    Airport,
    Route,
    Crew,
    AirplaneType,
    Airplane,
    Flight,
)
from airport.serializers import RouteListSerializer, FlightListSerializer

COUNTRY_URL = reverse("airport:country-list")
CITY_URL = reverse("airport:city-list")
AIRPORT_URL = reverse("airport:airport-list")
ROUTE_URL = reverse("airport:route-list")
FLIGHT_URL = reverse("airport:flight-list")
ORDER_URL = reverse("airport:order-list")
CREW_URL = reverse("airport:crew-list")
AIRPLANETYPE_URL = reverse("airport:airplanetype-list")
AIRPLANE_URL = reverse("airport:airplane-list")


def sample_country(**params):
    defaults = {
        "name": "Spain",
    }
    defaults.update(params)
    return Country.objects.create(**defaults)


def sample_city(**params):
    country = sample_country()

    defaults = {"name": "Barcelona", "country": country}
    defaults.update(**params)
    return City.objects.create(**defaults)


def sample_airport(**params):
    city = sample_city()

    defaults = {"name": "Barcelona International Airport", "city": city}
    defaults.update(**params)
    return Airport.objects.create(**defaults)


def sample_route(**params):
    source = sample_airport()
    destination = sample_airport(name="Another Barcelona International Airport")

    defaults = {
        "source": source,
        "destination": destination,
        "distance": 300,
    }
    defaults.update(**params)
    return Route.objects.create(**defaults)


def sample_crew(**params):
    defaults = {"first_name": "TestName", "last_name": "TestLastName"}
    defaults.update(**params)
    return Crew.objects.create(**defaults)


def sample_airplane_type(**params):
    defaults = {"name": "TestType"}
    defaults.update(**params)
    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):
    airplane_type = sample_airplane_type()

    defaults = {
        "name": "Test Airplane",
        "rows": 20,
        "seats_in_row": 5,
        "airplane_type": airplane_type,
    }
    defaults.update(**params)
    return Airplane.objects.create(**defaults)


def sample_flight(**params):
    route = sample_route()
    airplane = sample_airplane()
    crew = sample_crew()
    departure_time = datetime.datetime(year=2025, month=4, day=14, hour=10, minute=0)
    arrival_time = datetime.datetime(year=2025, month=4, day=14, hour=12, minute=0)

    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": departure_time,
        "arrival_time": arrival_time,
    }
    defaults.update(**params)
    flight = Flight.objects.create(**defaults)
    flight.crew.add(crew)
    return flight


class TestUnauthenticated(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.country = sample_country()

    def test_get_country_list(self):
        response = self.client.get(COUNTRY_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_city_list(self):
        response = self.client.get(COUNTRY_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_airport_list(self):
        response = self.client.get(AIRPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_route_list(self):
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_flight_list(self):
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_order_list_not_allowed(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_airplane_type_list_not_allowed(self):
        response = self.client.get(AIRPLANETYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_airplane_list_not_allowed(self):
        response = self.client.get(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_not_allowed(self):
        response = self.client.post(ORDER_URL, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestAuthenticatedUser(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@user.com", password="1qazcde3"
        )
        self.client.force_authenticate(self.user)

    def test_get_order_list(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_route_list(self):
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_flight_list(self):
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_airplane_list_not_allowed(self):
        response = self.client.get(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order(self):
        flight = sample_flight()

        response = self.client.post(
            ORDER_URL,
            data=json.dumps({"tickets": [{"row": 1, "seat": 2, "flight": flight.id}]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestRouteFilters(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@user.com", password="1qazcde3"
        )
        self.client.force_authenticate(self.user)

        self.airport1 = sample_airport()
        self.airport2 = sample_airport(
            name="Another Airport", city=sample_city(name="London")
        )
        self.airport3 = sample_airport(name="Paris IA")
        self.airport4 = sample_airport(name="Madrid IA")

        sample_route(source=self.airport1, destination=self.airport2)
        sample_route(source=self.airport2, destination=self.airport1)
        sample_route(source=self.airport3, destination=self.airport4)

    def test_source_filter(self):
        res = self.client.get(ROUTE_URL + f"?source={self.airport2.id}")

        routes = Route.objects.filter(source_id=self.airport2.id)
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_destination_filter(self):
        res = self.client.get(ROUTE_URL + f"?destination={self.airport1.id}")

        routes = Route.objects.filter(destination_id=self.airport1.id)
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_search(self):
        search_param = "London"
        res = self.client.get(ROUTE_URL + f"?search={search_param}")

        routes = Route.objects.filter(
            Q(source__city__name__icontains=search_param)
            | Q(source__city__country__name__icontains=search_param)
            | Q(destination__city__name__icontains=search_param)
            | Q(destination__city__country__name=search_param)
        )
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class TestFlightFilters(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@user.com", password="1qazcde3"
        )
        self.client.force_authenticate(self.user)

        spain = sample_country()
        france = sample_country(name="France")

        barca = sample_city(country=spain)
        paris = sample_city(country=france)

        airport_barcelona = sample_airport(city=barca)
        airport_paris = sample_airport(name="Paris IA", city=paris)

        self.barca_paris_route = sample_route(
            source=airport_barcelona,
            destination=airport_paris
        )
        self.paris_barca_route = sample_route(
            source=airport_paris,
            destination=airport_barcelona,
        )

        self.flight1 = sample_flight(route=self.barca_paris_route)
        self.flight2 = sample_flight(
            route=self.paris_barca_route,
            departure_time=datetime.datetime(year=2025, month=4, day=19, hour=17, minute=0),
            arrival_time=datetime.datetime(year=2025, month=4, day=19, hour=21, minute=0)
        )

    def test_route_filter(self):
        res = self.client.get(FLIGHT_URL + f"?route={self.barca_paris_route.id}")

        flights = Flight.objects.filter(route__id=self.barca_paris_route.id)
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_flight_by_exact_date(self):
        res = self.client.get(FLIGHT_URL + f"?departure_date={self.flight2.departure_time.date()}")

        flights = Flight.objects.filter(departure_time__date=self.flight2.departure_time.date())
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_flight_by_gt_date(self):
        res = self.client.get(FLIGHT_URL + f"?departure_date__gt={self.flight1.departure_time.date()}")

        flights = Flight.objects.filter(departure_time__date__gt=self.flight1.departure_time.date())
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_flight_by_lt_date(self):
        res = self.client.get(FLIGHT_URL + f"?departure_date__lt={self.flight1.departure_time.date()}")

        flights = Flight.objects.filter(departure_time__date__lt=self.flight1.departure_time.date())
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_flight_by_exact_time(self):
        res = self.client.get(FLIGHT_URL + f"?departure_time={self.flight2.departure_time.time()}")

        flights = Flight.objects.filter(departure_time__time=self.flight2.departure_time.time())
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_flight_by_gt_time(self):
        res = self.client.get(FLIGHT_URL + f"?departure_time__gt={self.flight1.departure_time.time()}")

        flights = Flight.objects.filter(departure_time__time__gt=self.flight1.departure_time.time())
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_flight_by_lt_time(self):
        res = self.client.get(FLIGHT_URL + f"?departure_time__lt={self.flight2.departure_time.time()}")

        flights = Flight.objects.filter(departure_time__time__lt=self.flight2.departure_time.time())
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
