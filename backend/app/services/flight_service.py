from app.services.serpapi_service import run_serpapi


AIRPORT_CODES = {
    "indore": "IDR",
    "idr": "IDR",

    "goa": "GOI",
    "goi": "GOI",

    "mumbai": "BOM",
    "bom": "BOM",

    "delhi": "DEL",
    "new delhi": "DEL",
    "del": "DEL",

    "bangalore": "BLR",
    "bengaluru": "BLR",
    "blr": "BLR",

    "hyderabad": "HYD",
    "hyd": "HYD",

    "pune": "PNQ",
    "pnq": "PNQ",

    "ahmedabad": "AMD",
    "amd": "AMD",

    "jaipur": "JAI",
    "jai": "JAI",

    "kolkata": "CCU",
    "ccu": "CCU",

    "chennai": "MAA",
    "maa": "MAA",

    "lucknow": "LKO",
    "lko": "LKO",

    "bhopal": "BHO",
    "bho": "BHO",

    "nagpur": "NAG",
    "nag": "NAG",

    "kochi": "COK",
    "cochin": "COK",
    "cok": "COK",

    "varanasi": "VNS",
    "vns": "VNS",

    "chandigarh": "IXC",
    "ixc": "IXC",

    "patna": "PAT",
    "pat": "PAT",
}


def get_airport_code(value: str) -> str:

    if not value:
        raise ValueError(
            "Origin or destination cannot be empty."
        )

    cleaned = value.strip().lower()

    if cleaned in AIRPORT_CODES:
        return AIRPORT_CODES[cleaned]

    if len(cleaned) == 3 and cleaned.isalpha():
        return cleaned.upper()

    raise ValueError(
        f"Airport code not found for '{value}'."
    )


def search_flights(
    origin,
    destination,
    departure_date,
    return_date,
    travelers=1
):

    origin_code = get_airport_code(origin)
    destination_code = get_airport_code(destination)

    params = {

        "engine": "google_flights",

        "departure_id":
            origin_code,

        "arrival_id":
            destination_code,

        "outbound_date":
            departure_date,

        "return_date":
            return_date,

        "type": "1",

        "travel_class": "1",

        "adults": travelers,

        "currency": "INR",

        "gl": "in",

        "hl": "en",

        "deep_search": "true"
    }

    results = run_serpapi(params)

    flights = []

    all_flights = (
        results.get("best_flights", [])
        +
        results.get("other_flights", [])
    )

    for flight in all_flights:

        legs = flight.get(
            "flights",
            []
        )

        if not legs:
            continue

        # --------------------------------------------
        # FIRST LEG = ACTUAL DEPARTURE
        # --------------------------------------------

        first_leg = legs[0]

        departure_airport = first_leg.get(
            "departure_airport",
            {}
        )

        # --------------------------------------------
        # LAST LEG = FINAL DESTINATION
        # --------------------------------------------

        last_leg = legs[-1]

        arrival_airport = last_leg.get(
            "arrival_airport",
            {}
        )

        # --------------------------------------------
        # ALL AIRLINES / FLIGHTS
        # --------------------------------------------

        flight_numbers = []

        airlines = []

        for leg in legs:

            airline = leg.get("airline")

            flight_number = leg.get(
                "flight_number"
            )

            if airline and airline not in airlines:
                airlines.append(airline)

            if flight_number:
                flight_numbers.append(
                    flight_number
                )

        # --------------------------------------------
        # STOPS
        # --------------------------------------------

        stops = flight.get("stops")

        if stops is None:
            stops = max(
                len(legs) - 1,
                0
            )

        # --------------------------------------------
        # PRICE
        # --------------------------------------------

        price = flight.get("price")

        if isinstance(price, str):

            cleaned_price = (
                price
                .replace("₹", "")
                .replace(",", "")
                .strip()
            )

            try:
                price = float(
                    cleaned_price
                )
            except ValueError:
                price = None

        # --------------------------------------------
        # SAVE FLIGHT
        # --------------------------------------------

        flights.append({

            "airline":
                ", ".join(airlines),

            "flight_number":
                ", ".join(flight_numbers),

            "departure":
                departure_airport.get(
                    "time"
                ),

            "departure_airport":
                departure_airport.get(
                    "name"
                ),

            "arrival":
                arrival_airport.get(
                    "time"
                ),

            "arrival_airport":
                arrival_airport.get(
                    "name"
                ),

            "duration_minutes":
                flight.get(
                    "total_duration"
                ),

            "stops":
                stops,

            "price_inr":
                price,

            "carbon_emissions":
                flight.get(
                    "carbon_emissions"
                ),

            "booking_token":
                flight.get(
                    "booking_token"
                ),

            "departure_token":
                flight.get(
                    "departure_token"
                ),

            "all_legs":
                legs
        })

    # --------------------------------------------
    # SORT BY PRICE
    # --------------------------------------------

    flights.sort(
        key=lambda x: (
            x["price_inr"]
            if isinstance(
                x["price_inr"],
                (int, float)
            )
            else float("inf")
        )
    )

    return flights[:10]