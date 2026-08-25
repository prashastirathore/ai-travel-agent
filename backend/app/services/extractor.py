import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.models.trip import TripRequirements


# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in .env")


# Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=api_key
)


# Structured output
structured_llm = llm.with_structured_output(TripRequirements)


def extract_trip_details(user_message: str) -> TripRequirements:

    prompt = f"""
You are a travel planning assistant.

Extract the trip information from the user's message.

Extract only information that the user actually provides.

If information is missing:
- Use null for optional fields.
- Do not invent dates.
- Do not invent budget.
- Do not invent preferences.

For currency:
- If the user says rupees, use INR.
- If the user says ₹, use INR.
- Otherwise use the currency mentioned by the user.

User message:

{user_message}
"""

    return structured_llm.invoke(prompt)


# Test extractor directly
if __name__ == "__main__":

    message = """
    I want to travel from Indore to Goa for 5 days
    with my friend. Our total budget is 40000 rupees.
    We love beaches and nightlife.
    """

    trip = extract_trip_details(message)

    print("\nExtracted Trip:\n")
    print(trip)