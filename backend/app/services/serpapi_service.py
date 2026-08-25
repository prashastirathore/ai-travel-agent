import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

if not SERPAPI_KEY:
    raise ValueError("SERPAPI_KEY was not found in .env")


SERPAPI_URL = "https://serpapi.com/search.json"


def run_serpapi(params: dict):
    """
    Generic SERPAPI request.
    """

    request_params = params.copy()
    request_params["api_key"] = SERPAPI_KEY

    response = requests.get(
        SERPAPI_URL,
        params=request_params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise Exception(
            f"SERPAPI Error: {data['error']}"
        )

    return data


def search_google(
    query: str,
    num_results: int = 10
):
    """
    Normal Google search through SERPAPI.
    """

    results = run_serpapi({
        "engine": "google",
        "q": query,
        "gl": "in",
        "hl": "en",
        "num": num_results
    })

    organic_results = results.get(
        "organic_results",
        []
    )

    return [
        {
            "title": result.get("title"),
            "link": result.get("link"),
            "snippet": result.get("snippet")
        }
        for result in organic_results[:num_results]
    ]