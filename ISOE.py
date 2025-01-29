import pandas as pd
import threading
import time
from datetime import datetime, timedelta
from modul_fotowoltaiczny import ModulFotowoltaiczny
from bateria import Bateria
from urzadzenie import Urzadzenie
from prognoza_naświetlania import pobierz_prognoze

class InteligentnySystemOszczedzaniaEnergii:
    def __init__(self, modul_fotowoltaiczny, bateria, urzadzenia):
        self.modul_fotowoltaiczny = modul_fotowoltaiczny
        self.bateria = bateria
        self.urzadzenia = urzadzenia
        self.godzina = datetime.now()
        self.log = []

    def aktualizuj_generacje_pradu(self, ghi, temperatura, azymut_slonca):
        return self.modul_fotowoltaiczny.generuj_prad(ghi, temperatura, azymut_slonca)

    def aktualizuj_zuzycie_urzadzen(self, harmonogram, godzina):
        zuzycie = 0
        for urzadzenie, cykle in harmonogram.items():
            if godzina in cykle:
                zuzycie += urzadzenie.odbior_pradu(liczba_cykli=1)
            else:
                zuzycie += urzadzenie.odbior_pradu(tryb_czuwania=True)
        return zuzycie

    def zarzadzaj_przeplywem_energii(self, generacja_pradu, zuzycie_urzadzen):
        """
        Zarządzanie przepływem energii na podstawie schematu decyzyjnego.
        """
        if generacja_pradu > 0:
            if generacja_pradu >= zuzycie_urzadzen:
                nadwyzka = generacja_pradu - zuzycie_urzadzen
                if self.bateria.stan_baterii() < 100:
                    self.bateria.ladowanie(nadwyzka)
                    self.log.append({"status": "Ładowanie baterii", "energia": nadwyzka})
                else:
                    self.log.append({"status": "Nadwyżka energii do sieci", "energia": nadwyzka})
            else:
                brakujaca_energia = zuzycie_urzadzen - generacja_pradu
                energia_z_baterii = self.bateria.rozladowanie(brakujaca_energia, 1)
                brakujaca_energia -= energia_z_baterii
                if brakujaca_energia > 0:
                    self.log.append({"status": "Pobór z sieci", "energia": brakujaca_energia})
        else:
            if self.bateria.stan_baterii() > 0:
                energia_z_baterii = self.bateria.rozladowanie(zuzycie_urzadzen, 1)
                if energia_z_baterii < zuzycie_urzadzen:
                    brakujaca_energia = zuzycie_urzadzen - energia_z_baterii
                    self.log.append({"status": "Pobór z sieci", "energia": brakujaca_energia})
            else:
                self.log.append({"status": "Całość pobierana z sieci", "energia": zuzycie_urzadzen})

    def zaplanuj_harmonogram(self, prognoza):
        harmonogram = {urzadzenie: [] for urzadzenie in self.urzadzenia}
        dzien = datetime.now().day

        # Sortowanie prognozy według dostępnej generacji prądu
        prognoza.sort(key=lambda x: x["ghi"], reverse=True)

        godzina_zmywarki = prognoza[0]["period_end"]  # Najlepsza godzina dla zmywarki
        godzina_pralki = prognoza[1]["period_end"] if dzien % 2 == 0 else None  # Co dwa dni
        godzina_suszarki = prognoza[2]["period_end"] if dzien % 2 == 1 else None  # W inne dni niż pralka

        for godzina, prognoza_godzinna in enumerate(prognoza):
            czas = datetime.fromisoformat(prognoza_godzinna["period_end"].replace("Z", "+00:00")).hour

            if prognoza_godzinna["period_end"] == godzina_zmywarki:
                for urzadzenie in self.urzadzenia:
                    if urzadzenie.nazwa == "Zmywarka":
                        harmonogram[urzadzenie].append(godzina)

            if prognoza_godzinna["period_end"] == godzina_pralki:
                for urzadzenie in self.urzadzenia:
                    if urzadzenie.nazwa == "Pralka":
                        harmonogram[urzadzenie].append(godzina)

            if prognoza_godzinna["period_end"] == godzina_suszarki:
                for urzadzenie in self.urzadzenia:
                    if urzadzenie.nazwa == "Suszarka":
                        harmonogram[urzadzenie].append(godzina)

        return harmonogram

    def symuluj_dobe(self, prognoza):
        harmonogram = self.zaplanuj_harmonogram(prognoza)
        for godzina, prognoza_godzinna in enumerate(prognoza):
            generacja = self.aktualizuj_generacje_pradu(
                prognoza_godzinna["ghi"], prognoza_godzinna["air_temp"], prognoza_godzinna["azimuth"]
            )
            zuzycie = self.aktualizuj_zuzycie_urzadzen(harmonogram, godzina)
            self.zarzadzaj_przeplywem_energii(generacja, zuzycie)

            self.log.append({
                "czas": self.godzina + timedelta(hours=godzina),
                "generacja_pradu": generacja,
                "zuzycie_urzadzen": zuzycie,
                "stan_baterii": self.bateria.aktualny_stan
            })

    def zapisz_log_do_csv(self, nazwa_pliku):
        df = pd.DataFrame(self.log)
        df.to_csv(nazwa_pliku, index=False)

