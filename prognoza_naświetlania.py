import requests
from datetime import datetime, timedelta, timezone
import json

def pobierz_prognoze():
    """
    Pobiera prognozę nasłonecznienia i dopisuje dane do istniejącego pliku JSON.

    :return: Lista prognozowanych danych nasłonecznienia na kolejne 24 godziny.
    """
    SC_ENDPOINT = "https://api.solcast.com.au/weather_sites/6d9d-f244-cea5-69a4/forecasts?format=json"
    API_KEY = "TR46pAMIR5dRIazybBliJSdEWmAESYG2"

    header = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(url=SC_ENDPOINT, headers=header)
    response.raise_for_status()

    # Konwersja surowych danych na format JSON
    data = response.json()

    # Pobranie aktualnego czasu w UTC i ustawienie końca na 24 godziny później
    current_time = datetime.now(timezone.utc)
    end_time = current_time + timedelta(hours=24)

    # Filtrowanie danych, aby uwzględnić tylko kolejne 24 godziny i pomiary co godzinę
    filtered_data = []
    for forecast in data['forecasts']:
        forecast_time = datetime.fromisoformat(forecast['period_end'].replace('Z', '+00:00'))
        if current_time <= forecast_time <= end_time and forecast_time.minute == 0:
            filtered_data.append(forecast)

    # Zachowanie tylko danych w odstępach godzinnych
    hourly_data = []
    last_hour = None
    for entry in filtered_data:
        entry_hour = datetime.fromisoformat(entry['period_end'].replace('Z', '+00:00')).hour
        if entry_hour != last_hour:
            hourly_data.append(entry)
            last_hour = entry_hour

    # Dopisanie przefiltrowanych danych do istniejącego pliku JSON
    try:
        with open('dane_biezace/prognoza_naslonecznienia.json', 'r+') as file:
            existing_data = json.load(file)
            if isinstance(existing_data, list):
                existing_data.extend(hourly_data)
            else:
                existing_data = hourly_data

            # Przesunięcie wskaźnika pliku na początek w celu nadpisania
            file.seek(0)
            json.dump(existing_data, file, indent=4)
    except FileNotFoundError:
        # Utworzenie nowego pliku, jeśli nie istnieje
        with open('dane_biezace/prognoza_naslonecznienia.json', 'w') as file:
            json.dump(hourly_data, file, indent=4)

    return hourly_data
