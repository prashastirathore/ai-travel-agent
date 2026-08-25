from typing import List, Dict, Any


# ============================================================
# SAFE NUMBER
# ============================================================

def _number(value):
    if isinstance(value, (int, float)):
        return float(value)

    return None


# ============================================================
# FLIGHT COMPARISON
# ============================================================

def compare_flights(
    flights: List[Dict[str, Any]]
):

    valid_flights = [
        flight
        for flight in flights
        if _number(
            flight.get("price_inr")
        ) is not None
    ]

    if not valid_flights:

        return {
            "cheapest": None,
            "fastest": None,
            "best_value": None,
            "alternatives": []
        }

    # --------------------------------------------------------
    # CHEAPEST
    # --------------------------------------------------------

    cheapest = min(
        valid_flights,
        key=lambda flight:
            flight["price_inr"]
    )

    # --------------------------------------------------------
    # FASTEST
    # --------------------------------------------------------

    flights_with_duration = [

        flight
        for flight in valid_flights

        if _number(
            flight.get(
                "duration_minutes"
            )
        ) is not None

    ]

    fastest = None

    if flights_with_duration:

        fastest = min(

            flights_with_duration,

            key=lambda flight:
                flight[
                    "duration_minutes"
                ]

        )

    # --------------------------------------------------------
    # BEST VALUE
    #
    # Prefer:
    # - lower price
    # - shorter duration
    # - fewer stops
    # --------------------------------------------------------

    def value_score(flight):

        price = _number(
            flight.get(
                "price_inr"
            )
        ) or 999999

        duration = _number(
            flight.get(
                "duration_minutes"
            )
        ) or 9999

        stops = _number(
            flight.get(
                "stops"
            )
        )

        if stops is None:
            stops = 2

        return (
            price * 0.5
            + duration * 20
            + stops * 5000
        )

    best_value = min(
        valid_flights,
        key=value_score
    )

    # --------------------------------------------------------
    # ALTERNATIVES
    # --------------------------------------------------------

    alternatives = []

    seen = set()

    for flight in valid_flights:

        key = (
            flight.get(
                "airline"
            ),
            flight.get(
                "flight_number"
            ),
            flight.get(
                "price_inr"
            )
        )

        if key in seen:
            continue

        seen.add(key)

        alternatives.append(
            flight
        )

    return {

        "cheapest":
            cheapest,

        "fastest":
            fastest,

        "best_value":
            best_value,

        "alternatives":
            alternatives[:5]

    }


# ============================================================
# HOTEL COMPARISON
# ============================================================

def compare_hotels(
    hotels: List[Dict[str, Any]]
):

    valid_hotels = [

        hotel
        for hotel in hotels

        if _number(
            hotel.get(
                "total_price"
            )
        ) is not None

    ]

    if not valid_hotels:

        return {

            "cheapest":
                None,

            "highest_rated":
                None,

            "best_value":
                None,

            "alternatives":
                []

        }

    # --------------------------------------------------------
    # CHEAPEST
    # --------------------------------------------------------

    cheapest = min(

        valid_hotels,

        key=lambda hotel:
            hotel[
                "total_price"
            ]

    )

    # --------------------------------------------------------
    # HIGHEST RATED
    # --------------------------------------------------------

    rated_hotels = [

        hotel
        for hotel in valid_hotels

        if _number(
            hotel.get(
                "rating"
            )
        ) is not None

    ]

    highest_rated = None

    if rated_hotels:

        highest_rated = max(

            rated_hotels,

            key=lambda hotel:
                hotel[
                    "rating"
                ]

        )

    # --------------------------------------------------------
    # BEST VALUE
    # --------------------------------------------------------

    def hotel_value_score(hotel):

        price = _number(
            hotel.get(
                "total_price"
            )
        ) or 999999

        rating = _number(
            hotel.get(
                "rating"
            )
        ) or 0

        reviews = _number(
            hotel.get(
                "reviews"
            )
        ) or 0

        # Lower price is better.
        # Higher rating is better.
        # Reviews provide a small confidence bonus.

        return (
            price
            - (rating * 1000)
            - min(reviews, 1000) * 0.5
        )

    best_value = min(

        valid_hotels,

        key=hotel_value_score

    )

    return {

        "cheapest":
            cheapest,

        "highest_rated":
            highest_rated,

        "best_value":
            best_value,

        "alternatives":
            valid_hotels[:5]

    }


# ============================================================
# COMPLETE COMPARISON
# ============================================================

def compare_travel_options(
    flights,
    hotels
):

    flight_comparison = compare_flights(
        flights
    )

    hotel_comparison = compare_hotels(
        hotels
    )

    return {

        "flight_comparison":
            flight_comparison,

        "hotel_comparison":
            hotel_comparison

    }