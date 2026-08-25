from fastapi import APIRouter, HTTPException
from app.models.travel import TravelRequest

from app.services.flight_service import search_flights
from app.services.hotel_service import search_hotels
from app.services.travel_search_service import (
    search_destination,
    search_activities,
    search_restaurants
)

from app.services.budget_service import calculate_budget
from app.services.travel_comparison_service import compare_travel_options
from app.services.gemini_service import generate_itinerary


router = APIRouter(
    prefix="/travel",
    tags=["Travel"]
)


# =========================================================
# TEMPORARY SESSION STORAGE
# =========================================================

sessions = {}


# =========================================================
# START TRIP
# =========================================================

@router.post("/start")
def start_trip(request: TravelRequest):

    try:

        session_id = str(len(sessions) + 1)

        flights = search_flights(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            travelers=request.travelers
        )

        sessions[session_id] = {
            "request": request,
            "flights": flights
        }

        return {
            "success": True,
            "session_id": session_id,
            "stage": "flights",
            "message": "Here are the available flights. Please approve one to continue.",
            "flights": flights
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# APPROVE FLIGHT
# =========================================================

@router.post("/approve-flight/{session_id}")
def approve_flight(
    session_id: str,
    flight_index: int = 0
):

    try:

        if session_id not in sessions:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        session = sessions[session_id]

        flights = session["flights"]

        if not flights:
            raise HTTPException(
                status_code=404,
                detail="No flights found"
            )

        if flight_index < 0 or flight_index >= len(flights):
            raise HTTPException(
                status_code=400,
                detail="Invalid flight index"
            )

        selected_flight = flights[flight_index]

        request = session["request"]

        hotels = search_hotels(
            destination=request.destination,
            check_in=request.departure_date,
            check_out=request.return_date,
            travelers=request.travelers
        )

        session["selected_flight"] = selected_flight
        session["hotels"] = hotels

        return {
            "success": True,
            "session_id": session_id,
            "stage": "hotels",
            "message": "Flight approved. Here are the available hotels.",
            "selected_flight": selected_flight,
            "hotels": hotels
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# APPROVE HOTEL
# =========================================================

@router.post("/approve-hotel/{session_id}")
def approve_hotel(
    session_id: str,
    hotel_index: int = 0
):

    try:

        if session_id not in sessions:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        session = sessions[session_id]

        hotels = session.get("hotels", [])

        if not hotels:
            raise HTTPException(
                status_code=404,
                detail="No hotels found"
            )

        if hotel_index < 0 or hotel_index >= len(hotels):
            raise HTTPException(
                status_code=400,
                detail="Invalid hotel index"
            )

        selected_hotel = hotels[hotel_index]

        request = session["request"]

        places = search_destination(
            request.destination
        )

        activities = search_activities(
            request.destination
        )

        restaurants = search_restaurants(
            request.destination
        )

        session["selected_hotel"] = selected_hotel

        session["travel_information"] = {
            "places": places,
            "activities": activities,
            "restaurants": restaurants
        }

        return {
            "success": True,
            "session_id": session_id,
            "stage": "activities",
            "message": "Hotel approved. Here are activities for your trip.",
            "selected_hotel": selected_hotel,
            "places": places,
            "activities": activities,
            "restaurants": restaurants
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# APPROVE ACTIVITIES
# =========================================================

@router.post("/approve-activities/{session_id}")
def approve_activities(
    session_id: str
):

    try:

        if session_id not in sessions:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        session = sessions[session_id]

        request = session["request"]

        flights = session.get("flights", [])
        hotels = session.get("hotels", [])

        selected_flight = session.get(
            "selected_flight"
        )

        selected_hotel = session.get(
            "selected_hotel"
        )

        travel_information = session.get(
            "travel_information",
            {}
        )

        # -------------------------------------------------
        # Budget
        # -------------------------------------------------

        budget = calculate_budget(
            flights=[selected_flight] if selected_flight else flights,
            hotels=[selected_hotel] if selected_hotel else hotels,
            travelers=request.travelers,
            days=request.days,
            budget=request.budget
        )

        session["budget_breakdown"] = budget

        return {
            "success": True,
            "session_id": session_id,
            "stage": "itinerary",
            "message": "Activities approved. Generate your final itinerary.",
            "budget_breakdown": budget
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# FINAL ITINERARY
# =========================================================

@router.post("/generate-itinerary/{session_id}")
def generate_final_itinerary(
    session_id: str
):

    try:

        if session_id not in sessions:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        session = sessions[session_id]

        request = session["request"]

        selected_flight = session.get(
            "selected_flight"
        )

        selected_hotel = session.get(
            "selected_hotel"
        )

        travel_information = session.get(
            "travel_information",
            {}
        )

        budget_breakdown = session.get(
            "budget_breakdown",
            {}
        )

        result = generate_itinerary(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            days=request.days,
            budget=request.budget,
            travelers=request.travelers,
            preferences=request.preferences,
            travel_information=travel_information,
            flights=[selected_flight] if selected_flight else [],
            hotels=[selected_hotel] if selected_hotel else [],
            budget_breakdown=budget_breakdown
        )

        session["final_itinerary"] = result

        return {
            "success": True,
            "stage": "complete",
            "message": "Your complete travel plan is ready!",
            "result": result
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )