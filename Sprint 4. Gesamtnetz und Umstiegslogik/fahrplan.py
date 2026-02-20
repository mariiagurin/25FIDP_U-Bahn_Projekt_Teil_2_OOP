from datetime import datetime, timedelta
from netzwerk import Netzwerk


# ==============================================================================
# KLASSE: Zug

class Zug:
    """Repräsentiert einen einzelnen Zug als kompletten Umlauf (Hin + Rück).

    Holt Fahrtzeiten direkt aus dem Graph (Verbindung-Objekte der Stationen).

    Args:
        linie:     Linie-Objekt
        startzeit: datetime - wann fährt er an stationen[0] ab
        stationen: LIST[Station] - kompletter Umlauf [A...Z...A]
    """

    def __init__(self, linie, startzeit, stationen):
        self.linie     = linie
        self.startzeit = startzeit   # datetime
        self.stationen = stationen   # Umlauf [A...Z...A]

    def get_abfahrt(self, station, ab_idx=0):
        """Wann fährt dieser Zug an der Station ab?

        Args:
            station: Station-Objekt
            ab_idx:  Ab welchem Index suchen (Standard: 0)

        Returns:
            (idx, datetime) oder None
        """
        zeit = self.startzeit

        for i in range(len(self.stationen)):
            if i >= ab_idx and self.stationen[i] == station:
                return (i, zeit)

            von  = self.stationen[i]
            nach = self.stationen[i + 1]

            verbindung = von.nachbarn[nach]
            zeit += timedelta(seconds=verbindung.fahrtzeit * 60)
            zeit += timedelta(seconds=nach.haltezeit)

        return None

    def get_ankunft(self, station, idx):
        """Wann kommt dieser Zug an der Station an?

        Ankunft = Abfahrt - haltezeit

        Args:
            station: Station-Objekt
            idx:     Index der Station im Umlauf

        Returns:
            datetime
        """
        _, abfahrt = self.get_abfahrt(station, idx)

        if idx == 0:
            return abfahrt

        return abfahrt - timedelta(seconds=station.haltezeit)

    def __str__(self):
        return f"Zug({self.linie.name}, {self.startzeit.strftime('%H:%M')})"

    def __repr__(self):
        return self.__str__()


# ==============================================================================
# KLASSE: ZugManager

class ZugManager:
    """Erstellt alle Züge für einen Tag und findet passende Verbindungen.

    Args:
        netzwerk:      Netzwerk-Objekt
        betrieb_daten: {linie_name: {"start": "05:00", "ende": "23:00", "takt": 10}}
    """

    def __init__(self, netzwerk, betrieb_daten):
        self.netzwerk = netzwerk
        self.zuege    = []
        self._erstelle_zuege(betrieb_daten)

    def _erstelle_zuege(self, betrieb_daten):
        """Erstellt alle Züge als Umläufe (Hin + Rück) für einen Tag."""
        for linie in self.netzwerk.linien:

            start_dt = datetime.strptime(betrieb_daten[linie.name]["start"], "%H:%M")
            ende_dt  = datetime.strptime(betrieb_daten[linie.name]["ende"],  "%H:%M")
            takt     = betrieb_daten[linie.name]["takt"]

            # Umlauf: A→Z→A (Endstation nicht doppelt!)
            stationen_umlauf = linie.stationen + linie.stationen[-2::-1]

            zug_zeit = start_dt
            while zug_zeit <= ende_dt:
                zug = Zug(linie, zug_zeit, stationen_umlauf)
                self.zuege.append(zug)
                zug_zeit += timedelta(minutes=takt)

    def finde_fahrten(self, route, wunschzeit):
        """Findet alle Züge für eine Route mit Umstiegen.

        Args:
            route:      Route-Objekt
            wunschzeit: STRING "08:30"

        Returns:
            LIST[(linie_name, zug, abfahrt, ankunft)] oder None
        """
        fahrten       = []
        naechste_zeit = wunschzeit

        for linie_name, seg_stationen in route.get_segmente():
            ergebnis = self.finde_naechsten_zug(
                seg_stationen[0],
                seg_stationen[-1],
                naechste_zeit,
                linie_name        # ← Linie direkt aus Route bekannt!
            )

            if not ergebnis:
                return None

            zug, abfahrt, ankunft = ergebnis
            fahrten.append((linie_name, zug, abfahrt, ankunft))
            naechste_zeit = ankunft.strftime("%H:%M")

        return fahrten

    def finde_naechsten_zug(self, start, ziel, wunschzeit, linie_name=None):
        """Findet nächsten Zug nach Wunschzeit von Start nach Ziel.

        Args:
            start:      Station-Objekt
            ziel:       Station-Objekt
            wunschzeit: STRING "08:30"
            linie_name: STRING optional - filtert direkt auf eine Linie

        Returns:
            (zug, abfahrt, ankunft) oder None
        """
        wunsch_dt = datetime.strptime(wunschzeit, "%H:%M")

        for zug in self.zuege:

            # Linie filtern wenn angegeben → kein falscher Zug möglich
            if linie_name and zug.linie.name != linie_name:
                continue

            start_result = zug.get_abfahrt(start)
            if not start_result:
                continue

            start_idx, abfahrt = start_result

            if abfahrt < wunsch_dt:
                continue

            # Ziel NACH Start suchen
            ziel_result = zug.get_abfahrt(ziel, start_idx + 1)
            if not ziel_result:
                continue

            ziel_idx, _ = ziel_result
            ankunft = zug.get_ankunft(ziel, ziel_idx)

            return (zug, abfahrt, ankunft)

        return None


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

    betrieb_daten = {
        "U1": {"start": daten.linie1_betrieb_start, "ende": daten.linie1_betrieb_ende, "takt": daten.linie1_takt},
        "U2": {"start": daten.linie2_betrieb_start, "ende": daten.linie2_betrieb_ende, "takt": daten.linie2_takt},
        "U3": {"start": daten.linie3_betrieb_start, "ende": daten.linie3_betrieb_ende, "takt": daten.linie3_takt},
    }
    manager = ZugManager(netz, betrieb_daten)
    print(f"Züge erstellt: {len(manager.zuege)}")
    print()

    start_name = input("Start-Station: ").strip()
    ziel_name  = input("Ziel-Station:  ").strip()
    wunschzeit = input("Wunschzeit (HH:MM): ").strip()

    route = netz.finde_route(start_name, ziel_name)

    if not route:
        print("Keine Route gefunden.")
    else:
        fahrten = manager.finde_fahrten(route, wunschzeit)

        if not fahrten:
            print("Kein Zug mehr heute!")
        else:
            for linie_name, zug, abfahrt, ankunft in fahrten:
                print(f"{linie_name}: {abfahrt.strftime('%H:%M:%S')} → {ankunft.strftime('%H:%M:%S')}")