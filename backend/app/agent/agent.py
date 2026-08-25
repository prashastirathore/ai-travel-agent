from app.services.extractor import extract_trip_details
from app.services.flight_service import search_flights
from app.services.hotel_service import search_hotels
from app.services.travel_search_service import (
    search_destination,
    search_activities,
    search_restaurants
)
from app.services.budget_service import calculate_budget
from app.services.gemini_service import generate_itinerary


def run_travel_agent(user_message: str):

    # =====================================================
    # 1. EXTRACT TRIP DETAILS
    # =====================================================

    trip = extract_trip_details(user_message)

    # =====================================================
    # 2. VALIDATION
    # =====================================================

    if not trip.origin:
        return {
            "success": False,
            "error": "Please provide your starting city."
        }

    if not trip.destination:
        return {
            "success": False,
            "error": "Please provide your destination."
        }

    if not trip.days:
        return {
            "success": False,
            "error": "Please provide number of days."
        }

    # =====================================================
    # 3. FLIGHTS
    # =====================================================

    flights = []

    if trip.start_date and trip.end_date:

        flights = search_flights(
            origin=trip.origin,
            destination=trip.destination,
            departure_date=trip.start_date,
            return_date=trip.end_date,
            travelers=trip.travelers
        )

    # =====================================================
    # 4. HOTELS
    # =====================================================

    hotels = []

    if trip.start_date and trip.end_date:

        hotels = search_hotels(
            destination=trip.destination,
            check_in_date=trip.start_date,
            check_out_date=trip.end_date,
            travelers=trip.travelers
        )

    # =====================================================
    # 5. DESTINATION SEARCH
    # =====================================================

    places = search_destination(
        trip.destination
    )[:5]

    activities = search_activities(
        trip.destination
    )[:5]

    restaurants = search_restaurants(
        trip.destination
    )[:5]

    travel_information = {
        "places": places,
        "activities": activities,
        "restaurants": restaurants
    }

    # =====================================================
    # 6. BUDGET
    # =====================================================

    budget_breakdown = calculate_budget(
        flights=flights,
        hotels=hotels,
        travelers=trip.travelers,
        days=trip.days,
        budget=trip.budget
    )

    # =====================================================
    # 7. GEMINI ITINERARY
    # =====================================================

    itinerary = generate_itinerary(
        origin=trip.origin,
        destination=trip.destination,
        departure_date=trip.start_date,
        return_date=trip.end_date,
        days=trip.days,
        budget=trip.budget,
        travelers=trip.travelers,
        preferences=trip.interests,
        travel_information=travel_information,
        flights=flights[:5],
        hotels=hotels[:5],
        budget_breakdown=budget_breakdown
    )

    # =====================================================
    # 8. CLEAN RESPONSE
    # =====================================================

    clean_flights = []

    for flight in flights[:5]:

        clean_flights.append({
            "airline": flight.get("airline"),
            "flight_number": flight.get("flight_number"),
            "departure": flight.get("departure"),
            "arrival": flight.get("arrival"),
            "duration_minutes": flight.get("duration_minutes"),
            "stops": flight.get("stops"),
            "price_inr": flight.get("price_inr")
        })

    clean_hotels = []

    for hotel in hotels[:5]:

        clean_hotels.append({
            "name": hotel.get("name"),
            "rating": hotel.get("rating"),
            "hotel_class": hotel.get("hotel_class"),
            "total_price": hotel.get("total_price")
        })

    return {

        "success": True,

        "trip": {
            "origin": trip.origin,
            "destination": trip.destination,
            "start_date": trip.start_date,
            "end_date": trip.end_date,
            "days": trip.days,
            "travelers": trip.travelers,
            "budget": trip.budget,
            "currency": trip.currency,
            "interests": trip.interests
        },

        "flight_options": clean_flights,

        "hotel_options": clean_hotels,

        "travel_information": travel_information,

        "budget_breakdown": budget_breakdown,

        "itinerary": itinerary
    }