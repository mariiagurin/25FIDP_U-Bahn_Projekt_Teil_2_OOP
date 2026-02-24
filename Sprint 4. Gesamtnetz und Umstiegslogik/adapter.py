from datetime import datetime, time, timedelta
from typing import List, Dict, Union

import daten
from netzwerk import Netzwerk
from fahrplan import ZugManager
from tarif import Tarif, Ticket
from eingabe_validator import EingabeValidator


class adapter_klasse:

    def __init__(self):
        """Netzwerk, ZugManager, Tarif und Validator einmalig aufbauen."""

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
        umstiegszeiten = {
            "hauptknoten": daten.umstiegszeit_hauptknoten,   # 5 min (3+ Linien)
            "knoten":      daten.umstiegszeit_knoten,        # 3 min (2 Linien)
        }
        self.netzwerk  = Netzwerk(linien_daten, umstiegszeiten)
        self.validator = EingabeValidator(self.netzwerk)

        betrieb_daten = {
            "U1": {"start": daten.linie1_betrieb_start, "ende": daten.linie1_betrieb_ende, "takt": daten.linie1_takt},
            "U2": {"start": daten.linie2_betrieb_start, "ende": daten.linie2_betrieb_ende, "takt": daten.linie2_takt},
            "U3": {"start": daten.linie3_betrieb_start, "ende": daten.linie3_betrieb_ende, "takt": daten.linie3_takt},
        }
        self.zugmanager = ZugManager(self.netzwerk, betrieb_daten)
        self.tarif      = Tarif()

    def _runde(self, dt):
        """Rundet datetime auf nächste volle Minute (für Fahrgast-Anzeige).

        Args:
            dt: datetime-Objekt

        Returns:
            time-Objekt gerundet auf volle Minute
        """
        if dt.second > 0:
            dt += timedelta(minutes=1)
        return dt.replace(second=0).time()

    def ausfuehren_testfall(self,
                            eingabe_start:            str,
                            eingabe_ziel:             str,
                            eingabe_startzeit:        str,
                            eingabe_einzelfahrkarte:  bool,
                            eingabe_sozialrabatt:     bool,
                            eingabe_barzahlung:       bool) -> dict:

        # Fehler-Rückgabe als Standardwert
        fehler_rueckgabe = {
            "fehler":                      True,
            "ausgabe_startzeit_fahrgast":  time(0, 0),
            "ausgabe_zielzeit_fahrgast":   time(0, 0),
            "ausgabe_startzeit_algo":      time(0, 0, 0),
            "ausgabe_zielzeit_algo":       time(0, 0, 0),
            "bahnlinien_gesamtfahrt":      [],
            "route":                       {},
            "umstieg_haltestellen":        [],
            "umstiege_exakt":              {},
            "umstiege_fahrgast":           {},
            "umstieg_bahnlinien":          [],
            "dauer_gesamtfahrt":           timedelta(0),
            "preis_endbetrag":             0.0,
        }

        # --- INTERNE VERARBEITUNG ---

        # 1. Zeit parsen
        try:
            wunschzeit = self.validator.parse_zeit(eingabe_startzeit)
        except ValueError:
            return fehler_rueckgabe

        # 2. Beste Fahrt finden (wenigste Umstiege → früheste Ankunft)
        route, fahrten = self.zugmanager.finde_beste_fahrt(eingabe_start, eingabe_ziel, wunschzeit)
        if not route or not fahrten:
            return fehler_rueckgabe

        # 3. Ticket und Preis
        ticket = Ticket(
            anzahl_stationen = len(route) - 1,
            ist_mehrfahrt    = not eingabe_einzelfahrkarte,  # invertiert!
            hat_sozialrabatt = eingabe_sozialrabatt,
            ist_barzahlung   = eingabe_barzahlung,
        )
        preis = self.tarif.berechne_preis(ticket)

        # --- ERGEBNIS WANDELN ---

        erste_abfahrt  = fahrten[0][2]    # (linie, zug, abfahrt, ankunft) → Index 2
        letzte_ankunft = fahrten[-1][3]   # letztes Segment → Index 3

        segmente          = route.get_segmente()
        bahnlinien        = [linie_name for linie_name, _ in segmente]
        umstieg_linien    = [linie_name for linie_name, _ in segmente[1:]]
        umstieg_stationen = route.get_umstiegestationen()

        # route als Dict: {"Stationsname": [Linie, An_HHMMSS, Ab_HHMMSS], ...}
        route_dict = {}
        for i, (linie_name, seg_stationen) in enumerate(segmente):
            _, zug, _, _ = fahrten[i]
            for station in seg_stationen:
                ab_result = zug.get_abfahrt(station)
                if not ab_result:
                    continue
                idx, abfahrt = ab_result
                ankunft      = zug.get_ankunft(station, idx)
                route_dict[station.name] = [
                    linie_name,
                    ankunft.strftime("%H:%M:%S"),
                    abfahrt.strftime("%H:%M:%S"),
                ]

        # umstiege: Ankunft Ende Segment i, Abfahrt Anfang Segment i+1
        umstiege_exakt    = {}
        umstiege_fahrgast = {}
        for i, station in enumerate(umstieg_stationen):
            ankunft_umstieg  = fahrten[i][3]       # Ankunft am Ende von Segment i
            abfahrt_umstieg  = fahrten[i + 1][2]   # Abfahrt am Anfang von Segment i+1
            umstiege_exakt[station.name]    = [ankunft_umstieg.time(),       abfahrt_umstieg.time()]
            umstiege_fahrgast[station.name] = [self._runde(ankunft_umstieg), self._runde(abfahrt_umstieg)]

        # --- RÜCKGABE ---
        return {
            "fehler":                      False,

            "ausgabe_startzeit_fahrgast":  erste_abfahrt.replace(second=0).time(),
            "ausgabe_zielzeit_fahrgast":   self._runde(letzte_ankunft),

            "ausgabe_startzeit_algo":      erste_abfahrt.time(),
            "ausgabe_zielzeit_algo":       letzte_ankunft.time(),

            "bahnlinien_gesamtfahrt":      bahnlinien,
            "route":                       route_dict,
            "umstieg_haltestellen":        [s.name for s in umstieg_stationen],
            "umstiege_exakt":              umstiege_exakt,
            "umstiege_fahrgast":           umstiege_fahrgast,
            "umstieg_bahnlinien":          umstieg_linien,
            "dauer_gesamtfahrt":           letzte_ankunft - erste_abfahrt,
            "preis_endbetrag":             preis,
        }


