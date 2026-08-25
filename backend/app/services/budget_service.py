# =========================================================
# BUDGET SERVICE
# =========================================================


def _number(value):
    """
    Safely convert a value to float.
    """

    if isinstance(value, (int, float)):

        return float(value)

    if isinstance(value, str):

        cleaned = (
            value
            .replace("₹", "")
            .replace(",", "")
            .strip()
        )

        try:

            return float(cleaned)

        except ValueError:

            return None

    return None


# =========================================================
# FLIGHT COST
# =========================================================

def calculate_flight_cost(
    flights,
    travelers
):
    """
    Calculate flight cost for all travelers.

    SerpAPI Google Flights prices are treated
    as the price for the requested adults,
    but if the result is supplied as a single
    traveler price, this function multiplies
    by travelers.

    Our current Google Flights search passes
    adults=travelers, so the returned price is
    normally already for the requested number
    of travelers.

    Therefore we do NOT multiply it again.
    """

    if not flights:

        return None

    valid_prices = []

    for flight in flights:

        price = _number(
            flight.get("price_inr")
        )

        if price is not None:

            valid_prices.append(price)

    if not valid_prices:

        return None

    return min(valid_prices)


# =========================================================
# HOTEL COST
# =========================================================

def calculate_hotel_cost(hotels):

    if not hotels:

        return None

    valid_prices = []

    for hotel in hotels:

        total_price = _number(
            hotel.get("total_price")
        )

        if total_price is not None:

            valid_prices.append(
                total_price
            )

    if not valid_prices:

        return None

    return min(valid_prices)


# =========================================================
# COMPLETE BUDGET
# =========================================================

def calculate_budget(
    flights,
    hotels,
    travelers,
    days,
    budget
):

    flight_cost = calculate_flight_cost(
        flights,
        travelers
    )

    hotel_cost = calculate_hotel_cost(
        hotels
    )

    # -----------------------------------------------------
    # Reasonable planning estimates
    # -----------------------------------------------------

    food_estimate = (
        1000 * travelers * days
    )

    local_transport_estimate = (
        500 * days
    )

    activities_estimate = (
        500 * travelers * days
    )

    miscellaneous_estimate = (
        500
    )

    # -----------------------------------------------------
    # Known costs
    # -----------------------------------------------------

    known_total = 0

    if flight_cost is not None:

        known_total += flight_cost

    if hotel_cost is not None:

        known_total += hotel_cost

    known_total += food_estimate

    known_total += local_transport_estimate

    known_total += activities_estimate

    known_total += miscellaneous_estimate

    # -----------------------------------------------------
    # Remaining budget
    # -----------------------------------------------------

    if budget is not None:

        remaining_budget = (
            float(budget)
            - known_total
        )

        within_budget = (
            remaining_budget >= 0
        )

    else:

        remaining_budget = None

        within_budget = None

    return {

        "flights_inr":
            flight_cost,

        "hotel_inr":
            hotel_cost,

        "food_estimate_inr":
            food_estimate,

        "local_transport_estimate_inr":
            local_transport_estimate,

        "activities_estimate_inr":
            activities_estimate,

        "miscellaneous_estimate_inr":
            miscellaneous_estimate,

        "estimated_total_inr":
            known_total,

        "remaining_budget_inr":
            remaining_budget,

        "within_budget":
            within_budget
    }