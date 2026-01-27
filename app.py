import streamlit as st
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# ------------------ CONFIG ------------------
load_dotenv()

st.set_page_config(
    page_title="TRIPGENIX",
    page_icon="🧭",
    layout="wide"
)

# ------------------ SESSION STATE ------------------
if "trip_history" not in st.session_state:
    st.session_state.trip_history = []

# ------------------ HF CLIENT ------------------
client = InferenceClient(
    model="HuggingFaceH4/zephyr-7b-beta",
    token=os.getenv("HF_TOKEN")
)

# ------------------ HELPER FUNCTIONS ------------------
def get_distance(source, destination):
    geolocator = Nominatim(user_agent="tripgenix")
    loc1 = geolocator.geocode(source)
    loc2 = geolocator.geocode(destination)

    if not loc1 or not loc2:
        return None

    return int(
        geodesic(
            (loc1.latitude, loc1.longitude),
            (loc2.latitude, loc2.longitude)
        ).km
    )


def transport_options(distance):
    if distance < 300:
        return """
- Bus: ₹500 – ₹1,200
- Train (Sleeper/AC): ₹600 – ₹1,500
"""
    elif distance < 1000:
        return """
- Train (AC/Sleeper): ₹1,200 – ₹2,500
- Flight: ₹3,500 – ₹6,000
"""
    else:
        return """
- Train (AC): ₹2,000 – ₹4,000
- Flight: ₹4,500 – ₹8,000
"""

# ------------------ SIDEBAR ------------------
st.sidebar.title("🧳 Trip Details")

source = st.sidebar.text_input("📍 Source", placeholder="e.g. Kolkata")
destination = st.sidebar.text_input("🏖️ Destination", placeholder="e.g. Goa")
days = st.sidebar.number_input("🗓️ Number of Days", min_value=1, step=1)
budget = st.sidebar.number_input("💰 Budget (INR)", min_value=1000, step=1000)

generate = st.sidebar.button("🚀 Generate Trip Plan")

if st.sidebar.button("🧹 Clear Trip History"):
    st.session_state.trip_history = []
    st.experimental_rerun()

# ------------------ MAIN UI ------------------
st.markdown("<h1 style='text-align:center;'>🧭 TRIPGENIX</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#9ca3af;'>Plan your trip step-by-step with AI</p>",
    unsafe_allow_html=True
)

# ------------------ TRIP PLANNER ------------------
def plan_trip(source, destination, days, budget, distance, transport_info):

    system_msg = f"""
You are TripGenix, a professional travel planning assistant.

STRICT RULES (NO EXCEPTIONS):
- Create EXACTLY {days} days itinerary (Day 1 to Day {days})
- Weather must be described ONCE only
- Weather must NOT be split day-wise
- Do NOT mention seasons changing during the trip
- Use general climate description only
- Do NOT hallucinate exact prices
- Use price ranges only
- Do NOT mention specific train or flight names
"""

    user_msg = f"""
Trip Details:
Source: {source}
Destination: {destination}
Distance: Approx {distance} km
Budget: INR {budget}
Total Days: {days}

AVAILABLE TRANSPORT OPTIONS:
{transport_info}

OUTPUT FORMAT:

1. Distance Between Source and Destination
2. Available Modes of Transport (with price range)
3. Best Mode of Transport (with reason)
4. Destination Weather & Travel Suitability
5. Day-wise Itinerary (Day 1 to Day {days})
   - Morning
   - Afternoon
   - Evening
   - Nearby food options
   - Estimated daily cost
6. Emergency Numbers (India)
7. Do’s and Don’ts
"""

    response = client.chat_completion(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        max_tokens=1200,
        temperature=0.2
    )

    return response.choices[0].message.content

# ------------------ OUTPUT ------------------
if generate:
    if not source or not destination:
        st.warning("Please fill source and destination.")
    else:
        with st.spinner("Calculating distance & planning trip... 🧭"):
            distance = get_distance(source, destination)

            if distance is None:
                st.error("Invalid source or destination.")
            else:
                transport_info = transport_options(distance)

                itinerary = plan_trip(
                    source,
                    destination,
                    days,
                    budget,
                    distance,
                    transport_info
                )

                # SAVE TO HISTORY
                st.session_state.trip_history.append({
                    "source": source,
                    "destination": destination,
                    "itinerary": itinerary
                })

# ------------------ SHOW HISTORY ------------------
if st.session_state.trip_history:
    st.success("Your trip history ✨")

    for i, trip in enumerate(reversed(st.session_state.trip_history), 1):
        with st.expander(
            f"🧳 Trip {i}: {trip['source']} ➜ {trip['destination']}"
        ):
            st.markdown(trip["itinerary"])
