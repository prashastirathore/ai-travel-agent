from typing import TypedDict, Optional, Any

from langgraph.graph import (
    StateGraph,
    START,
    END
)

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


# =========================================================
# STATE
# =========================================================

class TravelState(TypedDict, total=False):

    user_message: str

    trip: Optional[Any]

    flights: list

    hotels: list

    places: list

    activities: list

    restaurants: list

    budget_breakdown: dict

    itinerary: Any

    result: dict


# =========================================================
# NODE 1 - EXTRACT
# =========================================================

def extract_trip(state: TravelState):

    trip = extract_trip_details(
        state["user_message"]
    )

    return {
        "trip": trip
    }


# =========================================================
# NODE 2 - SEARCH
# =========================================================

def search_travel_data(state: TravelState):

    trip = state["trip"]

    flights = []

    hotels = []

    if trip.start_date and trip.end_date:

        flights = search_flights(
            origin=trip.origin,
            destination=trip.destination,
            departure_date=trip.start_date,
            return_date=trip.end_date,
            travelers=trip.travelers
        )

        hotels = search_hotels(
            destination=trip.destination,
            check_in_date=trip.start_date,
            check_out_date=trip.end_date,
            travelers=trip.travelers
        )

    places = search_destination(
        trip.destination
    )[:5]

    activities = search_activities(
        trip.destination
    )[:5]

    restaurants = search_restaurants(
        trip.destination
    )[:5]

    return {

        "flights": flights[:5],

        "hotels": hotels[:5],

        "places": places,

        "activities": activities,

        "restaurants": restaurants
    }


# =========================================================
# NODE 3 - BUDGET
# =========================================================

def calculate_trip_budget(state: TravelState):

    trip = state["trip"]

    budget = calculate_budget(

        flights=state.get(
            "flights",
            []
        ),

        hotels=state.get(
            "hotels",
            []
        ),

        travelers=trip.travelers,

        days=trip.days,

        budget=trip.budget
    )

    return {
        "budget_breakdown": budget
    }


# =========================================================
# NODE 4 - GEMINI
# =========================================================

def create_itinerary(state: TravelState):

    trip = state["trip"]

    travel_information = {

        "places":
            state.get(
                "places",
                []
            ),

        "activities":
            state.get(
                "activities",
                []
            ),

        "restaurants":
            state.get(
                "restaurants",
                []
            )
    }

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

        flights=state.get(
            "flights",
            []
        ),

        hotels=state.get(
            "hotels",
            []
        ),

        budget_breakdown=state.get(
            "budget_breakdown",
            {}
        )
    )

    return {
        "itinerary": itinerary
    }


# =========================================================
# BUILD GRAPH
# =========================================================

def build_graph():

    graph = StateGraph(
        TravelState
    )

    graph.add_node(
        "extract_trip",
        extract_trip
    )

    graph.add_node(
        "search_travel_data",
        search_travel_data
    )

    graph.add_node(
        "calculate_trip_budget",
        calculate_trip_budget
    )

    graph.add_node(
        "create_itinerary",
        create_itinerary
    )

    graph.add_edge(
        START,
        "extract_trip"
    )

    graph.add_edge(
        "extract_trip",
        "search_travel_data"
    )

    graph.add_edge(
        "search_travel_data",
        "calculate_trip_budget"
    )

    graph.add_edge(
        "calculate_trip_budget",
        "create_itinerary"
    )

    graph.add_edge(
        "create_itinerary",
        END
    )

    return graph.compile()