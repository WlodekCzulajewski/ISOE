import json
import pandas as pd
import math


# Funkcja do obliczenia produkcji energii na podstawie GHI z uwzględnieniem wpływu temperatury
def oblicz_generacje_energii(ghi, temperatura, kat_nachylenia, azymut, sprawnosc, powierzchnia, straty_systemowe,
                             wspolczynnik_cienia, pmax_temp_coeff):
    """
    Funkcja do obliczenia produkcji energii elektrycznej na podstawie GHI z uwzględnieniem temperatury.
    Parameters:
    ghi: float - Globalne promieniowanie słoneczne (kWh/m²)
    temperatura: float - Temperatura powietrza (°C)
    kat_nachylenia: float - Kąt nachylenia paneli (°)
    azymut: float - Azymut paneli względem południa (°)
    sprawnosc: float - Sprawność paneli fotowoltaicznych (0-1)
    powierzchnia: float - Całkowita powierzchnia instalacji (m²)
    straty_systemowe: float - Straty systemowe (0-1)
    wspolczynnik_cienia: float - Redukcja efektywności z powodu cienia (0-1)
    pmax_temp_coeff: float - Współczynnik temperaturowy Pmax (%/°C)

    Returns:
    float - Szacowana ilość wyprodukowanej energii (kWh)
    """

    temperatura_stc = 25.0  # °C Temperatura odniesienia paneli (standardowe warunki testowe - STC)
    korekta_temperaturowa = 1 + pmax_temp_coeff / 100 * (temperatura - temperatura_stc) # Korekta sprawności w zależności od temperatury
    sprawnosc_skorygowana = sprawnosc * korekta_temperaturowa # Skorygowane sprawność panelu
    wspolczynnik_orientacji = math.cos(math.radians(kat_nachylenia)) * math.cos(math.radians(azymut - 180)) # Ustal współczynnik orientacji
    efektywne_promieniowanie = ghi * powierzchnia * wspolczynnik_orientacji # Efektywne promieniowanie
    efektywna_moc = efektywne_promieniowanie * sprawnosc_skorygowana * (1 - straty_systemowe) * wspolczynnik_cienia # Uwzględnienie cienia i strat systemowych

    return max(efektywna_moc, 0)

# Wczytaj dane nasłonecznienia z pliku JSON
with open('dane_historyczne/stan_naslonecznienia_2024.json', 'r') as f:
    dane_naslonecznienia = json.load(f)

# Parametry paneli fotowoltaicznych
moc_pojedynczego_panelu = 320  # W
liczba_paneli = 18
szerokosc_panelu = 0.992  # m
dlugosc_panelu = 1.640  # m
moc_nominalna = (moc_pojedynczego_panelu * liczba_paneli) / 1000  # kW
pole_instalacji = liczba_paneli * szerokosc_panelu * dlugosc_panelu  # m²
wspolczynnik_pmax = -0.37

# Parametry instalacji fotowoltaicznej
kat_nachylenia = 26  # stopnie
azymut = 180  # stopnie
sprawnosc = 0.1955  # 19.55% sprawności
straty_systemowe = 0.10  # 10% przyjęte straty dla instalacji 4-letniej

# Parametry dla cienia
wysokosc_budynku = 12  # m
wysokosc_drzewa = 21  # m
odleglosc_drzewa = 8  # m

# Wczytaj dane elewacji i azymutu słońca
dane_elewacja_azymut = pd.read_csv('dane_historyczne/roczna_elewacja_azymut_slonca_2024.csv', delimiter=',')

# Funkcja do obliczenia współczynnika cienia dla paneli wschodnich
def oblicz_cien_wschod(azymut_slonca, elewacja_slonca):
    if azymut_slonca <= 160: # Po przekroczeniu azymutu 160 cień drzewa jest nakierowany poza dach
        kat_cienia = math.degrees(math.atan((wysokosc_drzewa - wysokosc_budynku) / odleglosc_drzewa))
        if elewacja_slonca < kat_cienia: # Zawsze będzie w cieniu na tej płaszczyźnie, ze względu na niską elewację
            return 0.4  # Redukcja o 60%
    return 1.0

