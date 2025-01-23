import requests


# SC_ENDPOINT = "https://api.solcast.com.au/data/forecast/rooftop_pv_power"
# API_KEY = "TR46pAMIR5dRIazybBliJSdEWmAESYG2"
# COORDINATES = (52.10223732321454, 20.799135457477743)
#
# header = {"Authorization": f"Bearer {API_KEY}"}
# parameters = {
# 	"latitude": COORDINATES[0],
# 	"longitude": COORDINATES[1],
# 	"hours": 24,
# 	"period": "PT60M",
# 	"capacity": 1,
# 	"tilt": 26,
# 	"format": "json",
# 	"api_key": API_KEY
# }
#
# response = requests.get(url=SC_ENDPOINT, params=parameters)
# response.raise_for_status()
#
# # Convert raw data to JSON.
# data = response.json()
# print(data)

response = requests.get(url="https://api.solcast.com.au/weather_sites/6d9d-f244-cea5-69a4/forecasts?format=json")
response.raise_for_status()

# Convert raw data to JSON.
data = response.json()
print(data)