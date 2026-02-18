# ==============================================================================
# netzwerk.py - Graph und Routing
# ==============================================================================


# ==============================================================================
# KLASSE: Verbindung
# ==============================================================================

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
        self.von = von
        self.nach = nach
        self.fahrtzeit = fahrtzeit      # Minuten
        self.linien = linien or []
    
    def __str__(self):
        return f"Verbindung({self.von} -> {self.nach}, {self.fahrtzeit} min)"
    
    def __repr__(self):
        return self.__str__()


# ==============================================================================
# KLASSE: Station
# ==============================================================================

class Station:
    """Repräsentiert eine Haltestelle im U-Bahn-Netz.
    
    Wird gefüllt durch _baue_graph() in Netzwerk:
    - name gesetzt (aus daten.py)
    - linien gefüllt
    - ist_endhaltestelle gesetzt
    - nachbarn verbunden (als Verbindung-Objekte!)
    """
    
    def __init__(self, name):
        self.name = name
        self.linien = []             # ["U1", "U2", ...]
        self.nachbarn = {}           # {Station: Verbindung-Objekt}
        self.ist_endhaltestelle = False
        self.haltezeit = 30          # Sekunden, Standard 30
    
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
# ==============================================================================

class Linie:
    """Repräsentiert eine U-Bahn-Linie.
    
    Besteht aus Station-Objekten und Fahrtzeiten zwischen Stationen.
    
    Args:
        name:       STRING - Linienname z.B. "U1"
        stationen:  LIST[Station] - Station-Objekte in Reihenfolge
        fahrtzeiten: LIST[INT] - Minuten zwischen Stationen
    """
    
    def __init__(self, name, stationen, fahrtzeiten):
        self.name = name
        self.stationen = stationen      # [Station, Station, ...]
        self.fahrtzeiten = fahrtzeiten  # [3, 2, 2, ...]
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Linie({self.name})"


# ==============================================================================
# KLASSE: Netzwerk
# ==============================================================================

class Netzwerk:
    """Graph und Routing für das U-Bahn-Netz.
    
    Wird EINMAL erstellt. Graph wird sofort im __init__() gebaut.
    
    Args:
        linien_daten: Liste von Dictionaries:
        [
            {
                "name": "U1",
                "stationen":  ["Langwasser Süd", ...],
                "fahrtzeiten": [3, 2, 2, ...]
            },
            ...
        ]
    """
    
    def __init__(self, linien_daten):
        self.stationen = {}   # {name: Station-Objekt}
        self.linien = []      # [Linie-Objekt, ...]
        self._baue_graph(linien_daten)
    
    # ==========================================================================
    # PRIVATE: Graph bauen (nur 1x beim Start)
    # ==========================================================================
    
    def _baue_graph(self, linien_daten):
        """Baut den Graph auf."""
        self._stationen_erstellen(linien_daten)
        self._linien_erstellen(linien_daten)
        self._linien_zuweisen()
        self._endhaltestellen_markieren()
        self._stationen_verbinden()
    
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
                a = linie.stationen[i]
                b = linie.stationen[i + 1]
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
    
    # ==========================================================================
    # PUBLIC: Graph nutzen
    # ==========================================================================
    
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
    
    def setze_haltezeiten(self, haltezeiten_speziell):
        """Setzt Haltezeiten für spezielle Stationen.
        
        Args:
            haltezeiten_speziell: DICT {name: sekunden}
        """
        for name, zeit in haltezeiten_speziell.items():
            station = self.get_station(name)
            if station:
                station.haltezeit = zeit
    
    def finde_route(self, start_name, ziel_name):
        """Findet kürzeste Route zwischen zwei Stationen (DFS)."""
        start = self.get_station(start_name)
        ziel  = self.get_station(ziel_name)
        
        if not start or not ziel:
            return None
        
        alle_pfade = self._dfs(start, ziel, [], [])
        
        if not alle_pfade:
            return None
        
        return min(alle_pfade, key=len)
    
    def _dfs(self, aktuell, ziel, pfad, ergebnis):
        """Tiefensuche - findet ALLE Pfade rekursiv."""
        pfad = pfad + [aktuell]
        
        if aktuell == ziel:
            ergebnis.append(pfad.copy())
            return ergebnis
        
        for nachbar in aktuell.nachbarn:
            if nachbar not in pfad:
                self._dfs(nachbar, ziel, pfad, ergebnis)
        
        return ergebnis


# ==============================================================================
# Test

if __name__ == "__main__":

    import daten

    linien_daten = [
        {
            "name": "U1",
            "stationen": daten.linie1_stationen,
            "fahrtzeiten": daten.linie1_fahrtzeiten
        }
    ]

    netz = Netzwerk(linien_daten)
    netz.setze_haltezeiten(daten.haltezeiten_speziell)

    # Verbindung prüfen
    messe    = netz.get_station("Messe")
    hasenbuck = netz.get_station("Bauernfeindstraße")
    print(f"Verbindung: {messe.nachbarn[hasenbuck]}")

    # Route prüfen
    route = netz.finde_route("Messe", "Plärrer")
    print(" -> ".join(str(s) for s in route))