from modul_fotowoltaiczny import ModulFotowoltaiczny
from bateria import Bateria
from urzadzenie import Urzadzenie

# Inicjalizacja obiektów
modul = ModulFotowoltaiczny(
    model="PV1234",
    ilosc_ogniw=60,
    sprawnosc=20.5,
    wymiary=(1.6, 1.0, 0.04),
    moc_mppt=400,
    moc_nmot=370,
    wsp_temp={"Voc": -0.003, "Pmax": -0.0045},
    roczny_spadek_mocy=0.5,
    material_ogniw="monokrystaliczny",
    typ_szyby="hartowana",
    obciazenie_mechaniczne=5400
)

bateria = Bateria(
    model="BAT-5000",
    rodzaj="Li-ion",
    pojemnosc=10,  # kWh
    moc_namionowa=5000,  # W
    cykl_zycia=5000,
    napiecie=48,  # V
    wymiary=(1, 0.5, 0.5),
    prad_rozladowywania=100,  # A
    czas_ladowania=2  # h
)

lodowka = Urzadzenie(
    nazwa="Lodówka",
    model="LG-1234",
    klasa_energetyczna="A++",
    roczne_zuzycie_energii=250,
    moc_namionowa=120,
    zuzycie_pradu_na_cykl=0,
    dlugosc_cyklu=0,
    pobor_mocy_czuwania=46
)

pralka = Urzadzenie(
    nazwa="Pralka",
    model="Bosch-WM-5678",
    klasa_energetyczna="A+++",
    roczne_zuzycie_energii=180,
    moc_namionowa=2000,
    zuzycie_pradu_na_cykl=1.2,
    dlugosc_cyklu=120,
    pobor_mocy_czuwania=0.5
)

# Symulacja 24 godzin
czas_dnia = 16  # Godziny światła dziennego
czas_nocy = 8
naslonecznienie = 1.1  # kWh/kWp
temperatura_dzien = 24  # stopnie Celsjusza

for godzina in range(24):
    if godzina < czas_dnia:
        # Dzień: generowanie i zużywanie energii
        energia_wygenerowana = modul.generuj_prad(naslonecznienie, temperatura_dzien) / 1000  # kWh
        energia_lodowka = lodowka.odbior_pradu(tryb_czuwania=True)  # kWh
        energia_pralka = pralka.odbior_pradu(liczba_cykli=1 if godzina == 10 else 0)  # kWh
        energia_zuzyta = energia_lodowka + energia_pralka
        energia_pozostala = bateria.ladowanie(energia_wygenerowana - energia_zuzyta)
        print(f"Godzina {godzina}: Panel wygenerował {energia_wygenerowana:.2f} kWh. Zużyto {energia_zuzyta:.2f} kWh. Energia w baterii: {bateria.aktualny_stan:.2f} kWh.")
    else:
        # Noc: zużywanie energii
        energia_lodowka = lodowka.odbior_pradu(tryb_czuwania=True)  # kWh
        energia_pralka = pralka.odbior_pradu(liczba_cykli=1 if godzina == 21 else 0)  # kWh
        energia_zuzyta = energia_lodowka + energia_pralka
        energia_oddana = bateria.rozladowanie(energia_zuzyta, 1)
        print(f"Godzina {godzina}: Zużyto {energia_zuzyta:.2f} kWh. Energia oddana z baterii: {energia_oddana:.2f} kWh. Pozostała energia w baterii: {bateria.aktualny_stan:.2f} kWh.")
