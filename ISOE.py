import json
import pandas as pd
import math
from datetime import datetime, timedelta
from modul_fotowoltaiczny import ModulFotowoltaiczny
from bateria import Bateria
from urzadzenie import Urzadzenie

class InteligentnySystemOszczedzaniaEnergii:
    def __init__(self, modul_fotowoltaiczny, bateria, urzadzenia):
        self.modul_fotowoltaiczny = modul_fotowoltaiczny
        self.bateria = bateria
        self.urzadzenia = urzadzenia
        self.godzina = datetime.now()
        self.zuzycie_urzadzen = 0
        self.generacja_pradu = 0
        self.stan_baterii = bateria.pojemnosc
        self.pobrana_energia_sieci = 0
        self.log = []

    def aktualizuj_generacje_pradu(self, ghi, temperatura):
        self.generacja_pradu = self.modul_fotowoltaiczny.generuj_prad(ghi, temperatura)

    def aktualizuj_zuzycie_urzadzen(self):
        self.zuzycie_urzadzen = sum([urzadzenie.odbior_pradu() for urzadzenie in self.urzadzenia])

    def zarzadzaj_przeplywem_energii(self):
        nadwyzka_pradu = self.generacja_pradu - self.zuzycie_urzadzen

        if nadwyzka_pradu > 0:
            # Ładuj baterię nadwyżką prądu
            self.stan_baterii = self.bateria.laduj(nadwyzka_pradu)
        else:
            # Sprawdź, czy bateria ma energię do rozładowania
            potrzebna_energia = abs(nadwyzka_pradu)
            energia_z_baterii = self.bateria.rozladuj(potrzebna_energia)
            brakujaca_energia = potrzebna_energia - energia_z_baterii

            if brakujaca_energia > 0:
                # Pobierz brakującą energię z sieci
                self.pobrana_energia_sieci += brakujaca_energia

    def zapisz_dane(self):
        wpis = {
            "czas": self.godzina,
            "generacja_pradu": self.generacja_pradu,
            "zuzycie_urzadzen": self.zuzycie_urzadzen,
            "stan_baterii": self.stan_baterii,
            "pobrana_energia_sieci": self.pobrana_energia_sieci
        }
        self.log.append(wpis)

    def symuluj_godzine(self, ghi, temperatura):
        self.aktualizuj_generacje_pradu(ghi, temperatura)
        self.aktualizuj_zuzycie_urzadzen()
        self.zarzadzaj_przeplywem_energii()
        self.zapisz_dane()
        self.godzina += timedelta(hours=1)

    def zapisz_log_do_csv(self, nazwa_pliku):
        df = pd.DataFrame(self.log)
        df.to_csv(nazwa_pliku, index=False)

# Inicjalizacja obiektów
modul = ModulFotowoltaiczny(sprawnosc=0.14, moc_nominalna=5.76, straty_systemowe=0.15, kat_nachylenia=26, azymut=180)
bateria = Bateria(pojemnosc=10, moc_znamionowa=5)
lodowka = Urzadzenie(nazwa="Lodówka", moc_znamionowa=0.1, dlugosc_cyklu=1440, pobor_mocy_czuwania=0.01)
pralka = Urzadzenie(nazwa="Pralka", moc_znamionowa=2, dlugosc_cyklu=120, pobor_mocy_czuwania=0.01)
system = InteligentnySystemOszczedzaniaEnergii(modul, bateria, [lodowka, pralka])

# Symulacja dla jednej doby
ghi_data = [0.5, 0.6, 0.7, 0.8, 1.0, 1.1, 1.2, 1.3, 1.1, 1.0, 0.8, 0.6, 0.4, 0.2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Przykładowe dane GHI
temp_data = [15] * 24  # Stała temperatura

for i in range(24):
    system.symuluj_godzine(ghi=ghi_data[i], temperatura=temp_data[i])

# Zapis logów do pliku CSV
system.zapisz_log_do_csv("log_systemu.csv")
