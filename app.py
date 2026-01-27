import streamlit as st
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
import json

# ------------------ CONFIG ------------------
load_dotenv()

st.set_page_config(
    page_title="TRIPGENIX",
    page_icon="🧭",
    layout="centered"
)

# ------------------ CSS ------------------
st.markdown("""
<style>
body { background-color: #0e1117; color: white; }

.chat-container {
    max-width: 900px;
    margin: auto;
}

.user-bubble {
    background: #ff4b4b;
    padding: 12px 16px;
    border-radius: 14px;
    margin: 10px 0;
    color: white;
    width: fit-content;
    max-width: 80%;
}

.bot-bubble {
    background: #1f2933;
    padding: 12px 16px;
    border-radius: 14px;
    margin: 10px 0;
    color: white;
    width: fit-content;
    max-width: 80%;
}

.small-text {
    color: #9ca3af;
    font-size: 14px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown("""
<h1 style='text-align:center;'>🧭 TRIPGENIX</h1>
<p class='small-text'>Chat with AI to plan trips within your budget</p>
""", unsafe_allow_html=True)

# ------------------ HF CLIENT ------------------
client = InferenceClient(
    model="HuggingFaceH4/zephyr-7b-beta",
    token=os.getenv("HF_TOKEN")
)

# ------------------ SESSION STATE ------------------
defaults = {
    "chat_history": [],
    "destination": None,
    "days": None,
    "budget": None,
    "trip_completed": False
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------------ FUNCTIONS ------------------
def extract_trip_details(user_text):
    prompt = f"""
Extract travel details from the text below.
Return ONLY raw JSON. No explanation.

Keys:
destination, days, budget

If missing, use null.

Text:
{user_text}
"""
    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )

    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "")

    try:
        return json.loads(text)
    except:
        return {"destination": None, "days": None, "budget": None}


def plan_trip(destination, days, budget):
    prompt = f"""
You are a professional travel planner.

Create a detailed {days}-day itinerary for {destination}
within a total budget of INR {budget}.

Rules:
- Stay within budget
- Day-wise itinerary
- Morning / Afternoon / Evening plan
- Food, stay and local transport
- Approximate costs
- Clear budget breakdown

Use bullet points and headings.
"""
    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content

# ------------------ RESET BUTTON ------------------
if st.button("Reset"):
    for k in defaults:
        st.session_state[k] = defaults[k]
    st.experimental_rerun()

# ------------------ CHAT DISPLAY ------------------
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ------------------ INPUT ------------------
user_input = st.text_input("", placeholder="e.g. Trip to Goa for 3 days under 10000")

if st.button("Send") and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # ----- Handle post-trip yes/no -----
    # ----- Handle post-trip yes/no -----
if st.session_state.trip_completed:
    if user_input.lower() in ["yes", "haan", "y"]:
        st.session_state.destination = None
        st.session_state.days = None
        st.session_state.budget = None
        st.session_state.trip_completed = False

        reply = "Great 👍 Let’s plan a new trip. Where do you want to go?"
        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )
        st.experimental_rerun()

    elif user_input.lower() in ["no", "nah", "n"]:
        reply = "Alright 😊 Jab bhi trip ka mood bane, just message me."
        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )
        st.experimental_rerun()

    else:
        reply = "Please reply with yes or no 🙂"
        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )
        st.experimental_rerun()

# 🚫 IMPORTANT: return here
# so extraction does NOT happen


    # ----- Normal flow -----
    data = extract_trip_details(user_input)

    if data.get("destination"):
        st.session_state.destination = data["destination"]
    if data.get("days"):
        st.session_state.days = data["days"]
    if data.get("budget"):
        st.session_state.budget = data["budget"]

    if not st.session_state.destination:
        reply = "Please mention destination."
    elif not st.session_state.days:
        reply = "Please mention number of days."
    elif not st.session_state.budget:
        reply = "Please mention budget."
    else:
        itinerary = plan_trip(
            st.session_state.destination,
            st.session_state.days,
            st.session_state.budget
        )
        reply = itinerary + "\n\n🧭 Do you want to plan another trip? (yes / no)"
        st.session_state.trip_completed = True

    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    st.experimental_rerun()
