import json
import pandas as pd
import math

# Funkcja do obliczenia produkcji energii na podstawie GHI
# Uwzględnia azymut, kąt nachylenia, straty systemowe, sprawność i moc nominalną

def oblicz_generacje_energii(ghi, temperatura, kat_nachylenia, azymut, sprawnosc, moc_nominalna, straty_systemowe):
    # Korekta kąta nachylenia i azymutu na wydajność w stosunku do GHI
    wspolczynnik_orientacji = math.cos(math.radians(kat_nachylenia)) * math.cos(math.radians(azymut - 180))

    # Efektywne promieniowanie na panel
    efektywne_promieniowanie = ghi * wspolczynnik_orientacji

    # Korekta strat systemowych i sprawności
    efektywna_moc = efektywne_promieniowanie * sprawnosc * moc_nominalna * (1 - straty_systemowe)

    return max(efektywna_moc, 0)  # Moc nie może być ujemna

# Załaduj dane GHI i temperatury z pliku JSON
with open('dane/stan_naslonecznienia_2024.json', 'r') as f:
    dane_naslonecznienia = json.load(f)

# Załaduj dane generacji prądu z pliku CSV
dane_generacji = pd.read_csv('dane/generacja_pradu_2024.csv')

dane_generacji['Data'] = pd.to_datetime(dane_generacji['Data'], format='%A, %B %d, %Y')  # Konwersja na typ daty
dane_generacji.set_index('Data', inplace=True)  # Ustawienie daty jako indeksu

# Parametry instalacji fotowoltaicznej
kat_nachylenia = 26  # stopnie
azymut = 180  # stopnie
sprawnosc = 0.76  # sprawność paneli (14%)
moc_nominalna = 5.76  # kWp
straty_systemowe = 0.15  # 15% strat

# Analiza danych
wyniki = []
dane_naslonecznienia = dane_naslonecznienia["estimated_actuals"]  # Dostosowanie do nowego formatu JSON

for wpis in dane_naslonecznienia:
    data_godzina = pd.to_datetime(wpis['period_end']).tz_convert(None).floor('D')  # Tylko data, bez godziny
    ghi = wpis['ghi'] / 1000  # Konwersja GHI z W/m² na kWh/m²
    temperatura = wpis['air_temp']  # Temperatura w °C
    energia = oblicz_generacje_energii(
        ghi=ghi,
        temperatura=temperatura,
        kat_nachylenia=kat_nachylenia,
        azymut=azymut,
        sprawnosc=sprawnosc,
        moc_nominalna=moc_nominalna,
        straty_systemowe=straty_systemowe
    )

    # Dodanie lub aktualizacja danych dla danej daty
    if wyniki and wyniki[-1]['Data'] == data_godzina:
        wyniki[-1]['Symulowana generacja (kWh)'] += energia
    else:
        wyniki.append({
            'Data': data_godzina,
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
wyniki_df.to_csv('dane/wyniki_porownania_generacji.csv', index=False)

print("Analiza zakończona. Wyniki zapisano w 'wyniki_porownania_generacji.csv'.")
