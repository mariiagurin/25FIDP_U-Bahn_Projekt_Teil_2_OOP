from datetime import datetime, timedelta


# ==============================================================================
# KLASSE: Verbindung

class Verbindung:
    """Repräsentiert eine Verbindung zwischen zwei Stationen.

    Speichert Fahrtzeit und Linien zwischen zwei Nachbarstationen.

    Args:
        von:       Station-Objekt (Startstation)
        nach:      Station-Objekt (Zielstation)
        fahrtzeit: INT - Minuten zwischen den Stationen
        linien:    LIST - Liniennamen die diese Verbindung nutzen
    """

    def __init__(self, von, nach, fahrtzeit, linien=None):
        self.von       = von
        self.nach      = nach
        self.fahrtzeit = fahrtzeit   # Minuten
        self.linien    = linien or []

    def __str__(self):
        return f"Verbindung({self.von} -> {self.nach}, {self.fahrtzeit} min)"

    def __repr__(self):
        return self.__str__()


# ==============================================================================
# KLASSE: Station

class Station:
    """Repräsentiert eine Haltestelle im U-Bahn-Netz.

    Wird durch _baue_graph() in Netzwerk befüllt:
    - linien:             auf welchen Linien sie liegt
    - nachbarn:           benachbarte Stationen als Verbindung-Objekte
    - haltezeit:          automatisch gesetzt je nach Stationstyp
    - ist_endhaltestelle: erste/letzte Station einer Linie
    """

    def __init__(self, name):
        self.name               = name
        self.linien             = []   # ["U1", "U2", ...]
        self.nachbarn           = {}   # {Station: Verbindung-Objekt}
        self.ist_endhaltestelle = False
        self.haltezeit          = 0    # Sekunden
        self.min_umstiegszeit   = 0    # Minuten — wird durch Netzwerk gesetzt

    @property
    def ist_umsteigestation(self):
        """True wenn Station auf mehr als einer Linie liegt."""
        return len(self.linien) > 1

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Station({self.name})"

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


# ==============================================================================
# KLASSE: Linie

class Linie:
    """Repräsentiert eine U-Bahn-Linie.

    Args:
        name:        STRING - Linienname z.B. "U1"
        stationen:   LIST[Station] - Station-Objekte in Reihenfolge
        fahrtzeiten: LIST[INT] - Minuten zwischen Stationen
    """

    def __init__(self, name, stationen, fahrtzeiten):
        self.name        = name
        self.stationen   = stationen
        self.fahrtzeiten = fahrtzeiten

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Linie({self.name})"


# ==============================================================================
# KLASSE: Route

