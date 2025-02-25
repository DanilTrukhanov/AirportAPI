from drf_spectacular.utils import OpenApiParameter, OpenApiExample


COUNTRY_PARAMETERS = [
    OpenApiParameter(
        "country",
        type={"type": "string"},
        description="Search a country by name,not case sensitive",
        examples=[
            OpenApiExample("-"),
            OpenApiExample("Spain", value="Spain"),
        ],
    ),
    OpenApiParameter(
        "ordering",
        type={"type": "string"},
        description="Ordering by country name."
                    " User '-' for descending order (ex. ?ordering=-name)",
        enum=["name", "-name"],
    ),
]

CITY_PARAMETERS = [
    OpenApiParameter(
        "search",
        type={"type": "string"},
        description="Search a city by name, by country name,"
                    " not case sensitive",
        examples=[
            OpenApiExample("-"),
            OpenApiExample("Barcelona", value="Barcelona"),
            OpenApiExample("Spain", value="Spain"),
        ],
    ),
    OpenApiParameter(
        "ordering",
        type={"type": "string"},
        description="Ordering by city name and country name",
        enum=["name", "-name", "country__name", "-country__name"],
    ),
]

AIRPORT_PARAMETERS = [
    OpenApiParameter(
        "search",
        type={"type": "string"},
        description="Search an airport by name,"
                    " by city name,"
                    " by country name, not case sensitive",
        examples=[
            OpenApiExample("-"),
            OpenApiExample(
                "El Prat de Llobregat Aeropuerto", value="el prat"
            ),
            OpenApiExample("Barcelona", value="Barcelona"),
            OpenApiExample("Spain", value="Spain"),
        ],
    ),
    OpenApiParameter(
        "ordering",
        type={"type": "string"},
        description="Ordering by airport name",
        enum=["name", "-name"],
    ),
]

ROUTE_PARAMETERS = [
    OpenApiParameter(
        "search",
        type={"type": "string"},
        description="Search a route by source,"
                    " destination city and country name,"
                    " not case sensitive",
        examples=[
            OpenApiExample("-"),
            OpenApiExample("Paris", value="Paris"),
            OpenApiExample("Barcelona", value="Barcelona"),
        ],
    ),
    OpenApiParameter(
        "source",
        type={"type": "integer"},
        description="Filter by source",
        examples=[
            OpenApiExample("-"),
            OpenApiExample("From Barcelona", value=3),
        ],
    ),
    OpenApiParameter(
        "destination",
        type={"type": "integer"},
        description="Filter by destination",
        examples=[
            OpenApiExample("-"),
            OpenApiExample("To Paris", value=2),
        ],
    ),
    OpenApiParameter(
        "has_flights",
        type={"type": "boolean"},
        description="Show routes that have flights",
    ),
]

FLIGHT_PARAMETERS = [
    OpenApiParameter(
        "departure_date",
        type={"type": "string"},
        description="Search by exact departure date",
        examples=[
            OpenApiExample("-"),
            OpenApiExample("2025-02-21", value="2025-02-21"),
        ],
    ),
    OpenApiParameter(
        "departure_date__gt",
        type={"type": "string"},
        description="Search by date that is later than given departure date",
        examples=[
            OpenApiExample("-"),
            OpenApiExample("2025-02-21", value="2025-02-21"),
        ],
    ),
    OpenApiParameter(
        "departure_date__lt",
        type={"type": "string"},
        description="Search by date that is sooner than given departure date",
        examples=[
            OpenApiExample("-"),
            OpenApiExample("2025-02-27", value="2025-02-27"),
        ],
    ),
    OpenApiParameter(
        "departure_time",
        type={"type": "string"},
        description="Search by exact departure time",
        examples=[
            OpenApiExample("-"),
            OpenApiExample("04:10", value="04:10"),
        ],
    ),
    OpenApiParameter(
        "departure_time__gt",
        type={"type": "string"},
        description="Search by time that is later than given departure time",
        examples=[
            OpenApiExample("-"),
            OpenApiExample("After 04:10", value="04:10"),
        ],
    ),
    OpenApiParameter(
        "departure_time__lt",
        type={"type": "string"},
        description="Search by time that is sooner than given departure time",
        examples=[
            OpenApiExample("-"),
            OpenApiExample("Before 07:00", value="07:00"),
        ],
    ),
    OpenApiParameter(
        "route",
        type={"type": "integer"},
        description="Filter by route",
        examples=[
            OpenApiExample("-"),
            OpenApiExample("Paris -> Barcelona", value=2),
        ],
    ),
    OpenApiParameter(
        "search",
        type={"type": "string"},
        description="Search a flight by route source city name"
                    " and route destination city name,"
                    " not case sensitive",
        examples=[
            OpenApiExample("-"),
            OpenApiExample("Paris", value="Paris"),
            OpenApiExample("Barcelona", value="Barcelona"),
        ],
    ),
]

ORDER_PARAMETERS = [
    OpenApiParameter(
        "ordering",
        type={"type": "string"},
        description="Order by order creation time",
        enum=["created_at", "-created_at"],
    ),
]
