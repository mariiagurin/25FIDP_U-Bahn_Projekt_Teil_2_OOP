"""
Enthält die Klasse `Netzwerk`, welche ein Verkehrsnetz als Graph
modelliert und Routenberechnungen ermöglicht.
"""

class Netzwerk:
    """
    Repräsentiert ein Verkehrsnetz als ungerichteten Graphen.
    """

    def __init__(self):
        """Initialisiert ein leeres Netzwerk."""
        self.stationen = {}

    def baue_graph(self, linien, fahrzeiten_liste):
        """
        Baut den Graphen aus Linien und Fahrzeiten auf.
        """
        for linie, fahrtzeiten in zip(linien, fahrzeiten_liste):
            for i in range(len(linie) - 1):
                a = linie[i]
                b = linie[i + 1]
                fahrtzeit = fahrtzeiten[i]

                self.stationen.setdefault(a, {})
                self.stationen.setdefault(b, {})

                self.stationen[a][b] = {"fahrtzeit": fahrtzeit}
                self.stationen[b][a] = {"fahrtzeit": fahrtzeit}

    def nutzereingabe(self):
        """Fragt Start- und Zielstation vom Benutzer ab."""
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
        """Findet alle möglichen Pfade zwischen zwei Stationen."""
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
        """Gibt den kürzesten Pfad (nach Anzahl Stationen) zurück."""
        alle = self.finde_alle_pfade(start, ziel)
        return min(alle, key=len) if alle else []

    def berechne_fahrtzeit(self, pfad):
        """Berechnet die Gesamtfahrzeit eines Pfades in Minuten."""
        gesamt = 0
        for i in range(len(pfad) - 1):
            gesamt += self.stationen[pfad[i]][pfad[i + 1]]["fahrtzeit"]
        return gesamt

    def pruefe_richtung(self, pfad, linie):
        """True = Hinfahrt, False = Rückfahrt."""
        if len(pfad) < 2:
            return True
        return linie.index(pfad[1]) > linie.index(pfad[0])
