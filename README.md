# Nuclear Event Alert System

![fine_cyber_punk](https://github.com/user-attachments/assets/5b89f765-4410-4983-bf56-bcde2cf73a40)

## Overview

The Nuclear Event Alert System is a monitoring tool designed to detect seismic activity and radiation levels in real-time. Combines data from the USGS ([United States Geological Survey](https://earthquake.usgs.gov)) and [Safecast APIs](https://api.safecast.org/en-US/measurements) to identify potential nuclear events and post alerts. 

> [!TIP]
> Monitor [Closetemail's](https://bsky.app/profile/closetemail.com) BlueSky Account for alerts if that is what you are interseted in - as that is what I will be using it for.

## Features

- **Seismic Monitoring**: Tracks recent seismic events and evaluates their magnitude and depth.
- **Radiation Detection**: Retrieves nearby radiation measurements to detect potential spikes.
- **Automated Alerts**: Posts detailed alerts to Bluesky when thresholds for seismic and radiation levels are exceeded.
- **Simulation Mode**: Allows users to simulate events for testing purposes.

## Why It’s Useful

This tool provides an early warning system for potential nuclear detonations or radiation leaks. By integrating seismic and radiation data, it helps raise awareness and improve response times for such critical events. The Bluesky integration ensures that alerts are shared quickly with a broader audience, making it valuable for public safety and disaster preparedness.

## How to Use

1. **Real-Time Monitoring**:
   - Set up the tool in your environment or on a CI/CD platform like GitHub Actions.
   - The tool will automatically monitor seismic and radiation data and post alerts if thresholds are exceeded.

2. **Simulation Mode**:
   - Trigger the workflow manually with simulated latitude, longitude, and radiation values to test the system.

## Requirements

- Python 3.x
- APIs: USGS, Safecast
- A Bluesky account for posting alerts

## License

This project is open-source and available for public use under the [MIT License](LICENSE).
