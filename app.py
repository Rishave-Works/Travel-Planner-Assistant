import streamlit as st
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

# ✅ Import functions from utils folder
from utils.weather import get_weather
from utils.distance import get_distance
from utils.transport import transport_options
from utils.filters import is_allowed_query
from utils.planner import plan_trip


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

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


# ------------------ HF CLIENT ------------------
client = InferenceClient(
    model="HuggingFaceH4/zephyr-7b-beta",
    token=os.getenv("HF_TOKEN")
)


# ------------------ SIDEBAR ------------------
st.sidebar.title("🧳 Trip Details (Date Mode)")

source = st.sidebar.text_input("📍 Source", placeholder="e.g. Kolkata")
destination = st.sidebar.text_input("🏖️ Destination", placeholder="e.g. Goa")

from_date = st.sidebar.date_input("📅 From Date")
to_date = st.sidebar.date_input("📅 To Date")

budget = st.sidebar.number_input("💰 Budget (INR)", min_value=1000, step=1000)

generate = st.sidebar.button("🚀 Generate Trip Plan")

if st.sidebar.button("🧹 Clear Trip History"):
    st.session_state.trip_history = []
    st.experimental_rerun()

if st.sidebar.button("🧽 Clear Chat"):
    st.session_state.chat_messages = []
    st.experimental_rerun()


# ------------------ DATE VALIDATION ------------------
if to_date < from_date:
    st.sidebar.error("❌ To Date must be after From Date")
    days = 1
else:
    days = (to_date - from_date).days + 1


# ------------------ MAIN UI ------------------
st.markdown("<h1 style='text-align:center;'>🧭 TRIPGENIX</h1>", unsafe_allow_html=True)

st.markdown(
    "<p style='text-align:center;color:gray;'>Travel + Weather + Places Assistant</p>",
    unsafe_allow_html=True
)


# ------------------ TRIP OUTPUT ------------------
if generate:

    if not source or not destination:
        st.warning("⚠️ Please fill source and destination.")

    elif to_date < from_date:
        st.error("❌ Fix date range first.")

    else:
        with st.spinner("Planning your trip..."):

            # ✅ Distance
            distance = get_distance(source, destination)

            if distance is None:
                st.error("❌ Invalid source/destination or geocoder timeout.")

            else:
                # ✅ Transport
                transport_info = transport_options(distance)

                # ✅ Weather
                weather_info = get_weather(destination)

                # ✅ AI Trip Plan
                itinerary = plan_trip(
                    client,
                    source,
                    destination,
                    days,
                    budget,
                    distance,
                    transport_info,
                    weather_info
                )

                # Save in history
                st.session_state.trip_history.append({
                    "source": source,
                    "destination": destination,
                    "itinerary": itinerary
                })


# ------------------ SHOW HISTORY ------------------
if st.session_state.trip_history:

    st.success("Your Trip History ✨")

    for i, trip in enumerate(reversed(st.session_state.trip_history), 1):
        with st.expander(f"🧳 Trip {i}: {trip['source']} ➜ {trip['destination']}"):
            st.markdown(trip["itinerary"])


# ------------------ CHAT SECTION ------------------
st.markdown("## 💬 Chat with TripGenix")

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


user_input = st.chat_input("Ask about places, hotels, food, travel...")

if user_input:

    st.session_state.chat_messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            if not is_allowed_query(user_input):
                reply = "🚫 Sorry! Main sirf travel + weather + places related questions answer karta hoon 🧭"

            else:
                response = client.chat_completion(
                    messages=[
                        {"role": "system",
                         "content": "You are TripGenix. Answer ONLY travel, hotels, food, places queries."},
                        *st.session_state.chat_messages
                    ],
                    max_tokens=600,
                    temperature=0.4
                )

                reply = response.choices[0].message.content

            st.markdown(reply)

    st.session_state.chat_messages.append(
        {"role": "assistant", "content": reply}
    )
