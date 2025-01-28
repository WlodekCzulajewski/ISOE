import math

class ModulFotowoltaiczny:
    def __init__(self, model, sprawnosc, wymiary, moc_mppt, ilosc_paneli, straty_systemowe,
                 material_ogniw, typ_szyby, obciazenie_mechaniczne, kat_nachylenia, azymut):
        """
        Inicjalizuje obiekt klasy ModulFotowoltaiczny.

        :param model: Model modułu (str)
        :param sprawnosc: Sprawność modułu (%) (float)
        :param wymiary: Wymiary modułu (szerokość, wysokość, grubość) w metrach (tuple(float, float, float))
        :param moc_mppt: Moc przy MPPT dla pojedynczego panelu (W) (float)
        :param ilosc_paneli: Liczba paneli w instalacji (int)
        :param straty_systemowe: Straty systemowe (%) (float)
        :param material_ogniw: Materiał ogniw (str, np. "monokrystaliczny", "polikrystaliczny")
        :param typ_szyby: Typ szyby ochronnej (str, np. "hartowana")
        :param obciazenie_mechaniczne: Maksymalne obciążenie mechaniczne (Pa) (float)
        :param kat_nachylenia: Kąt nachylenia instalacji (stopnie) (float)
        :param azymut: Azymut instalacji (stopnie) (float)
        """
        self.model = model
        self.sprawnosc = sprawnosc / 100  # Konwersja na wartość dziesiętną
        self.wymiary = wymiary
        self.moc_mppt = moc_mppt
        self.ilosc_paneli = ilosc_paneli
        self.straty_systemowe = straty_systemowe / 100  # Konwersja na wartość dziesiętną
        self.material_ogniw = material_ogniw
        self.typ_szyby = typ_szyby
        self.obciazenie_mechaniczne = obciazenie_mechaniczne
        self.kat_nachylenia = kat_nachylenia
        self.azymut = azymut

        szerokosc, wysokosc, _ = wymiary
        self.pole_instalacji = szerokosc * wysokosc * ilosc_paneli  # m²
        self.moc_calowita_znamionowa = moc_mppt * ilosc_paneli / 1000  # kW

    def generuj_prad(self, ghi, temperatura, azymut_slonca, wspolczynnik_cienia=1.0, wsp_temp_pmax=-0.37):
        """
        Generuje wartość prądu w zależności od warunków.

        :param ghi: Globalne promieniowanie słoneczne (kWh/m²)
        :param temperatura: Temperatura otoczenia (°C)
        :param azymut_slonca: Azymut słońca względem południa (°)
        :param wspolczynnik_cienia: Redukcja efektywności z powodu cienia (0-1)
        :param wsp_temp_pmax: Współczynnik temperaturowy Pmax (%/°C)
        :return: Generowana moc w watach (float)
        """
        # Sprawdź, czy panel znajduje się w cieniu
        if azymut_slonca < 160:
            wspolczynnik_cienia *= 0.6  # Redukcja efektywności do 60%

        temperatura_stc = 25.0  # Standardowa temperatura odniesienia w °C
        korekta_temperaturowa = 1 + wsp_temp_pmax / 100 * (temperatura - temperatura_stc)
        sprawnosc_skorygowana = self.sprawnosc * korekta_temperaturowa

        # Ustal współczynnik orientacji
        wspolczynnik_orientacji = (
            math.cos(math.radians(self.kat_nachylenia)) *
            math.cos(math.radians(self.azymut - 180))
        )

        # Efektywne promieniowanie słoneczne
        efektywne_promieniowanie = ghi * self.pole_instalacji * wspolczynnik_orientacji

        # Efektywna moc z uwzględnieniem strat i cienia
        efektywna_moc = (
            efektywne_promieniowanie * sprawnosc_skorygowana *
            (1 - self.straty_systemowe) * wspolczynnik_cienia
        )

        return max(efektywna_moc, 0)  # Moc nie może być ujemna

    def __str__(self):
        szerokosc, wysokosc, grubosc = self.wymiary
        return (
            f"Moduł fotowoltaiczny: {self.model}\n"
            f"  Sprawność: {self.sprawnosc * 100:.2f}%\n"
            f"  Wymiary: {szerokosc} m x {wysokosc} m x {grubosc} m\n"
            f"  Moc MPPT (pojedynczy panel): {self.moc_mppt} W\n"
            f"  Ilość paneli: {self.ilosc_paneli}\n"
            f"  Moc całkowita znamionowa: {self.moc_calowita_znamionowa:.2f} kW\n"
            f"  Pole instalacji: {self.pole_instalacji:.2f} m²\n"
            f"  Straty systemowe: {self.straty_systemowe * 100:.2f}%\n"
            f"  Kąt nachylenia: {self.kat_nachylenia}°\n"
            f"  Azymut: {self.azymut}°\n"
            f"  Materiał ogniw: {self.material_ogniw}\n"
            f"  Typ szyby: {self.typ_szyby}\n"
            f"  Obciążenie mechaniczne: {self.obciazenie_mechaniczne} Pa\n"
        )
