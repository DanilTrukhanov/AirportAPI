from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="cities"
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["name"]


class Airport(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="airports"
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["name"]


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="departing_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination_routes"
    )
    distance = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.source.city.name} -> {self.destination.city.name}"


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["first_name", "last_name"]


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField(validators=[MinValueValidator(1)])
    seats_in_row = models.IntegerField(validators=[MinValueValidator(1)])
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Flight(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    crew = models.ManyToManyField(Crew, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    @staticmethod
    def validate_time(departure_time: datetime, arrival_time: datetime):
        if arrival_time < departure_time:
            raise ValidationError(
                {
                    "arrival_time":
                        "Arrival time must be later than departure time."
                }
            )

    def clean(self):
        Flight.validate_time(self.departure_time, self.arrival_time)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ["departure_time"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    @staticmethod
    def validate_ticket(flight: Flight, row: int = None, seat: int = None):
        if not 1 <= row <= flight.airplane.rows:
            raise ValidationError(
                {"row": f"row must be in range (1, {flight.airplane.rows})"}
            )
        if not 1 <= seat <= flight.airplane.seats_in_row:
            raise ValidationError(
                {
                    "seat": f"seat must be in range"
                            f" (1, {flight.airplane.seats_in_row})"
                }
            )

    def clean(self):
        Ticket.validate_ticket(self.flight, row=self.row, seat=self.seat)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["row", "seat"], name="unique_row_and_seat"
            ),
        ]
        ordering = ["row", "seat"]
