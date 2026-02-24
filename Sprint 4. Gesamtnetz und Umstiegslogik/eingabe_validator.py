from datetime import datetime
from difflib import get_close_matches


# ==============================================================================
# BASISKLASSE: Frage

class Frage:
    """Basisklasse für alle Benutzereingaben.

    Jede Unterklasse überschreibt nur validiere() mit eigener Logik.
    stellen() ist immer gleich: input → normalisieren → validieren → loop.

    Args:
        prompt:        Anzeigetext für den Benutzer
        fehlermeldung: Text wenn Eingabe ungültig
    """

    def __init__(self, prompt, fehlermeldung):
        self.prompt        = prompt
        self.fehlermeldung = fehlermeldung

    def stellen(self):
        """Fragt den Benutzer und wiederholt bis Eingabe gültig.

        Returns:
            Ergebnis von validiere() — Typ je nach Unterklasse
        """
        while True:
            eingabe  = input(self.prompt)
            norm     = self._normalisiere(eingabe)
            ergebnis = self.validiere(norm)

            if ergebnis is not None:
                return ergebnis

            print(self.fehlermeldung)

    def validiere(self, eingabe):
        """Validiert die normalisierte Eingabe.

        Wird von jeder Unterklasse überschrieben (Polymorphie!).

        Args:
            eingabe: normalisierter Eingabe-String

        Returns:
            Ergebnis wenn gültig, None wenn ungültig
        """
        raise NotImplementedError

    def _normalisiere(self, eingabe):
        """Normalisiert Eingabe: strip, lower, Umlaute ersetzen."""
        eingabe = eingabe.strip().lower()
        eingabe = eingabe.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        return eingabe

    def _finde_fuzzy_match(self, eingabe, optionen, schwelle=0.8):
        """Findet besten Fuzzy-Match in Optionsliste."""
        matches = get_close_matches(eingabe, optionen, n=1, cutoff=schwelle)
        return matches[0] if matches else None


# ==============================================================================
# UNTERKLASSE: StationFrage

class StationFrage(Frage):
    """Fragt nach einer Station mit Fuzzy-Matching und Kürzel-Erkennung.

    Args:
        netzwerk: Netzwerk-Objekt für Stationssuche
        prompt:   Anzeigetext
    """

    KUERZEL = {
        "hbf":        "hauptbahnhof",
        "hbf.":       "hauptbahnhof",
        "str":        "strasse",
        "str.":       "strasse",
        "fuerth hbf": "fuerth hauptbahnhof",
    }

    def __init__(self, netzwerk, prompt):
        super().__init__(prompt, "Station nicht gefunden. Bitte erneut eingeben.\n")
        self.netzwerk = netzwerk

    def validiere(self, eingabe):
        """Sucht Station per Fuzzy-Match. Gibt Station-Objekt oder None zurück."""
        norm = self.KUERZEL.get(eingabe, eingabe)

        alle_stationen   = list(self.netzwerk.stationen.keys())
        norm_zu_original = {
            self.KUERZEL.get(self._normalisiere(s), self._normalisiere(s)): s
            for s in alle_stationen
        }

        match = self._finde_fuzzy_match(norm, list(norm_zu_original.keys()))
        if not match:
            return None

        return self.netzwerk.get_station(norm_zu_original[match])


# ==============================================================================
# UNTERKLASSE: ZeitFrage

class ZeitFrage(Frage):
    """Fragt nach einer Uhrzeit — akzeptiert flexible Formate.

    Akzeptiert (US 4.4):
        "08:15"  → 08:15    (Standard)
        "8:15"   → 08:15    (einstellige Stunde)
        "8:5"    → 08:05    (einstellige Minute)
        "08.15"  → 08:15    (Punkt als Trennzeichen)
        "08,15"  → 08:15    (Komma als Trennzeichen)
        "08 15"  → 08:15    (Leerzeichen als Trennzeichen)
        "0815"   → 08:15    (ohne Trenner)
        "815"    → 08:15    (ohne Trenner, einstellige Stunde)
        "8"      → 08:00    (nur Stunde)
    """

    def __init__(self):
        super().__init__(
            "Wann moechten Sie fahren? (HH:MM): ",
            "Ungueltiges Zeitformat. Bitte z.B. 08:15 oder 815 eingeben."
        )

    def validiere(self, eingabe):
        """Parst Zeitstring flexibel. Gibt datetime oder None zurueck."""

        # Fall 1: Mit Trennzeichen : . , oder Leerzeichen
        for trennzeichen in [":", ".", ",", " "]:
            if trennzeichen in eingabe:
                teile   = eingabe.split(trennzeichen)
                stunden = int(teile[0])
                minuten = int(teile[1]) if teile[1] else 0
                return self._baue_zeit(stunden, minuten)

        # Fall 2: Nur Ziffern — ohne Trennzeichen
        if eingabe.isdigit():
            if len(eingabe) <= 2:       # "8" oder "08" → 08:00
                return self._baue_zeit(int(eingabe), 0)
            elif len(eingabe) == 3:     # "815" → 8:15
                return self._baue_zeit(int(eingabe[0]), int(eingabe[1:]))
            else:                       # "0815" → 08:15
                return self._baue_zeit(int(eingabe[:2]), int(eingabe[2:]))

        return None

    def _baue_zeit(self, stunden, minuten):
        """Validiert Stunden/Minuten und baut datetime (00:00 bis 23:59)."""
        if 0 <= stunden <= 23 and 0 <= minuten <= 59:
            return datetime(1900, 1, 1, stunden, minuten)
        return None


