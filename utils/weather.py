import os
import requests

def get_weather(city):
    api_key = os.getenv("WEATHER_API_KEY")

    if not api_key:
        return "❌ WEATHER_API_KEY missing in .env"

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:
        res = requests.get(url, params=params).json()

        if res.get("cod") != 200:
            return "⚠️ Weather not available"

        desc = res["weather"][0]["description"].title()
        temp = res["main"]["temp"]
        humidity = res["main"]["humidity"]

        return f"🌤️ {desc}, 🌡️ {temp}°C, 💧 Humidity: {humidity}%"

    except:
        return "⚠️ Weather API failed"
