DESTINATION_KNOWLEDGE = {
    "goa": {
        "overview": "Goa is known for beaches, nightlife, Portuguese heritage, water activities and local seafood.",
        "tips": [
            "North Goa is popular for nightlife and beaches.",
            "South Goa is generally quieter and more relaxed.",
            "Scooters are commonly used for local travel."
        ]
    },

    "mumbai": {
        "overview": "Mumbai is known for Marine Drive, Gateway of India, markets, food and nightlife.",
        "tips": [
            "Use local trains or app-based cabs for transportation.",
            "Marine Drive is especially popular around sunset."
        ]
    },

    "delhi": {
        "overview": "Delhi combines historical monuments, markets, museums and diverse food.",
        "tips": [
            "Metro is useful for moving around major areas.",
            "Visit historical attractions earlier in the day."
        ]
    },

    "indore": {
        "overview": "Indore is known for food, markets, Rajwada and nearby attractions.",
        "tips": [
            "Try local street food.",
            "Rajwada and Sarafa are popular attractions."
        ]
    }
}


def get_destination_knowledge(destination: str):

    if not destination:
        return {}

    key = destination.strip().lower()

    return DESTINATION_KNOWLEDGE.get(
        key,
        {
            "overview": f"General travel information for {destination}.",
            "tips": []
        }
    )