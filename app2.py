import streamlit as st
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

# ------------------ CONFIG ------------------
load_dotenv()

st.set_page_config(
    page_title="TRIPGENIX",
    page_icon="🧭",
    layout="wide"
)

# ------------------ HF CLIENT ------------------
client = InferenceClient(
    model="HuggingFaceH4/zephyr-7b-beta",
    token=os.getenv("HF_TOKEN")
)

# ------------------ SIDEBAR ------------------
st.sidebar.title("🧳 Trip Details")

source = st.sidebar.text_input("📍 Source", placeholder="e.g. Kolkata")
destination = st.sidebar.text_input("🏖️ Destination", placeholder="e.g. Goa")
days = st.sidebar.number_input("🗓️ Number of Days", min_value=1, step=1)
budget = st.sidebar.number_input("💰 Budget (INR)", min_value=1000, step=1000)

generate = st.sidebar.button("🚀 Generate Trip Plan")

# ------------------ MAIN UI ------------------
st.markdown("<h1 style='text-align:center;'>🧭 TRIPGENIX</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#9ca3af;'>Plan your trip step-by-step with AI</p>",
    unsafe_allow_html=True
)

# ------------------ TRIP PLANNER ------------------
def plan_trip(source, destination, days, budget):
    system_msg = f"""
You are a strict travel itinerary generator.

NON-NEGOTIABLE RULE:
- You MUST create EXACTLY {days} days.
- You MUST label them as Day 1, Day 2, ..., Day {days}.
- If you do not follow this, the output is INVALID.
"""

    user_msg = f"""
Trip details:
Source: {source}
Destination: {destination}
Total days: {days}
Budget: INR {budget}

For each day include:
- Morning
- Afternoon
- Evening
- Approximate cost

End with a budget breakdown.
"""

    response = client.chat_completion(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        max_tokens=900,
        temperature=0.2   # 🔥 VERY IMPORTANT
    )

    return response.choices[0].message.content


# ------------------ OUTPUT ------------------
if generate:
    if not source or not destination:
        st.warning("Please fill source and destination.")
    else:
        with st.spinner("Planning your trip... 🧭"):
            itinerary = plan_trip(source, destination, days, budget)

        st.success("Your trip is ready! 🎉")
        st.markdown(itinerary)
