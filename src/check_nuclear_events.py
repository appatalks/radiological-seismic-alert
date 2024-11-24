import requests
import datetime
import argparse

# Constants
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
SAFECAST_URL = "https://api.safecast.org/measurements.json"
MAG_THRESHOLD = 2.0  # Minimum magnitude
DEPTH_THRESHOLD = 10.0  # Maximum depth (in km)
RADIATION_SPIKE_THRESHOLD_CPM = 125  # Example threshold for radiation in CPM
REQUEST_TIMEOUT = 15  # Timeout for API requests in seconds

def get_usgs_events():
    now = datetime.datetime.now(datetime.UTC)
    past = now - datetime.timedelta(minutes=10)  # Expand to the last 10 minutes
    params = {
        "format": "geojson",
        "starttime": past.isoformat(),
        "endtime": now.isoformat(),
        "minmagnitude": 0  # Fetch all events regardless of magnitude
    }
    print(f"[INFO] Fetching USGS events from {past} to {now}...")
    try:
        response = requests.get(USGS_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        events = response.json().get("features", [])
        if events:
            return events
        else:
            print("[INFO] No seismic events detected.")
            return []
    except requests.exceptions.Timeout:
        print("[WARNING] Timeout occurred while fetching USGS data.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch USGS data: {e}")
        return []

def get_nearest_radiation_sample(lat, lon):
    params = {
        "distance": 20,  # Distance in kilometers
        "latitude": lat,
        "longitude": lon
    }
    try:
        print(f"[INFO] Fetching nearest radiation sample near ({lat}, {lon}) with a distance of {params['distance']} km...")
        response = requests.get(SAFECAST_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        # Debug: Log the raw response content
        print(f"[DEBUG] Raw Safecast API Response: {response.text}")

        # Parse JSON data
        data = response.json()
        if data and "measurements" in data and data["measurements"]:
            nearest_sample = min(data["measurements"], key=lambda x: x.get("value", float('inf')))
            radiation_value = float(nearest_sample["value"])
            unit = nearest_sample.get("unit", "unknown")
            timestamp = nearest_sample["captured_at"]

            print(f"[INFO] Nearest radiation sample: {radiation_value:.2f} {unit} at {timestamp}")
            return radiation_value, unit, timestamp
        else:
            print("[INFO] No radiation samples found in the specified area.")
            return None, None, None
    except requests.exceptions.JSONDecodeError:
        print("[ERROR] Invalid JSON response from Safecast API.")
        print(f"[DEBUG] Raw Response Content: {response.content.decode('utf-8', errors='ignore')}")
        return None, None, None
    except requests.exceptions.Timeout:
        print("[WARNING] Timeout occurred while fetching Safecast data.")
        return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] An error occurred: {e}")
        return None, None, None

def main(simulate_lat=None, simulate_lon=None, simulate_radiation=None):
    if simulate_lat and simulate_lon and simulate_radiation:
        print(f"[SIMULATION] Simulating event at ({simulate_lat}, {simulate_lon}) with radiation {simulate_radiation} CPM.")
        if float(simulate_radiation) > RADIATION_SPIKE_THRESHOLD_CPM:
            print(f"[ALERT] Simulated radiation exceeds threshold! Possible detonation detected at ({simulate_lat}, {simulate_lon}).")
        else:
            print("[INFO] Simulated radiation does not exceed threshold.")
        return

    events = get_usgs_events()
    if not events:
        print("[INFO] No seismic events detected.")
        return

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

    radiation_level, radiation_unit, radiation_time = get_nearest_radiation_sample(lat, lon)
    if radiation_level is not None:
        print(f"[INFO] Nearest radiation sample:")
        print(f"  - Radiation Level: {radiation_level:.2f} {radiation_unit}")
        print(f"  - Time: {radiation_time}")
    else:
        print("[INFO] No radiation samples available for this location.")

    if isinstance(magnitude, (int, float)) and magnitude >= MAG_THRESHOLD and depth != "Unknown" and depth <= DEPTH_THRESHOLD:
        if radiation_level is not None and radiation_level > RADIATION_SPIKE_THRESHOLD_CPM:
            print(f"[ALERT] Possible detonation detected at ({lat}, {lon})!")
            print(f"[DETAILS] Detected radiation level: {radiation_level:.2f} {radiation_unit}")
            print(f"[DETAILS] Radiation sample captured at: {radiation_time}")
            return        

    print("[INFO] No significant events detected.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor seismic and radiation events.")
    parser.add_argument("--simulate-lat", type=str, help="Latitude for simulated event", default=None)
    parser.add_argument("--simulate-lon", type=str, help="Longitude for simulated event", default=None)
    parser.add_argument("--simulate-radiation", type=str, help="Simulated radiation level", default=None)
    args = parser.parse_args()

    main(simulate_lat=args.simulate_lat, simulate_lon=args.simulate_lon, simulate_radiation=args.simulate_radiation)
