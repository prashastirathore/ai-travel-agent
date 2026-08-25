from app.services.serpapi_service import run_serpapi


def search_hotels(
    destination,
    check_in,
    check_out,
    travelers=1
):
    """
    Search hotels using SerpAPI Google Hotels.
    Returns clean hotel data for the AI travel agent.
    """

    if not destination:
        raise ValueError("Destination is required.")

    if not check_in:
        raise ValueError("Check-in date is required.")

    if not check_out:
        raise ValueError("Check-out date is required.")

    params = {
        "engine": "google_hotels",
        "q": destination,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "adults": travelers,
        "currency": "INR",
        "gl": "in",
        "hl": "en",
        "sort_by": "3"
    }

    results = run_serpapi(params)

    hotels = []

    properties = results.get("properties", [])

    for hotel in properties:

        # =====================================================
        # PRICE PER NIGHT
        # =====================================================

        rate_per_night = hotel.get(
            "rate_per_night",
            {}
        )

        price_per_night = None

        if isinstance(rate_per_night, dict):

            price_per_night = (
                rate_per_night.get("extracted")
                or rate_per_night.get("value")
            )

        elif isinstance(
            rate_per_night,
            (int, float)
        ):

            price_per_night = rate_per_night

        # =====================================================
        # TOTAL PRICE
        # =====================================================

        total_rate = hotel.get(
            "total_rate",
            {}
        )

        total_price = None

        if isinstance(total_rate, dict):

            total_price = (
                total_rate.get("extracted")
                or total_rate.get("value")
            )

        elif isinstance(
            total_rate,
            (int, float)
        ):

            total_price = total_rate

        # =====================================================
        # FALLBACK PRICE
        # =====================================================

        # Some SerpAPI responses may provide the price
        # under different fields.

        if price_per_night is None:

            price_per_night = (
                hotel.get("price_per_night")
                or hotel.get("nightly_price")
            )

        if total_price is None:

            total_price = (
                hotel.get("total_price")
                or hotel.get("price")
            )

        # =====================================================
        # RATING
        # =====================================================

        rating = hotel.get(
            "overall_rating"
        )

        if rating is None:

            rating = hotel.get(
                "rating"
            )

        # =====================================================
        # REVIEWS
        # =====================================================

        reviews = hotel.get(
            "reviews"
        )

        # =====================================================
        # HOTEL DATA
        # =====================================================

        hotel_data = {

            "name":
                hotel.get("name"),

            "rating":
                rating,

            "hotel_class":
                hotel.get("hotel_class"),

            "price_per_night":
                price_per_night,

            "total_price":
                total_price,

            "reviews":
                reviews,

            "amenities":
                hotel.get(
                    "amenities",
                    []
                ),

            "description":
                hotel.get(
                    "description"
                ),

            "link":
                hotel.get(
                    "link"
                ),

            "location":
                hotel.get(
                    "gps_coordinates"
                )
        }

        # =====================================================
        # ONLY ADD VALID HOTELS
        # =====================================================

        if hotel_data["name"]:

            hotels.append(
                hotel_data
            )

    # =========================================================
    # SORT CHEAPEST FIRST
    # =========================================================

    hotels.sort(

        key=lambda hotel: (

            hotel.get(
                "total_price"
            )

            if isinstance(
                hotel.get(
                    "total_price"
                ),
                (int, float)
            )

            else (

                hotel.get(
                    "price_per_night"
                )

                if isinstance(
                    hotel.get(
                        "price_per_night"
                    ),
                    (int, float)
                )

                else float("inf")
            )
        )
    )

    # =========================================================
    # RETURN TOP 10 HOTELS
    # =========================================================

    return hotels[:10]