# ==============================================================================
if __name__ == "__main__":

    import openpyxl

    def _bereinige_station(name):
        if not name:
            return name
        return name.split(" (")[0].strip()

    def _zeit_gleich(ist, soll):
        if not ist or not soll:
            return False
        return ist.hour == soll.hour and ist.minute == soll.minute

    adapter    = adapter_klasse()
    wb         = openpyxl.load_workbook("/mnt/user-data/uploads/Testfälle_0_2.xlsx")
    ws         = wb["Tabelle1"]
    zeilen     = list(ws.iter_rows(values_only=True))
    testfaelle = zeilen[1:]

    bestanden = 0
    gesamt    = 0

    for zeile in testfaelle:
        if not zeile[0]:
            continue

        tf_id           = zeile[0]
        start           = _bereinige_station(zeile[1])
        ziel            = _bereinige_station(zeile[2])
        startzeit       = zeile[3].strftime("%H:%M") if zeile[3] else "00:00"
        erw_abfahrt     = zeile[6]
        erw_ankunft     = zeile[12]
        erw_umstieg     = zeile[7]
        erw_umstieg_alt = zeile[13]

        ergebnis = adapter.ausfuehren_testfall(
            eingabe_start           = start,
            eingabe_ziel            = ziel,
            eingabe_startzeit       = startzeit,
            eingabe_einzelfahrkarte = True,
            eingabe_sozialrabatt    = False,
            eingabe_barzahlung      = False,
        )

        fehler_liste = []

        if ergebnis["fehler"]:
            fehler_liste.append("fehler=True")
        else:
            if erw_abfahrt and not _zeit_gleich(ergebnis["ausgabe_startzeit_fahrgast"], erw_abfahrt):
                fehler_liste.append(f"Abfahrt: {ergebnis['ausgabe_startzeit_fahrgast']} ≠ erwartet {erw_abfahrt}")

            if erw_ankunft and not _zeit_gleich(ergebnis["ausgabe_zielzeit_fahrgast"], erw_ankunft):
                fehler_liste.append(f"Ankunft: {ergebnis['ausgabe_zielzeit_fahrgast']} ≠ erwartet {erw_ankunft}")

            if erw_umstieg and erw_umstieg != "Keine":
                umstieg_ok = (
                    erw_umstieg in ergebnis["umstieg_haltestellen"] or
                    (erw_umstieg_alt and erw_umstieg_alt in ergebnis["umstieg_haltestellen"])
                )
                if not umstieg_ok:
                    fehler_liste.append(f"Umstieg: {ergebnis['umstieg_haltestellen']} ≠ erwartet {erw_umstieg}")

        gesamt += 1
        if not fehler_liste:
            bestanden += 1
            print(f"✅ {tf_id}: {start} → {ziel}")
        else:
            print(f"❌ {tf_id}: {start} → {ziel}")
            for f in fehler_liste:
                print(f"     {f}")

    print()
    print(f"Ergebnis: {bestanden}/{gesamt} bestanden")