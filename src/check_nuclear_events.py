import requests
import datetime
import argparse

# Constants
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
SAFECAST_URL = "https://api.safecast.org/measurements"
MAG_THRESHOLD = 4.0  # Minimum magnitude
DEPTH_THRESHOLD = 10.0  # Maximum depth (in km)
RADIATION_SPIKE_THRESHOLD = 2.0  # Example threshold for radiation increase

def get_usgs_events():
    now = datetime.datetime.now(datetime.UTC)
    past = now - datetime.timedelta(minutes=30)  # Expand to the last 30 minutes
    params = {
        "format": "geojson",
        "starttime": past.isoformat(),
        "endtime": now.isoformat(),
        "minmagnitude": 0  # Fetch all events regardless of magnitude
    }
    print(f"[INFO] Fetching USGS events from {past} to {now}...")
    response = requests.get(USGS_URL, params=params)
    if response.status_code == 200:
        events = response.json().get("features", [])
        if events:
            return events
        else:
            print("[INFO] No seismic events detected.")
            return []
    else:
        print(f"[ERROR] Failed to fetch USGS data: {response.status_code}")
        return []

def check_safecast_radiation(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "distance": 10  # Check within 10 km
    }
    print(f"[INFO] Checking Safecast radiation levels near ({lat}, {lon})...")
    response = requests.get(SAFECAST_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data and data["measurements"]:
            for measurement in data["measurements"]:
                radiation_level = float(measurement["value"])
                print(f"[INFO] Radiation level detected: {radiation_level} μSv/h")
                if radiation_level > RADIATION_SPIKE_THRESHOLD:
                    return True
        else:
            print("[INFO] No radiation measurements found.")
    else:
        print(f"[ERROR] Failed to fetch Safecast data: {response.status_code}")
    return False

def main(simulate_lat=None, simulate_lon=None, simulate_radiation=None):
    # Check for simulation mode
    if simulate_lat and simulate_lon and simulate_radiation:
        print(f"[SIMULATION] Simulating event at ({simulate_lat}, {simulate_lon}) with radiation {simulate_radiation} μSv/h.")
        if float(simulate_radiation) > RADIATION_SPIKE_THRESHOLD:
            print(f"[ALERT] Simulated radiation exceeds threshold! Possible detonation detected at ({simulate_lat}, {simulate_lon}).")
        else:
            print("[INFO] Simulated radiation does not exceed threshold.")
        return

    # Fetch seismic events
    events = get_usgs_events()
    if not events:
        print("[INFO] No seismic events detected.")
        return

    # Report the most recent event
    latest_event = events[0]
    props = latest_event["properties"]
    geo = latest_event["geometry"]["coordinates"]
    magnitude = props.get("mag", "Unknown")
    depth = geo[2] if len(geo) > 2 else "Unknown"
    lat, lon = geo[1], geo[0]
    event_time = datetime.datetime.fromtimestamp(props["time"] / 1000).strftime("%Y-%m-%d %H:%M:%S UTC") if "time" in props else "Unknown"

    print(f"[INFO] Most recent seismic event:")
    print(f"  - Magnitude: {magnitude}")
    print(f"  - Depth: {depth} km")
    print(f"  - Location: ({lat}, {lon})")
    print(f"  - Time: {event_time}")

    # Check if the latest event meets alert conditions
    if isinstance(magnitude, (int, float)) and magnitude >= MAG_THRESHOLD and depth != "Unknown" and depth <= DEPTH_THRESHOLD:
        if check_safecast_radiation(lat, lon):
            print(f"[ALERT] Possible detonation detected at ({lat}, {lon})!")
            return

    print("[INFO] No significant events detected.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor seismic and radiation events.")
    parser.add_argument("--simulate-lat", type=str, help="Latitude for simulated event", default=None)
    parser.add_argument("--simulate-lon", type=str, help="Longitude for simulated event", default=None)
    parser.add_argument("--simulate-radiation", type=str, help="Simulated radiation level", default=None)
    args = parser.parse_args()

    main(simulate_lat=args.simulate_lat, simulate_lon=args.simulate_lon, simulate_radiation=args.simulate_radiation)
