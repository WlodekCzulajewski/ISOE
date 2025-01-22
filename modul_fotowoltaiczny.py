class ModulFotowoltaiczny:
    def __init__(self, model, ilosc_ogniw, sprawnosc, wymiary, moc_mppt, moc_nmot, wsp_temp, roczny_spadek_mocy, material_ogniw, typ_szyby, obciazenie_mechaniczne):
        """
        Inicjalizuje obiekt klasy ModulFotowoltaiczny.

        :param model: Model modułu (str)
        :param ilosc_ogniw: Liczba ogniw w module (int)
        :param sprawnosc: Sprawność modułu (%) (float)
        :param wymiary: Wymiary modułu (szerokość, wysokość, grubość) w metrach (tuple(float, float, float))
        :param moc_mppt: Moc przy MPPT (W) (float)
        :param moc_nmot: Moc przy NMOT/NCOT (W) (float)
        :param wsp_temp: Współczynniki temperaturowe (dict)
        :param roczny_spadek_mocy: Roczny spadek mocy (%) (float)
        :param material_ogniw: Materiał ogniw (str, np. "monokrystaliczny", "polikrystaliczny")
        :param typ_szyby: Typ szyby ochronnej (str, np. "hartowana")
        :param obciazenie_mechaniczne: Maksymalne obciążenie mechaniczne (Pa) (float)
        """
        self.model = model
        self.ilosc_ogniw = ilosc_ogniw
        self.sprawnosc = sprawnosc / 100  # Konwersja na wartość dziesiętną
        self.wymiary = wymiary
        self.moc_mppt = moc_mppt
        self.moc_nmot = moc_nmot
        self.wsp_temp = wsp_temp  # Oczekiwany format: {"Voc": -0.003, "Pmax": -0.0045}
        self.roczny_spadek_mocy = roczny_spadek_mocy / 100  # Konwersja na wartość dziesiętną
        self.material_ogniw = material_ogniw
        self.typ_szyby = typ_szyby
        self.obciazenie_mechaniczne = obciazenie_mechaniczne

    def generuj_prad(self, naslonecznienie, temperatura, lata_uzytkowania=0):
        """
        Generuje wartość prądu w zależności od warunków.

        :param naslonecznienie: Poziom nasłonecznienia (kW/m^2)
        :param temperatura: Temperatura otoczenia (°C)
        :param lata_uzytkowania: Ilość lat od instalacji modułu (int, domyślnie 0)
        :return: Generowana moc w watach (float)
        """
        # Uwzględnij roczny spadek mocy
        moc_obnizona = self.moc_mppt * ((1 - self.roczny_spadek_mocy) ** lata_uzytkowania)

        # Uwzględnij wpływ temperatury na moc
        delta_temp = temperatura - 25  # Referencyjna temperatura to 25°C
        wsp_temp_pmax = self.wsp_temp.get("Pmax", 0)  # Domyślnie brak wpływu, jeśli klucz nie istnieje
        moc_temperatura = moc_obnizona * (1 + wsp_temp_pmax * delta_temp)

        # Uwzględnij nasłonecznienie
        moc_koncowa = moc_temperatura * (naslonecznienie / 1.0)  # 1.0 kW/m^2 to standardowe nasłonecznienie

        return max(moc_koncowa, 0)  # Moc nie może być ujemna

    def __str__(self):
        szerokosc, wysokosc, grubosc = self.wymiary
        return (
            f"Moduł fotowoltaiczny: {self.model}\n"
            f"  Ilość ogniw: {self.ilosc_ogniw}\n"
            f"  Sprawność: {self.sprawnosc * 100:.2f}%\n"
            f"  Wymiary: {szerokosc} m x {wysokosc} m x {grubosc} m\n"
            f"  Moc MPPT: {self.moc_mppt} W\n"
            f"  Moc NMOT: {self.moc_nmot} W\n"
            f"  Roczny spadek mocy: {self.roczny_spadek_mocy * 100:.2f}%\n"
            f"  Współczynniki temperaturowe: {self.wsp_temp}\n"
            f"  Materiał ogniw: {self.material_ogniw}\n"
            f"  Typ szyby: {self.typ_szyby}\n"
            f"  Obciążenie mechaniczne: {self.obciazenie_mechaniczne} Pa\n"
        )
