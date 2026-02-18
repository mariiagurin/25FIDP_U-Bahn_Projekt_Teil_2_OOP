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

    def berechne_fahrtzeit(self, pfad):
        if len(pfad) < 2:
            return 0

        gesamt = 0

        #for i in range(len(pfad) - 1):
         #   von = pfad[i]
          #  nach = pfad[i + 1]
          #  gesamt += self.stationen[von][nach]["fahrtzeit"]

        #return gesamt

    #def finde_route(self, start, ziel, linie):
       # pfad = self.finde_kuerzesten_pfad(start, ziel)
        #fahrtzeit = self.berechne_fahrtzeit(pfad)
        #ist_hinfahrt = self._pruefe_richtung(pfad, linie)

        #return {
            #'pfad': pfad,
           # 'fahrtzeit': fahrtzeit,
           # 'ist_hinfahrt': ist_hinfahrt
        #pruefe R

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
            offset_minuten = self._berechne_offset_hinfahrt(route_info)
        else:
            offset_minuten = self._berechne_offset_rueckfahrt(route_info)

        offset = timedelta(minutes=offset_minuten)

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

    def _berechne_offset_hinfahrt(self, route_info):
        von_station = route_info['pfad'][0]
        pfad_bis_start = self.netzwerk.finde_kuerzesten_pfad(self.start_station, von_station)

        fahrtzeit_minuten = self.netzwerk.berechne_fahrtzeit(pfad_bis_start)

        haltezeit_sekunden = 0
        for i in range(1, len(pfad_bis_start) - 1):
            zwischenstation = pfad_bis_start[i]
            haltezeit_sekunden += self.haltezeiten.get(zwischenstation,
                                                       self.haltezeit_standard)

        haltezeit_minuten = round(haltezeit_sekunden / 60)

        return fahrtzeit_minuten + haltezeit_minuten

    def _berechne_offset_rueckfahrt(self, route_info):
        von_station = route_info['pfad'][0]
        endstation = self.linie[-1]

        fahrt_bis_ende = sum(self.fahrtzeiten)

        haltezeit_hinfahrt_sekunden = 0
        for i in range(1, len(self.linie) - 1):
            station = self.linie[i]
            haltezeit_hinfahrt_sekunden += self.haltezeiten.get(station,
                                                                self.haltezeit_standard)

        halt_endstation = self.haltezeiten.get(endstation, self.haltezeit_standard)

        pfad_rueck = self.netzwerk.finde_kuerzesten_pfad(endstation, von_station)
        fahrt_rueck = self.netzwerk.berechne_fahrtzeit(pfad_rueck)

        haltezeit_rueck_sekunden = 0
        for i in range(1, len(pfad_rueck) - 1):
            zwischenstation = pfad_rueck[i]
            haltezeit_rueck_sekunden += self.haltezeiten.get(zwischenstation,
                                                             self.haltezeit_standard)

        gesamt_haltezeit_sekunden = haltezeit_hinfahrt_sekunden + halt_endstation + haltezeit_rueck_sekunden
        gesamt_haltezeit_minuten = round(gesamt_haltezeit_sekunden / 60)

        return fahrt_bis_ende + fahrt_rueck + gesamt_haltezeit_minuten

    def frage_wunschzeit(self):
        print("Bitte Zeit im Format HH:MM eingeben (z.B. 08:07)")

        while True:
            zeit = input("Ab wann möchten Sie fahren? ")

            try:
                datetime.strptime(zeit, "%H:%M")
                return zeit
            except ValueError:
                print("Ungültiges Format. Bitte HH:MM verwenden.\n")


# ==============================================================================
# TEST
# ==============================================================================

if __name__ == "__main__":
    print("=== GRAPH BAUEN ===\n")

    netz = Netzwerk()
    netz.baue_graph(alle_linien, alle_fahrtzeiten)

    print("=== ROUTE SUCHEN ===\n")
    start, ziel = netz.nutzereingabe()

    print(f"Von: {start}")
    print(f"Nach: {ziel}\n")

    alle_pfade = netz.finde_alle_pfade(start, ziel)
    print(f"Gefundene Pfade: {len(alle_pfade)}")
    for i, pfad in enumerate(alle_pfade, 1):
        route = " -> ".join(pfad)
        anzahl = len(pfad) - 1
        print(f"  Pfad {i}: {route} ({anzahl} Stationen)")
    print()

    route_info = netz.finde_route(start, ziel, linie1)

    print("Kürzester Pfad:")
    route = " -> ".join(route_info['pfad'])
    anzahl = len(route_info['pfad']) - 1
    richtung = "Hinfahrt" if route_info['ist_hinfahrt'] else "Rückfahrt"
    print(f"  {route}")
    print(f"  Anzahl Stationen: {anzahl}")
    print(f"  Fahrtzeit: {route_info['fahrtzeit']} min")
    print(f"  Richtung: {richtung}\n")

    print("=== FAHRPLAN ===\n")
    fahrplan = Fahrplan(netz,
                        linie=linie1,
                        fahrtzeiten=fahrtzeiten1,
                        start_station=linie1_startstation,
                        betrieb_start=linie1_betriebsstart,
                        betrieb_ende=linie1_betriebsende,
                        takt=linie1_takt,
                        haltezeiten=linie1_haltezeiten,
                        haltezeit_standard=linie1_haltezeit_standard)

    wunschzeit = fahrplan.frage_wunschzeit()
    print()

    abfahrt = fahrplan.finde_naechste_abfahrt(route_info, wunschzeit)

    if abfahrt:
        print(f"Nächste Bahn an Station {start}: {abfahrt} Uhr")
    else:
        print(f"Heute keine Bahn mehr (Betriebsende: {fahrplan.betrieb_ende})")
