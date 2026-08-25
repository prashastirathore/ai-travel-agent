from app.services.serpapi_service import search_google


def search_destination(
    destination: str
) -> list:

    return search_google(
        f"best places to visit in {destination}, India",
        num_results=10
    )


def search_activities(
    destination: str
) -> list:

    return search_google(
        f"best things to do in {destination}, India",
        num_results=10
    )


def search_restaurants(
    destination: str
) -> list:

    return search_google(
        f"best local restaurants food in {destination}, India",
        num_results=10
    )