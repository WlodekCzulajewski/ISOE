class Bateria:
    def __init__(self, model, rodzaj, pojemnosc, moc_namionowa, cykl_zycia, napiecie, wymiary, prad_rozladowywania, czas_ladowania):
        """
        Inicjalizuje obiekt klasy Bateria.

        :param model: Model akumulatora (str)
        :param rodzaj: Rodzaj akumulatora (str, np. "litowo-jonowy", "kwasowo-ołowiowy")
        :param pojemnosc: Pojemność baterii (Wh) (float)
        :param moc_namionowa: Moc znamionowa (W) (float)
        :param cykl_zycia: Liczba pełnych cykli ładowania i rozładowania (int)
        :param napiecie: Napięcie pracy (V) (float)
        :param wymiary: Wymiary baterii (szerokość, wysokość, głębokość) w metrach (tuple(float, float, float))
        :param prad_rozladowywania: Maksymalny prąd rozładowywania (A) (float)
        :param czas_ladowania: Czas pełnego ładowania (h) (float)
        """
        self.model = model
        self.rodzaj = rodzaj
        self.pojemnosc = pojemnosc
        self.moc_namionowa = moc_namionowa
        self.cykl_zycia = cykl_zycia
        self.napiecie = napiecie
        self.wymiary = wymiary
        self.prad_rozladowywania = prad_rozladowywania
        self.czas_ladowania = czas_ladowania
        self.aktualny_stan = 0  # Domyślnie bateria jest w pełni naładowana

    def rozladowanie(self, moc, czas):
        """
        Symuluje oddanie prądu przez baterię.

        :param moc: Moc pobierana z baterii (W)
        :param czas: Czas pobierania mocy (h)
        :return: Pozostała energia w baterii (Wh)
        """
        energia_do_oddania = moc * czas
        if energia_do_oddania > self.aktualny_stan:
            energia_do_oddania = self.aktualny_stan  # Ogranicz do dostępnej energii

        self.aktualny_stan -= energia_do_oddania
        return self.aktualny_stan

    def ladowanie(self, energia):
        """
        Symuluje ładowanie baterii.

        :param energia: Ilość energii dostarczanej do baterii (Wh)
        :return: Aktualny stan baterii (Wh)
        """
        self.aktualny_stan += energia
        if self.aktualny_stan > self.pojemnosc:
            self.aktualny_stan = self.pojemnosc  # Ogranicz do maksymalnej pojemności

        return self.aktualny_stan

    def stan_baterii(self):
        """
        Zwraca aktualny stan naładowania baterii w procentach.

        :return: Stan naładowania (%)
        """
        return (self.aktualny_stan / self.pojemnosc) * 100

    def __str__(self):
        szerokosc, wysokosc, glebokosc = self.wymiary
        return (
            f"Bateria: {self.model}\n"
            f"  Rodzaj: {self.rodzaj}\n"
            f"  Pojemność: {self.pojemnosc} kWh\n"
            f"  Moc znamionowa: {self.moc_namionowa} kW\n"
            f"  Cykl życia: {self.cykl_zycia} cykli\n"
            f"  Napięcie: {self.napiecie} V\n"
            f"  Wymiary: {szerokosc} m x {wysokosc} m x {glebokosc} m\n"
            f"  Prąd rozładowywania: {self.prad_rozladowywania} A\n"
            f"  Czas ładowania: {self.czas_ladowania} h\n"
            f"  Aktualny stan naładowania: {self.aktualny_stan:.2f} kWh ({self.stan_baterii():.2f}%)\n"
        )
