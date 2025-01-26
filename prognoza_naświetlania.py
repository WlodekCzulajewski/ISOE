import requests
from datetime import datetime, timedelta, timezone
import json

SC_ENDPOINT = "https://api.solcast.com.au/weather_sites/6d9d-f244-cea5-69a4/forecasts?format=json"
API_KEY = "TR46pAMIR5dRIazybBliJSdEWmAESYG2"

header = {"Authorization": f"Bearer {API_KEY}"}
response = requests.get(url= SC_ENDPOINT, headers=header)
response.raise_for_status()

# Convert raw data to JSON.
data = response.json()

# Get the current time in UTC and set the end time to 24 hours later
current_time = datetime.now(timezone.utc)
end_time = current_time + timedelta(hours=24)

# Filter data to include only the next 24 hours and hourly measurements
filtered_data = []
for forecast in data['forecasts']:
    forecast_time = datetime.fromisoformat(forecast['period_end'].replace('Z', '+00:00'))
    if current_time <= forecast_time <= end_time and forecast_time.minute == 0:
        filtered_data.append(forecast)

# Save filtered data to a JSON file
with open('dane_biezace/prognoza_naslonecznienia.json', 'w') as file:
    json.dump(filtered_data, file, indent=4)

# Process or print filtered data
print(filtered_data)


