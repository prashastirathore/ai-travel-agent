import { useState } from "react";
import "./App.css";

const API = "https://ai-travel-agent-7ket.onrender.com";

function App() {
  const [stage, setStage] = useState("form");
  const [sessionId, setSessionId] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);

  const [form, setForm] = useState({
    origin: "Indore",
    destination: "Goa",
    departure_date: "2026-09-10",
    return_date: "2026-09-14",
    days: 5,
    travelers: 2,
    budget: 40000,
    preferences: ["beaches", "nightlife"],
  });

  const updateForm = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  // =====================================================
  // SAFE HELPERS
  // =====================================================

  const safeText = (value, fallback = "Not available") => {
    if (value === null || value === undefined || value === "") {
      return fallback;
    }

    if (typeof value === "object") {
      return fallback;
    }

    return String(value);
  };

  // =====================================================
  // PRICE FORMATTER
  // =====================================================

  const formatPrice = (value) => {
    if (value === null || value === undefined || value === "") {
      return "Price unavailable";
    }

    // If price is an object, try to extract a useful value
    if (typeof value === "object") {
      const possibleValues = [
        value.extracted_lowest,
        value.extractedLowest,
        value.lowest,
        value.amount,
        value.value,
        value.price,
        value.total,
      ];

      for (const item of possibleValues) {
        if (
          item !== null &&
          item !== undefined &&
          item !== ""
        ) {
          return formatPrice(item);
        }
      }

      return "Price unavailable";
    }

    // Number
    if (typeof value === "number") {
      if (Number.isNaN(value)) {
        return "Price unavailable";
      }

      return `₹${value.toLocaleString("en-IN")}`;
    }

    // String
    const text = String(value).trim();

    if (!text) {
      return "Price unavailable";
    }

    // Already contains currency
    if (
      text.includes("₹") ||
      text.includes("$") ||
      text.includes("€") ||
      text.includes("£")
    ) {
      return text;
    }

    // Remove commas and currency-like characters
    const numericText = text.replace(/[^\d.-]/g, "");
    const number = Number(numericText);

    if (!Number.isNaN(number)) {
      return `₹${number.toLocaleString("en-IN")}`;
    }

    return text;
  };

  // =====================================================
  // HOTEL LOCATION
  // =====================================================

  const getHotelLocation = (hotel) => {
    const location = hotel?.location;

    // Object: { latitude, longitude }
    if (
      location &&
      typeof location === "object" &&
      !Array.isArray(location)
    ) {
      const latitude = location.latitude;
      const longitude = location.longitude;

      if (
        latitude !== undefined &&
        longitude !== undefined
      ) {
        return `${latitude}, ${longitude}`;
      }

      return "Location available";
    }

    // String location
    if (typeof location === "string") {
      return location;
    }

    // Try common alternative fields
    if (hotel?.address) {
      return safeText(hotel.address);
    }

    if (hotel?.city) {
      return safeText(hotel.city);
    }

    return "Location unavailable";
  };

  // =====================================================
  // HOTEL PRICE PER NIGHT
  // =====================================================
  // Supports:
  //
  // price_per_night
  // pricePerNight
  // nightly_price
  // nightlyPrice
  // price
  // amount
  //
  // AND SerpAPI-style:
  //
  // rate_per_night: {
  //    lowest: "$100",
  //    extracted_lowest: 100
  // }
  //
  // AND:
  //
  // total_rate: {
  //    lowest: "$500",
  //    extracted_lowest: 500
  // }
  // =====================================================

  const getHotelPricePerNight = (hotel) => {
    if (!hotel) {
      return null;
    }

    const possiblePrices = [
      hotel.price_per_night,
      hotel.pricePerNight,
      hotel.nightly_price,
      hotel.nightlyPrice,

      // SerpAPI Google Hotels
      hotel.rate_per_night?.extracted_lowest,
      hotel.rate_per_night?.lowest,

      hotel.ratePerNight?.extracted_lowest,
      hotel.ratePerNight?.lowest,

      // Other common API formats
      hotel.nightly_rate,
      hotel.nightlyRate,

      hotel.price,
      hotel.amount,
      hotel.rate,

      // Sometimes price is nested
      hotel.pricing?.price_per_night,
      hotel.pricing?.pricePerNight,
      hotel.pricing?.nightly_price,
      hotel.pricing?.nightlyPrice,
      hotel.pricing?.amount,
      hotel.pricing?.price,

      hotel.cost?.per_night,
      hotel.cost?.perNight,
      hotel.cost?.nightly,
      hotel.cost?.amount,

      hotel.rates?.price_per_night,
      hotel.rates?.pricePerNight,
      hotel.rates?.nightly,
      hotel.rates?.amount,
    ];

    for (const price of possiblePrices) {
      if (
        price !== null &&
        price !== undefined &&
        price !== ""
      ) {
        return price;
      }
    }

    return null;
  };

  // =====================================================
  // HOTEL TOTAL PRICE
  // =====================================================

  const getHotelTotalPrice = (hotel) => {
    if (!hotel) {
      return null;
    }

    const possiblePrices = [
      hotel.total_price,
      hotel.totalPrice,
      hotel.total_amount,
      hotel.totalAmount,
      hotel.estimated_total_inr,

      // SerpAPI Google Hotels
      hotel.total_rate?.extracted_lowest,
      hotel.total_rate?.lowest,

      hotel.totalRate?.extracted_lowest,
      hotel.totalRate?.lowest,

      // Other common formats
      hotel.total,
      hotel.estimated_total,

      hotel.pricing?.total_price,
      hotel.pricing?.totalPrice,
      hotel.pricing?.total,
      hotel.pricing?.estimated_total,

      hotel.cost?.total,
      hotel.cost?.estimated_total,

      hotel.rates?.total,
    ];

    for (const price of possiblePrices) {
      if (
        price !== null &&
        price !== undefined &&
        price !== ""
      ) {
        return price;
      }
    }

    return null;
  };

  // =====================================================
  // START TRIP
  // =====================================================

  const startTrip = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API}/travel/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...form,
          days: Number(form.days),
          travelers: Number(form.travelers),
          budget: Number(form.budget),
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.detail || "Failed to start trip"
        );
      }

      console.log("START RESPONSE:", result);

      setSessionId(result.session_id);
      setData(result);
      setStage("flights");
    } catch (err) {
      console.error("START ERROR:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // APPROVE FLIGHT
  // =====================================================

  const approveFlight = async (index) => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API}/travel/approve-flight/${sessionId}?flight_index=${index}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      console.log(
        "FLIGHT APPROVAL RESPONSE:",
        result
      );

      if (!response.ok) {
        throw new Error(
          result.detail || "Flight approval failed"
        );
      }

      setData(result);
      setStage("hotels");
    } catch (err) {
      console.error(
        "FLIGHT APPROVAL ERROR:",
        err
      );
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // APPROVE HOTEL
  // =====================================================

  const approveHotel = async (index) => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API}/travel/approve-hotel/${sessionId}?hotel_index=${index}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      console.log(
        "HOTEL APPROVAL RESPONSE:",
        result
      );

      if (!response.ok) {
        throw new Error(
          result.detail || "Hotel approval failed"
        );
      }

      setData(result);
      setStage("activities");
    } catch (err) {
      console.error(
        "HOTEL APPROVAL ERROR:",
        err
      );
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // APPROVE ACTIVITIES
  // =====================================================

  const approveActivities = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API}/travel/approve-activities/${sessionId}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      console.log(
        "ACTIVITIES RESPONSE:",
        result
      );

      if (!response.ok) {
        throw new Error(
          result.detail || "Activity approval failed"
        );
      }

      setData(result);
      setStage("itinerary");
    } catch (err) {
      console.error("ACTIVITY ERROR:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // GENERATE FINAL ITINERARY
  // =====================================================

  const generateItinerary = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API}/travel/generate-itinerary/${sessionId}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      console.log(
        "ITINERARY RESPONSE:",
        result
      );

      if (!response.ok) {
        throw new Error(
          result.detail ||
            "Failed to generate itinerary"
        );
      }

      setData(result);
      setStage("complete");
    } catch (err) {
      console.error(
        "ITINERARY ERROR:",
        err
      );
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div className="app">
        <header className="header">
          <div className="logo">
            ✈️ AI Travel Agent
          </div>

          <p>
            Your trip, planned step by step.
          </p>
        </header>

        <div className="progress">
          <span
            className={
              stage === "form"
                ? "active"
                : ""
            }
          >
            1. Trip
          </span>

          <span
            className={
              stage === "flights"
                ? "active"
                : ""
            }
          >
            2. Flights
          </span>

          <span
            className={
              stage === "hotels"
                ? "active"
                : ""
            }
          >
            3. Hotels
          </span>

          <span
            className={
              stage === "activities"
                ? "active"
                : ""
            }
          >
            4. Activities
          </span>

          <span
            className={
              stage === "itinerary" ||
              stage === "complete"
                ? "active"
                : ""
            }
          >
            5. Itinerary
          </span>
        </div>

        <div className="loading">
          <div className="spinner"></div>

          <p>
            AI Travel Agent is working...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">

      {/* HEADER */}

      <header className="header">
        <div className="logo">
          ✈️ AI Travel Agent
        </div>

        <p>
          Your trip, planned step by step.
        </p>
      </header>

      {/* PROGRESS */}

      <div className="progress">

        <span
          className={
            stage === "form"
              ? "active"
              : ""
          }
        >
          1. Trip
        </span>

        <span
          className={
            stage === "flights"
              ? "active"
              : ""
          }
        >
          2. Flights
        </span>

        <span
          className={
            stage === "hotels"
              ? "active"
              : ""
          }
        >
          3. Hotels
        </span>

        <span
          className={
            stage === "activities"
              ? "active"
              : ""
          }
        >
          4. Activities
        </span>

        <span
          className={
            stage === "itinerary" ||
            stage === "complete"
              ? "active"
              : ""
          }
        >
          5. Itinerary
        </span>

      </div>

      {/* ERROR */}

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {/* FORM */}

      {stage === "form" && (

        <section className="section">

          <div className="hero">

            <h2>
              Plan Your Perfect Trip ✈️
            </h2>

            <p>
              Tell me where you want to go
              and I'll handle the rest.
            </p>

          </div>

          <div className="form-card">

            <div className="form-grid">

              <div className="field">

                <label>
                  From
                </label>

                <input
                  name="origin"
                  value={form.origin}
                  onChange={updateForm}
                  placeholder="Indore"
                />

              </div>

              <div className="field">

                <label>
                  Destination
                </label>

                <input
                  name="destination"
                  value={form.destination}
                  onChange={updateForm}
                  placeholder="Goa"
                />

              </div>

              <div className="field">

                <label>
                  Departure Date
                </label>

                <input
                  type="date"
                  name="departure_date"
                  value={form.departure_date}
                  onChange={updateForm}
                />

              </div>

              <div className="field">

                <label>
                  Return Date
                </label>

                <input
                  type="date"
                  name="return_date"
                  value={form.return_date}
                  onChange={updateForm}
                />

              </div>

              <div className="field">

                <label>
                  Number of Days
                </label>

                <input
                  type="number"
                  name="days"
                  value={form.days}
                  onChange={updateForm}
                  min="1"
                />

              </div>

              <div className="field">

                <label>
                  Travelers
                </label>

                <input
                  type="number"
                  name="travelers"
                  value={form.travelers}
                  onChange={updateForm}
                  min="1"
                />

              </div>

              <div className="field full">

                <label>
                  Total Budget (₹)
                </label>

                <input
                  type="number"
                  name="budget"
                  value={form.budget}
                  onChange={updateForm}
                  min="1000"
                />

              </div>

            </div>

            <button
              className="primary-button"
              onClick={startTrip}
            >
              Start Planning My Trip →
            </button>

          </div>

        </section>
      )}

      {/* FLIGHTS */}

      {stage === "flights" && data && (

        <section className="section">

          <h2>
            ✈️ Step 1 — Choose Your Flight
          </h2>

          <p className="agent-message">
            I've searched the available flights.
            Choose one and I'll continue to hotels.
          </p>

          {Array.isArray(data.flights) &&
          data.flights.length > 0 ? (

            <div className="grid">

              {data.flights.map(
                (flight, index) => (

                  <div
                    className="card"
                    key={index}
                  >

                    <div className="card-top">

                      <span className="badge">
                        Flight {index + 1}
                      </span>

                    </div>

                    <h3>
                      {safeText(
                        flight.airline
                      )}
                    </h3>

                    <p>
                      <b>
                        {safeText(
                          flight.flight_number,
                          "Flight number unavailable"
                        )}
                      </b>
                    </p>

                    <p>
                      {safeText(
                        flight.departure,
                        "Departure unavailable"
                      )}
                    </p>

                    <div className="info-row">

                      <span>
                        Duration
                      </span>

                      <span>
                        {safeText(
                          flight.duration_minutes,
                          "-"
                        )} min
                      </span>

                    </div>

                    <div className="info-row">

                      <span>
                        Stops
                      </span>

                      <span>
                        {safeText(
                          flight.stops,
                          "0"
                        )}
                      </span>

                    </div>

                    <div className="price">
                      {formatPrice(
                        flight.price_inr
                      )}
                    </div>

                    <button
                      className="secondary-button"
                      onClick={() =>
                        approveFlight(index)
                      }
                    >
                      Choose Flight →
                    </button>

                  </div>

                )
              )}

            </div>

          ) : (

            <div className="empty">
              No flights were found.
            </div>

          )}

        </section>
      )}

      {/* HOTELS */}

      {stage === "hotels" && data && (

        <section className="section">

          <h2>
            🏨 Step 2 — Choose Your Hotel
          </h2>

          <p className="agent-message">
            Great! Your flight is approved.
            Now choose your hotel.
          </p>

          {Array.isArray(data.hotels) &&
          data.hotels.length > 0 ? (

            <div className="grid">

              {data.hotels.map(
                (hotel, index) => {

                  const pricePerNight =
                    getHotelPricePerNight(
                      hotel
                    );

                  const totalPrice =
                    getHotelTotalPrice(
                      hotel
                    );

                  return (

                    <div
                      className="card hotel-card"
                      key={index}
                    >

                      <div className="card-top">

                        <span className="badge">
                          Hotel {index + 1}
                        </span>

                        {hotel.rating && (
                          <span className="rating">
                            ⭐{" "}
                            {safeText(
                              hotel.rating
                            )}
                          </span>
                        )}

                      </div>

                      <h3>
                        {safeText(
                          hotel.name,
                          "Hotel"
                        )}
                      </h3>

                      <p>
                        📍{" "}
                        {getHotelLocation(
                          hotel
                        )}
                      </p>

                      {hotel.description && (
                        <p>
                          {safeText(
                            hotel.description
                          )}
                        </p>
                      )}

                      {/* HOTEL PRICE */}

                      <div className="hotel-price-box">

                        {pricePerNight !== null ? (

                          <>
                            <div className="hotel-price">
                              {formatPrice(
                                pricePerNight
                              )}
                            </div>

                            <div className="price-label">
                              per night
                            </div>
                          </>

                        ) : (

                          <div className="hotel-price unavailable">
                            Price unavailable
                          </div>

                        )}

                        {totalPrice !== null && (

                          <div className="hotel-total">

                            Estimated total:{" "}

                            <strong>
                              {formatPrice(
                                totalPrice
                              )}
                            </strong>

                          </div>

                        )}

                      </div>

                      <button
                        className="secondary-button"
                        onClick={() =>
                          approveHotel(
                            index
                          )
                        }
                      >
                        Choose Hotel →
                      </button>

                    </div>

                  );
                }
              )}

            </div>

          ) : (

            <div className="empty">
              No hotels were found.
            </div>

          )}

        </section>
      )}

      {/* ACTIVITIES */}

      {stage === "activities" && data && (

        <section className="section">

          <h2>
            🎯 Step 3 — Activities
          </h2>

          <p className="agent-message">
            Your flight and hotel are approved.
            Here are the activities I found for you.
          </p>

          {Array.isArray(data.activities) &&
          data.activities.length > 0 ? (

            <div className="grid">

              {data.activities
                .slice(0, 6)
                .map(
                  (activity, index) => (

                    <div
                      className="card"
                      key={index}
                    >

                      <h3>
                        {safeText(
                          activity.title,
                          "Activity"
                        )}
                      </h3>

                      <p>
                        {safeText(
                          activity.snippet,
                          "No description available."
                        )}
                      </p>

                    </div>

                  )
                )}

            </div>

          ) : (

            <div className="empty">
              No activities were found.
            </div>

          )}

          <button
            className="primary-button"
            onClick={approveActivities}
          >
            Approve Activities →
          </button>

        </section>
      )}

      {/* ITINERARY */}

      {stage === "itinerary" && data && (

        <section className="section">

          <div className="card">

            <h2>
              🗺️ Step 4 — Final Itinerary
            </h2>

            <p className="agent-message">
              Everything is selected.
              Shall I generate your complete
              day-by-day itinerary?
            </p>

            <div className="budget">

              <h3>
                Budget Estimate
              </h3>

              <p>

                <span>
                  Estimated Total:
                </span>

                <strong>
                  {formatPrice(
                    data.budget_breakdown
                      ?.estimated_total_inr
                  )}
                </strong>

              </p>

              <p>

                <span>
                  Remaining:
                </span>

                <strong>
                  {formatPrice(
                    data.budget_breakdown
                      ?.remaining_budget_inr
                  )}
                </strong>

              </p>

            </div>

            <button
              className="primary-button"
              onClick={generateItinerary}
            >
              🤖 Generate My Itinerary
            </button>

          </div>

        </section>
      )}

      {/* COMPLETE */}

      {stage === "complete" &&
        data?.result && (

          <section className="section">

            <h2>
              🎉 Your Trip Is Ready!
            </h2>

            <div className="card">

              <h3>

                {safeText(
                  data.result.trip_summary
                    ?.origin
                )}

                {" → "}

                {safeText(
                  data.result.trip_summary
                    ?.destination
                )}

              </h3>

              <p>

                {safeText(
                  data.result.trip_summary
                    ?.days
                )}{" "}
                days •{" "}
                {safeText(
                  data.result.trip_summary
                    ?.travelers
                )}{" "}
                travelers

              </p>

              <p>

                Budget:{" "}

                {formatPrice(
                  data.result.trip_summary
                    ?.budget_inr
                )}

              </p>

            </div>

            {Array.isArray(
              data.result.itinerary
            ) &&
              data.result.itinerary.map(
                (day, index) => (

                  <div
                    className="card"
                    key={index}
                  >

                    <h2>
                      Day{" "}
                      {safeText(day.day)}:{" "}
                      {safeText(day.title)}
                    </h2>

                    <p>
                      🌅{" "}
                      <b>Morning:</b>{" "}
                      {safeText(
                        day.morning
                      )}
                    </p>

                    <p>
                      ☀️{" "}
                      <b>Afternoon:</b>{" "}
                      {safeText(
                        day.afternoon
                      )}
                    </p>

                    <p>
                      🌙{" "}
                      <b>Evening:</b>{" "}
                      {safeText(
                        day.evening
                      )}
                    </p>

                    <p>
                      🍳{" "}
                      <b>Breakfast:</b>{" "}
                      {safeText(
                        day.breakfast
                      )}
                    </p>

                    <p>
                      🍽️{" "}
                      <b>Lunch:</b>{" "}
                      {safeText(day.lunch)}
                    </p>

                    <p>
                      🍽️{" "}
                      <b>Dinner:</b>{" "}
                      {safeText(day.dinner)}
                    </p>

                  </div>

                )
              )}

          </section>
        )}

    </div>
  );
}

export default App;
