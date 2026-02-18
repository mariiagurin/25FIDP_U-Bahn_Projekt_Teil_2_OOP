from datetime import datetime, timedelta

# Linie 1 definieren (Langwasser Süd → Fürth Hbf.)
linie1 = ["Langwasser Süd", "Gemeinschaftshaus", "Langwasser Mitte", "Scharfreiterring", "Langwasser Nord",
        "Messe", "Bauernfeindstraße", "Hasenbuck", "Frankenstraße", "Maffeiplatz", "Aufseßplatz", "Hauptbahnhof",
        "Lorenzkirche", "Weißer Turm", "Plärrer", "Gostenhof", "Bärenschanze", "Maximilianstraße", "Eberhardshof",
        "Muggenhof", "Stadtgrenze", "Jakobinenstraße", "Fürth Hbf."]
fahrtzeiten1 = [3, 2, 2, 3, 2, 3, 2, 2, 2, 1, 2, 2, 3, 2, 2, 1, 2, 2, 2, 3, 2, 3]
linie1_startstation = "Langwasser Süd"
linie1_betriebsstart = "05:00"
linie1_betriebsende = "23:00"
linie1_takt = 10

linie1_haltezeiten = {
    "Langwasser Süd": 60,
    "Hauptbahnhof": 60,
    "Plärrer": 60,
    "Fürth Hbf.": 60
}
linie1_haltezeit_standard = 30

alle_linien = [linie1]
alle_fahrtzeiten = [fahrtzeiten1]

# Konstanten
SEKUNDEN_PRO_MINUTE = 60



# ==============================================================================
# KLASSE: Netzwerk
# ==============================================================================

class Netzwerk:

    def __init__(self):
        self.stationen = {}


    def baue_graph(self, linien, fahrzeiten_liste):
        for linie, fahrtzeiten in zip(linien, fahrzeiten_liste):
            for i in range(len(linie) - 1):
                a = linie[i]
                b = linie[i + 1]
                fahrtzeit = fahrtzeiten[i]

                if a not in self.stationen:
                    self.stationen[a] = {}
                if b not in self.stationen:
                    self.stationen[b] = {}

                self.stationen[a][b] = {"fahrtzeit": fahrtzeit}
                self.stationen[b][a] = {"fahrtzeit": fahrtzeit}


    def nutzereingabe(self):
        while True:
            start = input("Start-Station: ")

            for station in self.stationen:
                if start.lower() == station.lower():
                    start = station
                    break
            else:
                print("Station nicht gefunden. Erneut eingeben.\n")
                continue

            break

        while True:
            ziel = input("Ziel-Station: ")

            for station in self.stationen:
                if ziel.lower() == station.lower():
                    ziel = station
                    break
            else:
                print("Station nicht gefunden. Erneut eingeben.\n")
                continue

            break

        return start, ziel


    def finde_alle_pfade(self, start, ziel, pfad=None, ergebnis=None):
        if pfad is None:
            pfad = []
        if ergebnis is None:
            ergebnis = []

        pfad.append(start)

        if start == ziel:
            ergebnis.append(pfad.copy())
            pfad.pop()
            return ergebnis

        for nachbar in self.stationen[start]:
            if nachbar not in pfad:
                self.finde_alle_pfade(nachbar, ziel, pfad, ergebnis)

        pfad.pop()
        return ergebnis


    def finde_kuerzesten_pfad(self, start, ziel):
        alle = self.finde_alle_pfade(start, ziel)

        if not alle:
            return []

        kuerzester = min(alle, key=len)
        return kuerzester


    def finde_route(self, start, ziel, linie):
        pfad = self.finde_kuerzesten_pfad(start, ziel)
        ist_hinfahrt = self._pruefe_richtung(pfad, linie)

        return {
            'pfad': pfad,
            'ist_hinfahrt': ist_hinfahrt
        }


    def _pruefe_richtung(self, pfad, linie):
        if len(pfad) < 2:
            return True

        start_station = pfad[0]
        naechste_station = pfad[1]

        start_index = linie.index(start_station)
        naechste_index = linie.index(naechste_station)

        return naechste_index > start_index

# ==============================================================================
# Klasse Fahrplan
# ==============================================================================

class Fahrplan:

    def __init__(self, netzwerk, linie, fahrtzeiten, start_station,
                 betrieb_start, betrieb_ende, takt, haltezeiten, haltezeit_standard):
        self.netzwerk = netzwerk
        self.linie = linie
        self.fahrtzeiten = fahrtzeiten
        self.start_station = start_station
        self.betrieb_start = betrieb_start
        self.betrieb_ende = betrieb_ende
        self.takt = takt
        self.haltezeiten = haltezeiten
        self.haltezeit_standard = haltezeit_standard


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
            gesamt_sekunden += fahrtzeit_minuten * SEKUNDEN_PRO_MINUTE

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
        fahrt_bis_ende_sekunden = sum(self.fahrtzeiten) * SEKUNDEN_PRO_MINUTE

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


# ==============================================================================
# TEST
# ==============================================================================

if __name__ == "__main__":
    # Graph bauen
    netz = Netzwerk()
    netz.baue_graph(alle_linien, alle_fahrtzeiten)

    # Fahrplan erstellen
    fahrplan = Fahrplan(netz,
                        linie=linie1,
                        fahrtzeiten=fahrtzeiten1,
                        start_station=linie1_startstation,
                        betrieb_start=linie1_betriebsstart,
                        betrieb_ende=linie1_betriebsende,
                        takt=linie1_takt,
                        haltezeiten=linie1_haltezeiten,
                        haltezeit_standard=linie1_haltezeit_standard)

    # User-Eingaben
    start, ziel = netz.nutzereingabe()
    route_info = netz.finde_route(start, ziel, linie1)
    wunschzeit = fahrplan.frage_wunschzeit()

    # Abfahrt berechnen
    abfahrt = fahrplan.finde_naechste_abfahrt(route_info, wunschzeit)

    if abfahrt:
        # Ankunftszeit berechnen (in Sekunden!)
        pfad = route_info['pfad']
        fahrtdauer_sekunden = fahrplan.berechne_ankunftszeit_sekunden(pfad)

        abfahrt_dt = datetime.strptime(abfahrt, "%H:%M")
        ankunft_dt = abfahrt_dt + timedelta(seconds=fahrtdauer_sekunden)

        print(f"Start:             {start}")
        print(f"Ziel:              {ziel}")
        print(f"Gewünschte Zeit:   {wunschzeit} Uhr")
        print(f"Nächste Abfahrt:   {abfahrt} Uhr")
        print(f"Ankunft am Ziel:   {ankunft_dt.strftime('%H:%M')} Uhr")
    else:
        print(f"Start:             {start}")
        print(f"Ziel:              {ziel}")
        print(f"Gewünschte Zeit:   {wunschzeit} Uhr")
        print(f"Status:            Kein Betrieb mehr (Ende: {fahrplan.betrieb_ende})")