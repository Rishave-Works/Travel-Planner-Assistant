def get_distance(source, destination):
    try:
        geolocator = Nominatim(user_agent="tripgenix_app_rishav")

        loc1 = geolocator.geocode(source, timeout=10)
        loc2 = geolocator.geocode(destination, timeout=10)

        if not loc1:
            return "SOURCE_NOT_FOUND"
        if not loc2:
            return "DESTINATION_NOT_FOUND"

        return int(geodesic(
            (loc1.latitude, loc1.longitude),
            (loc2.latitude, loc2.longitude)
        ).km)

    except Exception as e:
        return str(e)
