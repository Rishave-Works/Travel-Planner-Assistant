from geopy.geocoders import Nominatim
from geopy.distance import geodesic

def get_distance(source, destination):
    try:
        geolocator = Nominatim(user_agent="tripgenix")

        loc1 = geolocator.geocode(source, timeout=5)
        loc2 = geolocator.geocode(destination, timeout=5)

        if not loc1 or not loc2:
            return None

        return int(
            geodesic(
                (loc1.latitude, loc1.longitude),
                (loc2.latitude, loc2.longitude)
            ).km
        )

    except:
        return None