class Route:
    """Repräsentiert eine gefundene Route zwischen zwei Stationen.

    Speichert den Pfad als Liste von (Station, Linie) Paaren.
    Die Linie gibt an mit welcher Linie man ZU dieser Station gefahren ist.
    Die Start-Station hat linie=None (noch keine Linie).

    Beispiel pfad:
        [(Messe, None), (Bauernfeindstr, U1), ...,
         (Hauptbahnhof, U1), (Wöhrder Wiese, U3), ..., (Maxfeld, U3)]

    Da die DFS Linien bereits kennt, ist get_segmente() nur noch simples
    Gruppieren — keine Logik mehr nötig.

    Args:
        pfad: LIST[(Station, linie_name)] - Ergebnis der linienbewussten DFS
    """

    def __init__(self, pfad):
        self.pfad  = pfad        # [(Station, linie_name), ...]
        self.start = pfad[0][0]
        self.ziel  = pfad[-1][0]

    @property
    def stationen(self):
        """Alle Stationen ohne Linienzuordnung."""
        return [station for station, linie in self.pfad]

    def get_segmente(self):
        """Teilt die Route in Abschnitte pro Linie auf.

        Simples Gruppieren — Linie ist bereits im Pfad bekannt.
        Umstiegsstationen gehören zum Ende des alten UND Anfang des neuen Segments.

        Returns:
            LIST of (linie_name, LIST[Station])

        Beispiel:
            [("U1", [Messe, ..., Hauptbahnhof]),
             ("U3", [Hauptbahnhof, ..., Maxfeld])]
        """
        segmente          = []
        aktuelle_linie    = self.pfad[1][1]   # erste Linie (Index 0 hat None)
        segment_start_idx = 0

        for i in range(2, len(self.pfad)):
            _, linie = self.pfad[i]

            if linie != aktuelle_linie:
                seg_stationen = [s for s, l in self.pfad[segment_start_idx:i]]
                segmente.append((aktuelle_linie, seg_stationen))
                segment_start_idx = i - 1   # Umstiegsstation startet neues Segment
                aktuelle_linie    = linie

        # Letztes Segment
        seg_stationen = [s for s, l in self.pfad[segment_start_idx:]]
        segmente.append((aktuelle_linie, seg_stationen))

        return segmente

    def get_umstiegestationen(self):
        """Gibt alle Umstiegsstationen auf der Route zurück.

        Returns:
            LIST[Station]
        """
        segmente = self.get_segmente()
        return [seg_stationen[-1] for _, seg_stationen in segmente[:-1]]

    def __len__(self):
        return len(self.pfad)

    def __iter__(self):
        return iter(self.stationen)

    def __str__(self):
        return ' -> '.join(s.name for s in self.stationen)


# ==============================================================================
# KLASSE: Netzwerk

