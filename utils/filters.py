def is_allowed_query(user_input):

    text = user_input.lower().strip()

    blocked = [
        "scholarship", "nsp", "ai", "machine learning",
        "coding", "programming", "politics", "bitcoin", "exam"
    ]

    if any(word in text for word in blocked):
        return False

    travel_keywords = [
        "trip", "travel", "tour", "itinerary",
        "destination", "places", "visit",
        "flight", "train", "bus", "budget",
        "weather", "hotel", "stay", "food"
    ]

    if any(word in text for word in travel_keywords):
        return True

    if len(text.split()) <= 3:
        return True

    return False
