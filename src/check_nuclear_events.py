import requests
import datetime

# Constants
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
SAFECAST_URL = "https://api.safecast.org/measurements"
MAG_THRESHOLD = 4.0  # Minimum magnitude
DEPTH_THRESHOLD = 10.0  # Maximum depth (in km)
RADIATION_SPIKE_THRESHOLD = 2.0  # Example threshold for radiation increase

def get_usgs_events():
    now = datetime.datetime.utcnow()
    past = now - datetime.timedelta(minutes=5)  # Last 5 minutes
    params = {
        "format": "geojson",
        "starttime": past.isoformat(),
        "endtime": now.isoformat(),
        "minmagnitude": MAG_THRESHOLD
    }
    response = requests.get(USGS_URL, params=params)
    return response.json().get("features", [])

def check_safecast_radiation(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "distance": 25  # Check within 25 km
    }
    response = requests.get(SAFECAST_URL, params=params)
    data = response.json()
    if data and data["measurements"]:
        # Compare current measurements with the threshold
        return any(float(m["value"]) > RADIATION_SPIKE_THRESHOLD for m in data["measurements"])
    return False

def main():
    events = get_usgs_events()
    for event in events:
        props = event["properties"]
        geo = event["geometry"]["coordinates"]
        magnitude = props.get("mag", 0)
        depth = geo[2]

        if magnitude >= MAG_THRESHOLD and depth <= DEPTH_THRESHOLD:
            # Check radiation levels
            lat, lon = geo[1], geo[0]
            if check_safecast_radiation(lat, lon):
                print(f"Alert! Possible detonation detected at {lat}, {lon}")
                return

    print("No significant events detected.")

if __name__ == "__main__":
    main()
