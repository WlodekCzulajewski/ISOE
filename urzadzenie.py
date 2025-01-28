class Urzadzenie:
    def __init__(self, nazwa, model, klasa_energetyczna, roczne_zuzycie_energii, moc_namionowa,
                 zuzycie_pradu_na_cykl=0, dlugosc_cyklu=0, pobor_mocy_czuwania=0):
        """
        Inicjalizuje obiekt klasy Urzadzenie.

        :param nazwa: Nazwa urządzenia (str)
        :param model: Model urządzenia (str)
        :param klasa_energetyczna: Klasa energetyczna urządzenia (str, np. "A+++", "A++")
        :param roczne_zuzycie_energii: Roczne zużycie energii (kWh) (float)
        :param moc_namionowa: Moc znamionowa urządzenia (W) (float)
        :param zuzycie_pradu_na_cykl: Zużycie energii na cykl (kWh) (float)
        :param dlugosc_cyklu: Długość cyklu pracy (w minutach) (int)
        :param pobor_mocy_czuwania: Pobór mocy w trybie czuwania (W) (float)
        """
        self.nazwa = nazwa
        self.model = model
        self.klasa_energetyczna = klasa_energetyczna
        self.roczne_zuzycie_energii = roczne_zuzycie_energii
        self.moc_namionowa = moc_namionowa
        self.zuzycie_pradu_na_cykl = zuzycie_pradu_na_cykl
        self.dlugosc_cyklu = dlugosc_cyklu
        self.pobor_mocy_czuwania = pobor_mocy_czuwania

    def odbior_pradu(self, tryb_czuwania=False, liczba_cykli=0):
        """
        Oblicza zużycie energii przez urządzenie w zależności od trybu pracy.

        :param tryb_czuwania: Czy urządzenie jest w trybie czuwania (bool)
        :param liczba_cykli: Liczba wykonanych cykli pracy (int)
        :return: Zużyta energia w kWh (float)
        """
        if tryb_czuwania:
            return (self.pobor_mocy_czuwania / 1000) * (24 / 60)  # Zużycie energii na minutę w kWh
        else:
            return liczba_cykli * self.zuzycie_pradu_na_cykl
