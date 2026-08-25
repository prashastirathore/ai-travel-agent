from app.services.flight_service import search_flights


print("=" * 60)
print("GOOGLE FLIGHTS TEST")
print("=" * 60)


try:

    flights = search_flights(

        origin="Indore",

        destination="Goa",

        departure_date="2026-09-10",

        return_date="2026-09-14",

        travelers=2
    )


    print(
        f"\nFlights found: {len(flights)}"
    )


    for i, flight in enumerate(
        flights,
        1
    ):

        print("\n")

        print(
            f"FLIGHT {i}"
        )

        print("-" * 60)

        print(
            "Airline:",
            flight.get("airline")
        )

        print(
            "Flight:",
            flight.get("flight_number")
        )

        print(
            "Departure:",
            flight.get("departure")
        )

        print(
            "Arrival:",
            flight.get("arrival")
        )

        print(
            "From:",
            flight.get("departure_airport")
        )

        print(
            "To:",
            flight.get("arrival_airport")
        )

        print(
            "Duration:",
            flight.get("duration_minutes"),
            "minutes"
        )

        print(
            "Stops:",
            flight.get("stops")
        )

        print(
            "Price:",
            flight.get("price_inr"),
            "INR"
        )


    print("\n")

    print("=" * 60)
    print("FLIGHT SEARCH SUCCESSFUL")
    print("=" * 60)


except Exception as e:

    print("\n")

    print("=" * 60)
    print("FLIGHT SEARCH FAILED")
    print("=" * 60)

    print(e)