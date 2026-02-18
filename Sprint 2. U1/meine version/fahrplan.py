from datetime import datetime, timedelta


class Fahrplan:
    SEKUNDEN_PRO_MINUTE = 60
    def __init__(self, netzwerk, linie, fahrtzeiten, start_station,
                 betrieb_start, betrieb_ende, takt, haltezeiten, haltezeit_standard,
                 sekunden_pro_minute):
        self.netzwerk = netzwerk
        self.linie = linie
        self.fahrtzeiten = fahrtzeiten
        self.start_station = start_station
        self.betrieb_start = betrieb_start
        self.betrieb_ende = betrieb_ende
        self.takt = takt
        self.haltezeiten = haltezeiten
        self.haltezeit_standard = haltezeit_standard
        self.sekunden_pro_minute = SEKUNDEN_PRO_MINUTE


    def finde_naechste_abfahrt(self, route_info, wunschzeit):
        if route_info['ist_hinfahrt']:
            offset_sekunden = self._berechne_offset_hinfahrt(route_info)
        else:
            offset_sekunden = self._berechne_offset_rueckfahrt(route_info)

        offset = timedelta(seconds=offset_sekunden)

        wunsch = datetime.strptime(wunschzeit, "%H:%M")
        start = datetime.strptime(self.betrieb_start, "%H:%M")
        ende = datetime.strptime(self.betrieb_ende, "%H:%M")
        takt_delta = timedelta(minutes=self.takt)

        aktuelle_startzeit = start

        while aktuelle_startzeit <= ende:
            abfahrt_an_station = aktuelle_startzeit + offset

            if abfahrt_an_station >= wunsch:
                return abfahrt_an_station.strftime("%H:%M")

            aktuelle_startzeit += takt_delta

        return None


    def berechne_ankunftszeit_sekunden(self, pfad):
        if len(pfad) < 2:
            return 0

        gesamt_sekunden = 0

        # Fahrtzeiten (Minuten → Sekunden)
        for i in range(len(pfad) - 1):
            von = pfad[i]
            nach = pfad[i + 1]
            fahrtzeit_minuten = self.netzwerk.stationen[von][nach]["fahrtzeit"]
            gesamt_sekunden += fahrtzeit_minuten * self.sekunden_pro_minute

        # Haltezeiten an Zwischenstationen (bereits in Sekunden)
        for i in range(1, len(pfad) - 1):
            station = pfad[i]
            gesamt_sekunden += self.haltezeiten.get(station, self.haltezeit_standard)

        return gesamt_sekunden


    def berechne_abfahrtszeit_sekunden(self, pfad):
        ankunft_sekunden = self.berechne_ankunftszeit_sekunden(pfad)

        # Haltezeit an Zielstation
        zielstation = pfad[-1]
        halt_ziel = self.haltezeiten.get(zielstation, self.haltezeit_standard)

        return ankunft_sekunden + halt_ziel


    def _berechne_offset_hinfahrt(self, route_info):
        von_station = route_info['pfad'][0]
        pfad_bis_start = self.netzwerk.finde_kuerzesten_pfad(self.start_station, von_station)

        return self.berechne_abfahrtszeit_sekunden(pfad_bis_start)


    def _berechne_offset_rueckfahrt(self, route_info):
        von_station = route_info['pfad'][0]
        endstation = self.linie[-1]

        # Komplette Hinfahrt (Minuten → Sekunden)
        fahrt_bis_ende_sekunden = sum(self.fahrtzeiten) * self.sekunden_pro_minute

        # Haltezeiten auf Hinfahrt (bereits in Sekunden)
        haltezeit_hinfahrt_sekunden = 0
        for i in range(1, len(self.linie) - 1):
            station = self.linie[i]
            haltezeit_hinfahrt_sekunden += self.haltezeiten.get(station, self.haltezeit_standard)

        # Haltezeit an Endstation (bereits in Sekunden)
        halt_endstation = self.haltezeiten.get(endstation, self.haltezeit_standard)

        # Rückweg zum User (in Sekunden)
        pfad_rueck = self.netzwerk.finde_kuerzesten_pfad(endstation, von_station)
        abfahrt_user_sekunden = self.berechne_abfahrtszeit_sekunden(pfad_rueck)

        # Alles zusammen
        return fahrt_bis_ende_sekunden + haltezeit_hinfahrt_sekunden + halt_endstation + abfahrt_user_sekunden


    def frage_wunschzeit(self):
        print("Ab wann möchten Sie fahren? (HH:MM)")

        while True:
            zeit = input("> ")

            try:
                datetime.strptime(zeit, "%H:%M")
                return zeit
            except ValueError:
                print("Ungültiges Format. Bitte HH:MM verwenden.")
