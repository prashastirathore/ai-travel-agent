from app.services.serpapi_service import (
    search_google
)


print("=" * 50)

print("SERPAPI TEST")

print("=" * 50)


try:

    results = search_google(

        "best places to visit in Goa",

        num_results=5

    )


    print(
        "\nSUCCESS! SerpAPI is working.\n"
    )


    for i, result in enumerate(
        results,
        1
    ):

        print(
            f"Result {i}"
        )

        print("-" * 50)

        print(
            "Title:",
            result.get("title")
        )

        print(
            "Link:",
            result.get("link")
        )

        print(
            "Description:",
            result.get("snippet")
        )

        print()


except Exception as exc:

    print(
        "\nERROR:"
    )

    print(exc)