# ==============================================================================
# UNTERKLASSE: AuswahlFrage

class AuswahlFrage(Frage):
    """Fragt nach einer Auswahl aus vorgegebenen Optionen per Fuzzy-Match.

    Args:
        prompt:    Anzeigetext
        optionen:  Dict {norm_option: rückgabewert}
                   z.B. {"einzelticket": False, "einzel": False,
                          "mehrticket": True,   "mehr":   True}
    """

    def __init__(self, prompt, fehlermeldung, optionen):
        super().__init__(prompt, fehlermeldung)
        self.optionen = optionen   # {option_string: rückgabewert}

    def validiere(self, eingabe):
        """Fuzzy-Match gegen Optionen. Gibt Rückgabewert oder None zurück."""
        match = self._finde_fuzzy_match(eingabe, list(self.optionen.keys()))
        if not match:
            return None
        return self.optionen[match]


# ==============================================================================
# KLASSE: EingabeValidator

class EingabeValidator:
    """Stellt alle Benutzerfragen für den Ticketautomaten.

    Nutzt Frage-Unterklassen — jede Frage kennt ihre eigene Validierungslogik.

    Args:
        netzwerk: Netzwerk-Objekt für Stationssuche
    """

    def __init__(self, netzwerk):
        self.netzwerk = netzwerk

    def eingabe_station(self, prompt):
        """Fragt nach einer Station.

        Returns:
            Station-Objekt
        """
        return StationFrage(self.netzwerk, prompt).stellen()

    def frage_wunschzeit(self):
        """Fragt nach der Wunschzeit.

        Returns:
            datetime-Objekt
        """
        return ZeitFrage().stellen()

    def parse_zeit(self, eingabe):
        """Parst Zeitstring ohne input() — für Adapter nutzbar.

        Args:
            eingabe: Zeitstring "HH:MM"

        Returns:
            String "HH:MM"

        Raises:
            ValueError: wenn Format ungültig
        """
        frage    = ZeitFrage()
        norm     = frage._normalisiere(eingabe)
        ergebnis = frage.validiere(norm)

        if not ergebnis:
            raise ValueError(f"Ungültiges Zeitformat: '{eingabe}'")

        return ergebnis.strftime("%H:%M")

    def frage_einzel_mehrticket(self):
        """Fragt nach Einzelticket oder Mehrfahrtenticket.

        Returns:
            False = Einzelticket, True = Mehrfahrtenticket
        """
        return AuswahlFrage(
            prompt        = "Möchten Sie ein Einzelticket oder Mehrticket? (einzelticket/mehrticket): ",
            fehlermeldung = "Ungültige Eingabe. Bitte 'einzelticket' oder 'mehrticket' eingeben.",
            optionen      = {
                "einzelticket": False,
                "einzel":       False,
                "mehrticket":   True,
                "mehr":         True,
            }
        ).stellen()

    def frage_sozialrabatt(self):
        """Fragt nach Sozialrabatt.

        Returns:
            True = Rabatt, False = kein Rabatt
        """
        return AuswahlFrage(
            prompt        = "Haben Sie Anspruch auf Sozialrabatt? (ja/nein): ",
            fehlermeldung = "Ungültige Eingabe. Bitte 'ja' oder 'nein' eingeben.",
            optionen      = {
                "ja":   True,
                "nein": False,
            }
        ).stellen()

    def frage_zahlart(self):
        """Fragt nach Zahlungsart.

        Returns:
            False = Kartenzahlung, True = Barzahlung
        """
        return AuswahlFrage(
            prompt        = "Möchten Sie mit Karte oder Bar bezahlen? (karte/bar): ",
            fehlermeldung = "Ungültige Eingabe. Bitte 'karte' oder 'bar' eingeben.",
            optionen      = {
                "kartenzahlung": False,
                "karte":         False,
                "barzahlung":    True,
                "bar":           True,
            }
        ).stellen()


# ==============================================================================
if __name__ == "__main__":

    import daten
    from netzwerk import Netzwerk

    linien_daten = [
        {
            "name":               "U1",
            "stationen":          daten.linie1_stationen,
            "fahrtzeiten":        daten.linie1_fahrtzeiten,
            "haltezeit_end":      daten.linie1_haltezeit_endstation,
            "haltezeit_umstieg":  daten.linie1_haltezeit_umstieg,
            "haltezeit_standard": daten.linie1_haltezeit_standard,
        },
    ]
    netz      = Netzwerk(linien_daten)
    validator = EingabeValidator(netz)

    # print("\n--- Station ---")
    # station = validator.eingabe_station("Station: ")
    # print(f">>> Gefunden: {station.name}")

    print("\n--- Wunschzeit ---")
    zeit = validator.frage_wunschzeit()
    print(f">>> Gefunden: {zeit.strftime('%H:%M')}")

    # print("\n--- Ticketart ---")
    # ist_mehrticket = validator.frage_einzel_mehrticket()
    # print(f">>> Mehrticket: {ist_mehrticket}")

    # print("\n--- Sozialrabatt ---")
    # hat_rabatt = validator.frage_sozialrabatt()
    # print(f">>> Sozialrabatt: {hat_rabatt}")

    # print("\n--- Zahlart ---")
    # ist_bar = validator.frage_zahlart()
    # print(f">>> Barzahlung: {ist_bar}")