# Ustawienie harmonogramu pobierania prognozy

def harmonogram_pobierania():
    while True:
        teraz = datetime.now()
        nastepny_cykl = (teraz + timedelta(days=1)).replace(hour=3, minute=0, second=0, microsecond=0)
        czas_oczekiwania = (nastepny_cykl - teraz).total_seconds()
        time.sleep(czas_oczekiwania)
        pobierz_prognoze()

harmonogram_thread = threading.Thread(target=harmonogram_pobierania, daemon=True)
harmonogram_thread.start()

# Inicjalizacja obiektów
modul = ModulFotowoltaiczny(
    model="SM-320-60M",
    sprawnosc=19.55,
    wymiary=(0.992, 1.640, 0.04),
    moc_mppt=320,
    ilosc_paneli=18,
    straty_systemowe=10,
    material_ogniw="monokrystaliczny",
    typ_szyby="hartowana",
    obciazenie_mechaniczne=5400,
    kat_nachylenia=26,
    azymut=180
)

bateria = Bateria(
    model="BAT-5000",
    rodzaj="Li-ion",
    pojemnosc=10000,  # Wh
    moc_namionowa=5000,  # W
    cykl_zycia=5000,
    napiecie=48,  # V
    wymiary=(1, 0.5, 0.5),
    prad_rozladowywania=100,  # A
    czas_ladowania=2  # h
)

lodowka = Urzadzenie(
    nazwa="Lodówka",
    model="LG 606L GSJ361DIDV",
    klasa_energetyczna="F",
    roczne_zuzycie_energii=419,
    moc_namionowa=113,
    zuzycie_pradu_na_cykl=1130,
    dlugosc_cyklu=1440,
    pobor_mocy_czuwania=47
)

pralka = Urzadzenie(
    nazwa="Pralka",
    model="LG F4WV709S1BE",
    klasa_energetyczna="A",
    roczne_zuzycie_energii=0,
    moc_namionowa=2000,
    zuzycie_pradu_na_cykl=509,
    dlugosc_cyklu=120,
    pobor_mocy_czuwania=0.5
)

suszarka = Urzadzenie(
    nazwa="Suszarka",
    model="WHIRLPOOL W6 D84WB EE",
    klasa_energetyczna="A+++",
    roczne_zuzycie_energii=176,
    moc_namionowa=1400,
    zuzycie_pradu_na_cykl=1410,
    dlugosc_cyklu=90,
    pobor_mocy_czuwania=0.18
)

zmywarka = Urzadzenie(
    nazwa="Zmywarka",
    model="BOSCH SPS4EMI60E",
    klasa_energetyczna="D",
    roczne_zuzycie_energii=0,
    moc_namionowa=1120,
    zuzycie_pradu_na_cykl=1120,
    dlugosc_cyklu=180,
    pobor_mocy_czuwania=0.5
)

system = InteligentnySystemOszczedzaniaEnergii(modul, bateria, [lodowka, pralka, suszarka, zmywarka])
prognoza = pobierz_prognoze()
system.symuluj_dobe(prognoza)
system.zapisz_log_do_csv("dane_biezace/og_systemu.csv")
print(system.log)