class Netzwerk:
    """Graph und Routing für das U-Bahn-Netz.

    Wird EINMAL erstellt. Graph wird sofort im __init__() gebaut.

    Args:
        linien_daten: Liste von Dictionaries:
        [
            {
                "name":               "U1",
                "stationen":          ["Langwasser Süd", ...],
                "fahrtzeiten":        [3, 2, 2, ...],
                "haltezeit_end":      60,
                "haltezeit_umstieg":  60,
                "haltezeit_standard": 30
            },
            ...
        ]
    """

    def __init__(self, linien_daten, umstiegszeiten=None):
        self.stationen = {}   # {name: Station-Objekt}
        self.linien    = []   # [Linie-Objekt, ...]
        self._baue_graph(linien_daten, umstiegszeiten)


    # PRIVATE: Graph bauen

    def _baue_graph(self, linien_daten, umstiegszeiten):
        """Baut den Graph auf."""
        self._stationen_erstellen(linien_daten)
        self._linien_erstellen(linien_daten)
        self._linien_zuweisen()
        self._endhaltestellen_markieren()
        self._stationen_verbinden()
        self._setze_haltezeiten(linien_daten)
        if umstiegszeiten:
            self._setze_umstiegszeiten(umstiegszeiten)

    def _stationen_erstellen(self, linien_daten):
        """Stationsnamen → Station-Objekte (keine Duplikate!)"""
        for linie_info in linien_daten:
            for name in linie_info["stationen"]:
                if name not in self.stationen:
                    self.stationen[name] = Station(name)

    def _linien_erstellen(self, linien_daten):
        """Linie-Objekte mit Station-Objekten und Fahrtzeiten erstellen."""
        for linie_info in linien_daten:
            stationen_objekte = [
                self.stationen[name]
                for name in linie_info["stationen"]
            ]
            linie = Linie(
                name=linie_info["name"],
                stationen=stationen_objekte,
                fahrtzeiten=linie_info["fahrtzeiten"]
            )
            self.linien.append(linie)

    def _linien_zuweisen(self):
        """Jeder Station sagen auf welchen Linien sie liegt."""
        for linie in self.linien:
            for station in linie.stationen:
                if linie.name not in station.linien:
                    station.linien.append(linie.name)

    def _endhaltestellen_markieren(self):
        """Erste und letzte Station jeder Linie markieren."""
        for linie in self.linien:
            linie.stationen[0].ist_endhaltestelle = True
            linie.stationen[-1].ist_endhaltestelle = True

    def _stationen_verbinden(self):
        """Adjazenzliste aufbauen - mit Verbindung-Objekten!"""
        for linie in self.linien:
            for i in range(len(linie.stationen) - 1):
                a         = linie.stationen[i]
                b         = linie.stationen[i + 1]
                fahrtzeit = linie.fahrtzeiten[i]

                # Verbindung a → b
                if b not in a.nachbarn:
                    a.nachbarn[b] = Verbindung(a, b, fahrtzeit, [linie.name])
                elif linie.name not in a.nachbarn[b].linien:
                    a.nachbarn[b].linien.append(linie.name)

                # Verbindung b → a (beide Richtungen!)
                if a not in b.nachbarn:
                    b.nachbarn[a] = Verbindung(b, a, fahrtzeit, [linie.name])
                elif linie.name not in b.nachbarn[a].linien:
                    b.nachbarn[a].linien.append(linie.name)

    def _setze_haltezeiten(self, linien_daten):
        """Setzt Haltezeiten automatisch anhand Station-Eigenschaften pro Linie.

        Bei Stationen auf mehreren Linien gewinnt der größte Wert (max).
        """
        for linie_info in linien_daten:
            linie = self.get_linie(linie_info["name"])
            for station in linie.stationen:
                if station.ist_endhaltestelle:
                    station.haltezeit = max(
                        station.haltezeit,
                        linie_info["haltezeit_end"]
                    )
                elif len(station.linien) >= 3:
                    station.haltezeit = max(
                        station.haltezeit,
                        linie_info["haltezeit_umstieg"]
                    )
                else:
                    station.haltezeit = max(
                        station.haltezeit,
                        linie_info["haltezeit_standard"]
                    )

    def _setze_umstiegszeiten(self, umstiegszeiten):
        """Setzt Mindestumstiegszeiten automatisch anhand der Linienanzahl.

        Hauptknoten (3+ Linien): z.B. Hauptbahnhof, Plärrer → längere Pufferzeit
        Knoten       (2 Linien): alle anderen Umstiegsstationen → kürzere Pufferzeit

        Args:
            umstiegszeiten: {"hauptknoten": int, "knoten": int}  — Werte in Minuten
        """
        for station in self.stationen.values():
            if station.ist_umsteigestation:
                if len(station.linien) >= 3:
                    station.min_umstiegszeit = umstiegszeiten["hauptknoten"]
                else:
                    station.min_umstiegszeit = umstiegszeiten["knoten"]


    # PUBLIC: Graph nutzen

    def get_station(self, name):
        """Findet Station-Objekt anhand Namen (case-insensitive)."""
        for station_name, station in self.stationen.items():
            if station_name.lower() == name.lower():
                return station
        return None

    def get_linie(self, name):
        """Findet Linie-Objekt anhand Namen."""
        for linie in self.linien:
            if linie.name == name:
                return linie
        return None

    def finde_route(self, start_name, ziel_name):
        """Findet optimale Route: wenigste Umstiege, bei Gleichstand kürzeste Strecke.

        Returns:
            Route-Objekt oder None
        """
        start = self.get_station(start_name)
        ziel  = self.get_station(ziel_name)

        if not start or not ziel:
            return None

        alle_pfade = self._dfs(start, ziel, [], None, [])

        if not alle_pfade:
            return None

        bester_pfad = min(alle_pfade, key=lambda p: (self._zaehle_umstiege(p), len(p)))
        return Route(bester_pfad)

    def finde_alle_routen(self, start_name, ziel_name):
        """Gibt alle möglichen Routen zurück — ZugManager entscheidet welche beste ist.

        Args:
            start_name: STRING - Name der Startstation
            ziel_name:  STRING - Name der Zielstation

        Returns:
            LIST[Route] - alle gefundenen Routen, oder []
        """
        start = self.get_station(start_name)
        ziel  = self.get_station(ziel_name)

        if not start or not ziel:
            return []

        alle_pfade = self._dfs(start, ziel, [], None, [])
        return [Route(pfad) for pfad in alle_pfade]

    def _zaehle_umstiege(self, pfad):
        """Zählt Linienwechsel in einem (Station, Linie) Pfad."""
        return sum(
            1 for i in range(2, len(pfad))
            if pfad[i][1] != pfad[i - 1][1]
        )

    def _dfs(self, aktuell, ziel, pfad, aktuelle_linie, ergebnis):
        """Linienbewusste Tiefensuche — speichert (Station, Linie) Paare.

        Die Linie im Tupel gibt an mit welcher Linie man ZU dieser Station kam.
        Start-Station bekommt None da noch keine Linie genutzt wurde.

        Args:
            aktuell:        aktuelle Station
            ziel:           Ziel-Station
            pfad:           bisheriger Pfad als [(Station, linie_name)]
            aktuelle_linie: Linie mit der wir zur aktuellen Station gefahren sind
            ergebnis:       Liste aller gefundenen Pfade

        Returns:
            LIST of [(Station, linie_name)]
        """
        pfad = pfad + [(aktuell, aktuelle_linie)]

        if aktuell == ziel:
            ergebnis.append(pfad)
            return ergebnis

        besuchte = {station for station, linie in pfad}

        for nachbar, verbindung in aktuell.nachbarn.items():
            if nachbar in besuchte:
                continue
            for linie_name in verbindung.linien:
                self._dfs(nachbar, ziel, pfad, linie_name, ergebnis)

        return ergebnis


