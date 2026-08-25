from app.services.hotel_service import search_hotels


print("=" * 60)
print("GOOGLE HOTELS TEST")
print("=" * 60)

try:

    hotels = search_hotels(
        destination="Goa",
        check_in_date="2026-09-10",
        check_out_date="2026-09-14",
        travelers=2
    )

    print()
    print("Hotels found:", len(hotels))
    print()

    for index, hotel in enumerate(hotels, 1):

        print(f"HOTEL {index}")
        print("-" * 60)

        print(
            "Name:",
            hotel.get("name")
        )

        print(
            "Location:",
            hotel.get("location")
        )

        print(
            "Rating:",
            hotel.get("rating")
        )

        print(
            "Reviews:",
            hotel.get("reviews")
        )

        print(
            "Price per night:",
            hotel.get("price_per_night"),
            "INR"
        )

        print(
            "Total price:",
            hotel.get("total_price"),
            "INR"
        )

        print(
            "Amenities:",
            hotel.get("amenities")
        )

        print(
            "Hotel link:",
            hotel.get("hotel_link")
        )

        print()

    print("=" * 60)
    print("HOTEL SEARCH SUCCESSFUL")
    print("=" * 60)


except Exception as e:

    print()
    print("=" * 60)
    print("HOTEL SEARCH FAILED")
    print("=" * 60)

    print(e)