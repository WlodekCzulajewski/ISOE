import json
import pandas as pd
import math


# Funkcja do obliczenia produkcji energii na podstawie GHI
def oblicz_generacje_energii(ghi, temperatura, kat_nachylenia, azymut, sprawnosc, powierzchnia, straty_systemowe, wspolczynnik_cienia):
    """
    Funkcja do obliczenia produkcji energii elektrycznej na podstawie GHI.

    Parameters:
    ghi: float - Globalne promieniowanie słoneczne (kWh/m²)
    temperatura: float - Temperatura powietrza (°C)
    kat_nachylenia: float - Kąt nachylenia paneli (°)
    azymut: float - Azymut paneli względem południa (°)
    sprawnosc: float - Sprawność paneli fotowoltaicznych (0-1)
    powierzchnia: float - Całkowita powierzchnia instalacji (m²)
    straty_systemowe: float - Straty systemowe (0-1)
    wspolczynnik_cienia: float - Redukcja efektywności z powodu cienia (0-1)

    Returns:
    float - Szacowana ilość wyprodukowanej energii (kWh)
    """
    # Korekta kąta nachylenia i azymutu na wydajność w stosunku do GHI
    wspolczynnik_orientacji = math.cos(math.radians(kat_nachylenia)) * math.cos(math.radians(azymut - 180))

    # Efektywne promieniowanie na całą powierzchnię instalacji
    efektywne_promieniowanie = ghi * powierzchnia * wspolczynnik_orientacji

    # Korekta strat systemowych, sprawności i wpływu cienia
    efektywna_moc = efektywne_promieniowanie * sprawnosc * (1 - straty_systemowe) * wspolczynnik_cienia

    return max(efektywna_moc, 0)  # Moc nie może być ujemna


# Parametry paneli fotowoltaicznych
moc_pojedynczego_panelu = 320  # W
liczba_paneli = 18
szerokosc_panelu = 0.992  # m
dlugosc_panelu = 1.668  # m

# Całkowita moc instalacji
moc_nominalna = (moc_pojedynczego_panelu * liczba_paneli) / 1000  # kW
print(f"Całkowita moc instalacji: {moc_nominalna:.2f} kW")

# Całkowite pole instalacji
pole_instalacji = liczba_paneli * szerokosc_panelu * dlugosc_panelu  # m²
print(f"Całkowite pole instalacji: {pole_instalacji:.2f} m²")

# Parametry instalacji fotowoltaicznej
kat_nachylenia = 26  # stopnie
azymut = 180  # stopnie
sprawnosc = 0.1934  # 19.34% sprawności
straty_systemowe = 0.14  # 14% strat dla instalacji 4-letniej

# Załaduj dane horyzontu
with open('dane_historyczne/horyzont_2024.json', 'r') as f:
    dane_horyzontu = json.load(f)

# Dane o cieniu na podstawie horyzontu
def uwzglednij_cien(czas):
    """
    Uwzględnia cień spadający na panele do godziny 10:30.

    Parameters:
    czas: datetime - Czas do sprawdzenia

    Returns:
    float - Współczynnik redukcji efektywności (0-1)
    """
    godzina = czas.hour + czas.minute / 60  # Przekształcenie na godzinę dziesiętną
    if godzina <= 9:  # Cień przed 10:30
        return 0.5  # Redukcja o 50%
    elif godzina <= 11:  # Cień przed 10:30
        return 0.6  # Redukcja o 50%
    elif godzina <= 12:  # Cień przed 10:30
        return 0.4  # Redukcja o 50%
    return 1.0  # Brak redukcji


# Załaduj dane historyczne GHI i temperatury z pliku JSON
with open('dane_historyczne/stan_naslonecznienia_2024.json', 'r') as f:
    dane_naslonecznienia = json.load(f)

# Załaduj dane historyczne generacji prądu z pliku CSV
dane_generacji = pd.read_csv('dane_historyczne/generacja_pradu_2024.csv')

dane_generacji['Data'] = pd.to_datetime(dane_generacji['Data'], format='%A, %B %d, %Y')  # Konwersja na typ daty
dane_generacji.set_index('Data', inplace=True)  # Ustawienie daty jako indeksu

# Analiza danych
wyniki = []
dane_naslonecznienia = dane_naslonecznienia["estimated_actuals"]  # Dostosowanie do nowego formatu JSON

for wpis in dane_naslonecznienia:
    data_godzina = pd.to_datetime(wpis['period_end']).tz_convert(None)  # Data i godzina
    ghi = wpis['ghi'] / 1000  # Konwersja GHI z W/m² na kW/m²
    temperatura = wpis['air_temp']  # Temperatura w °C

    wspolczynnik_cienia = uwzglednij_cien(data_godzina)  # Uwzględnienie cienia

    energia = oblicz_generacje_energii(
        ghi=ghi,
        temperatura=temperatura,
        kat_nachylenia=kat_nachylenia,
        azymut=azymut,
        sprawnosc=sprawnosc,
        powierzchnia=pole_instalacji,  # Całkowite pole instalacji
        straty_systemowe=straty_systemowe,
        wspolczynnik_cienia=wspolczynnik_cienia
    )

    # Dodanie lub aktualizacja danych dla danej daty
    if wyniki and wyniki[-1]['Data'] == data_godzina.floor('D'):
        wyniki[-1]['Symulowana generacja (kWh)'] += energia
    else:
        wyniki.append({
            'Data': data_godzina.floor('D'),
            'Symulowana generacja (kWh)': energia,
            'Rzeczywista generacja (kWh)': 0  # Placeholder, uzupełnimy później
        })

# Uzupełnienie rzeczywistych danych generacji z CSV
for wynik in wyniki:
    data = wynik['Data']
    if data in dane_generacji.index:
        wynik['Rzeczywista generacja (kWh)'] = dane_generacji.loc[data, 'Generacja prądu kWh']
        wynik['Różnica (kWh)'] = wynik['Rzeczywista generacja (kWh)'] - wynik['Symulowana generacja (kWh)']
    else:
        wynik['Różnica (kWh)'] = None

# Tworzenie DataFrame z wynikami
wyniki_df = pd.DataFrame(wyniki)

# Obliczanie średniego odchylenia prognozy od rzeczywistych danych dla miesięcy 5-12
wyniki_df['Miesiąc'] = wyniki_df['Data'].dt.month
wyniki_maj_grudzien = wyniki_df[(wyniki_df['Miesiąc'] >= 5) & (wyniki_df['Miesiąc'] <= 12)]
srednie_odchylenie = wyniki_maj_grudzien['Różnica (kWh)'].abs().mean()
print(f"Średnie odchylenie prognozy dla miesięcy 5-12: {srednie_odchylenie:.2f} kWh")

# Zapis wyników do pliku CSV
wyniki_df.to_csv('dane_historyczne/wyniki_porownania_generacji.csv', index=False)

print("Analiza zakończona. Wyniki zapisano w 'wyniki_porownania_generacji.csv'.")
