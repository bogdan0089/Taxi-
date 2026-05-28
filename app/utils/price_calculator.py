from math import radians, sin, cos, sqrt, atan2


def price_calculate(pickup_lat: float, pickup_lon: float, dropoff_lat: float, dropoff_lon: float) -> float:

    R = 6371

    lat1, lon1 = radians(pickup_lat), radians(pickup_lon)
    lat2, lon2 = radians(dropoff_lat), radians(dropoff_lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    distance = 2 * R * atan2(sqrt(a), sqrt(1-a))

    return round(distance * 1.5, 2)