# ==============================================================================
# Test

if __name__ == "__main__":

    import daten

    linien_daten = [
        {
            "name":               "U1",
            "stationen":          daten.linie1_stationen,
            "fahrtzeiten":        daten.linie1_fahrtzeiten,
            "haltezeit_end":      daten.linie1_haltezeit_endstation,
            "haltezeit_umstieg":  daten.linie1_haltezeit_umstieg,
            "haltezeit_standard": daten.linie1_haltezeit_standard,
        },
        {
            "name":               "U2",
            "stationen":          daten.linie2_stationen,
            "fahrtzeiten":        daten.linie2_fahrtzeiten,
            "haltezeit_end":      daten.linie2_haltezeit_endstation,
            "haltezeit_umstieg":  daten.linie2_haltezeit_umstieg,
            "haltezeit_standard": daten.linie2_haltezeit_standard,
        },
        {
            "name":               "U3",
            "stationen":          daten.linie3_stationen,
            "fahrtzeiten":        daten.linie3_fahrtzeiten,
            "haltezeit_end":      daten.linie3_haltezeit_endstation,
            "haltezeit_umstieg":  daten.linie3_haltezeit_umstieg,
            "haltezeit_standard": daten.linie3_haltezeit_standard,
        },
    ]
    netz = Netzwerk(linien_daten)

    # Umsteigestationen ausgeben
    print("Umsteigestationen:")
    for station in netz.stationen.values():
        if station.ist_umsteigestation:
            print(f"  {station.name} → {station.linien}")
    print()

    # Route suchen
    start_name = input("Start-Station: ").strip()
    ziel_name  = input("Ziel-Station:  ").strip()

    route = netz.finde_route(start_name, ziel_name)

    if not route:
        print("Keine Route gefunden.")
    else:
        print(f"Route:     {route}")
        print(f"Stationen: {len(route) - 1}")

        umstieg = route.get_umstiegestationen()
        if umstieg:
            print(f"Umstieg:   {', '.join(s.name for s in umstieg)}")

        print("\nSegmente:")
        for linie_name, stationen in route.get_segmente():
            print(f"  {linie_name}: {stationen[0].name} → {stationen[-1].name}")