# Wczytaj rzeczywiste dane generacji prądu
dane_generacji = pd.read_csv('dane_historyczne/generacja_pradu_2024.csv')
dane_generacji['Data'] = pd.to_datetime(dane_generacji['Data'])
dane_generacji.set_index('Data', inplace=True)

# Analiza danych
wyniki = []
for wpis in dane_naslonecznienia['estimated_actuals']:
    data_godzina = pd.to_datetime(wpis['period_end']).tz_convert(None)
    ghi = wpis['ghi'] / 1000  # kW/m²
    temperatura = wpis['air_temp']

    # Filtruj odpowiedni czas z danych elewacji
    elewacje_azymuty = dane_elewacja_azymut[
        dane_elewacja_azymut['Date'] == data_godzina.date().strftime('%Y-%m-%d')]

    for _, row in elewacje_azymuty.iterrows():
        if row[f'E {data_godzina.hour:02}:00:00'] == '--':
            wspolczynnik_cienia = 0
        else:
            elewacja = float(row[f'E {data_godzina.hour:02}:00:00'])
            azymut_slonca = float(row[f'A {data_godzina.hour:02}:00:00'])
            wspolczynnik_cienia = oblicz_cien_wschod(azymut_slonca, elewacja)

        energia = oblicz_generacje_energii(
            ghi=ghi,
            temperatura=temperatura,
            kat_nachylenia=kat_nachylenia,
            azymut=azymut,
            sprawnosc=sprawnosc,
            powierzchnia=pole_instalacji,
            straty_systemowe=straty_systemowe,
            wspolczynnik_cienia=wspolczynnik_cienia,
            pmax_temp_coeff=wspolczynnik_pmax
        )

        if wyniki and wyniki[-1]['Data'] == data_godzina.floor('D'):
            wyniki[-1]['Symulowana generacja (kWh)'] += energia
        else:
            wyniki.append({
                'Data': data_godzina.floor('D'),
                'Symulowana generacja (kWh)': energia,
                'Rzeczywista generacja (kWh)': 0
            })

# Dopasowanie rzeczywistych danych generacji
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
wyniki_maj_grudzien = wyniki_df[(wyniki_df['Miesiąc'] >= 5)]
srednie_odchylenie = wyniki_maj_grudzien['Różnica (kWh)'].abs().mean()
# Obliczenie największego odchylenia
najwieksze_odchylenie = wyniki_maj_grudzien.loc[wyniki_maj_grudzien['Różnica (kWh)'].abs().idxmax()]

# Wyświetlenie szczegółów największego odchylenia
print("\nNajwiększe odchylenie:")
print(f"Data: {najwieksze_odchylenie['Data']}")
print(f"Symulowana generacja: {najwieksze_odchylenie['Symulowana generacja (kWh)']:.2f} kWh")
print(f"Rzeczywista generacja: {najwieksze_odchylenie['Rzeczywista generacja (kWh)']:.2f} kWh")
print(f"Odchylenie: {najwieksze_odchylenie['Różnica (kWh)']:.2f} kWh")
print(f"Odchylenie w procencie symulowanej generacji: {(najwieksze_odchylenie['Różnica (kWh)']/najwieksze_odchylenie['Symulowana generacja (kWh)']):.2f} %")
print(f"Średnie odchylenie prognozy dla miesięcy 5-12: {srednie_odchylenie:.2f} kWh")

# Eksport wyników
wyniki_df = pd.DataFrame(wyniki)
wyniki_df.to_csv('dane_historyczne/wyniki_porownania_generacji.csv', index=False)
print("Analiza zakończona. Wyniki zapisano w 'wyniki_porownania_generacji.csv'.")
