from app.services.serpapi_service import run_serpapi


params = {
    "engine": "google_hotels",
    "q": "hotels in Goa, India",
    "check_in_date": "2026-09-10",
    "check_out_date": "2026-09-14",
    "adults": 2,
    "children": 0,
    "currency": "INR",
    "gl": "in",
    "hl": "en",
    "sort_by": "3"
}


print("=" * 70)
print("RAW GOOGLE HOTELS RESPONSE")
print("=" * 70)

try:

    results = run_serpapi(params)

    print("\nTop-level keys:")
    print(results.keys())

    properties = results.get("properties", [])

    print("\nProperties found:", len(properties))

    if properties:

        print("\nFIRST HOTEL RAW DATA")
        print("=" * 70)

        first_hotel = properties[0]

        print(first_hotel)

        print("\n")
        print("FIRST HOTEL KEYS")
        print("=" * 70)

        print(first_hotel.keys())

except Exception as e:

    print("\nERROR:")
    print(type(e).__name__)
    print(e)