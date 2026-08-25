import os
import json

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY was not found in .env")


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=GEMINI_API_KEY
)


def generate_itinerary(
    origin,
    destination,
    departure_date,
    return_date,
    days,
    budget,
    travelers,
    preferences,
    travel_information,
    flights,
    hotels,
    budget_breakdown=None,
    rag_context=None,
    comparison=None
):

    budget = budget if budget is not None else 0
    preferences = preferences or []
    travel_information = travel_information or {}
    flights = flights or []
    hotels = hotels or []
    budget_breakdown = budget_breakdown or {}
    rag_context = rag_context or {}
    comparison = comparison or {}

    prompt = f"""
You are an expert AI travel planning agent.

Create a practical and personalized travel plan.

Use ONLY the data supplied by the backend.

==================================================
TRIP
==================================================

Origin: {origin}
Destination: {destination}

Departure: {departure_date}
Return: {return_date}

Days: {days}
Travelers: {travelers}
Budget INR: {budget}

Preferences:
{json.dumps(preferences, indent=2, default=str)}


==================================================
FLIGHTS
==================================================

{json.dumps(flights, indent=2, default=str)}


==================================================
HOTELS
==================================================

{json.dumps(hotels, indent=2, default=str)}


==================================================
DESTINATION SEARCH
==================================================

{json.dumps(travel_information, indent=2, default=str)}


==================================================
RAG CONTEXT
==================================================

{json.dumps(rag_context, indent=2, default=str)}


==================================================
COMPARISON
==================================================

{json.dumps(comparison, indent=2, default=str)}


==================================================
BUDGET
==================================================

{json.dumps(budget_breakdown, indent=2, default=str)}


==================================================
RULES
==================================================

1. Do not invent flights.
2. Do not invent flight prices.
3. Do not invent hotels.
4. Do not invent hotel prices.
5. Use backend flight and hotel data.
6. Use backend budget calculations as the source of truth.
7. Respect the user's preferences.
8. Use the supplied RAG context when relevant.
9. Do not claim unsupported facts.
10. Create exactly {days} itinerary days.
11. Keep activities geographically practical.
12. Include local food.
13. Include practical travel tips.
14. If budget is exceeded, clearly say so.
15. If budget is sufficient, mention remaining budget.
16. Return ONLY valid JSON.
17. Do not use markdown code fences.

Each itinerary day must contain:

day
title
morning
afternoon
evening
breakfast
lunch
dinner
local_transport
estimated_daily_cost_inr


==================================================
OUTPUT
==================================================

Return exactly:

{{
    "trip_summary": {{
        "origin": "{origin}",
        "destination": "{destination}",
        "departure_date": "{departure_date}",
        "return_date": "{return_date}",
        "days": {days},
        "travelers": {travelers},
        "budget_inr": {budget}
    }},

    "flight_comparison": {{}},

    "hotel_comparison": {{}},

    "budget_breakdown": {json.dumps(budget_breakdown, default=str)},

    "itinerary": [],

    "restaurant_recommendations": [],

    "travel_tips": [],

    "important_note": ""
}}
"""

    response = llm.invoke(prompt)

    content = response.content

    if isinstance(content, list):
        text = ""

        for item in content:
            if isinstance(item, dict):
                text += str(item.get("text", ""))
            else:
                text += str(item)

        content = text

    content = str(content).strip()

    if content.startswith("```json"):
        content = content[7:]

    elif content.startswith("```"):
        content = content[3:]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    try:
        return json.loads(content)

    except json.JSONDecodeError:

        return {
            "error": "Gemini returned invalid JSON",
            "raw_response": content
        }