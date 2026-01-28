def plan_trip(client, source, destination, days, budget,
              distance, transport_info, weather_info):

    system_msg = f"""
You are TripGenix, a strict Travel Assistant.

RULES:
- Answer ONLY travel, hotels, food, places queries
- Create EXACTLY {days} days itinerary
- Weather is expected current weather (not future guarantee)
- Use price ranges only
"""

    user_msg = f"""
Trip Details:
Source: {source}
Destination: {destination}
Distance: Approx {distance} km
Budget: INR {budget}

Expected Weather in {destination}:
{weather_info}

Transport Options:
{transport_info}

Output Format:
1. Distance
2. Transport options
3. Best transport
4. Weather (once only)
5. Day-wise itinerary (Day 1 to Day {days})
6. Emergency numbers
7. Do’s and Don’ts
"""

    response = client.chat_completion(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        max_tokens=1400,
        temperature=0.3
    )

    return response.choices[0].message.content
