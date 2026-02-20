from datetime import datetime
from difflib import get_close_matches

class EingabeValidator:
    """Klasse zur Validierung und Normalisierung von Benutzereingaben"""

    def __init__(self, netzwerk):
        """Initialisiert den Validator mit Netzwerk-Zugriff"""
        self.netzwerk = netzwerk

        # Kürzel-Mapping für die Ersetzung von häufigen Abkürzungen
        self.station_kuerzel = {
            "hbf": "hauptbahnhof",
            "hbf.": "hauptbahnhof",
            "str": "straße",
            "str.": "straße",
            "fr.": "Friedrich",
            "fuerth hbf.": "fuerth hauptbahnhof",
            "fuerth hbf": "fuerth hauptbahnhof",
        }
        
    # Hilfsfunktion

    # 1. normalisieren

    def _normalisiere(self, eingabe):
        """Normalisiert die Eingabe: entfernt Leerzeichen (strip), 
        konvertiert zu Kleinbuchstaben (lower) und entfernt Umlaute"""
        eingabe = eingabe.strip().lower()
        eingabe = eingabe.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        return eingabe
        
    # 2. fuzzy match

    def _finde_fuzzy_match(self, eingabe, optionen, schwelle=0.8):
        """Findet den besten Fuzzy-Match für die Eingabe in den Möglichkeiten
        
        Args:
            eingabe (str): Die Benutzereingabe
            optionen (list): Liste der gültigen Optionen
            schwelle (float): Mindestähnlichkeit für einen Match
            
        Returns:
            str oder None: Der beste Match oder None, 
            wenn kein Match über der Schwelle gefunden wurde"""
        
        matches = get_close_matches(eingabe, optionen, n=1, cutoff=schwelle)

        if matches:
            return matches[0]
        else:
            return None 
        
    # ersetze Kürzel durch vollständigen Namen

    def _ersetze_kuerzel(self, eingabe):
        """Ersetzt bekannte Kürzel durch vollständige Namen
        Args:
            eingabe (str): normalisierte eingabe
        
        Returns: str: Vollständiger Name oder unveränderte Eingabe, 
        wenn kein Kürzel gefunden wurde"""

        return self.station_kuerzel.get(eingabe, eingabe)


#==============================================================================
#==============================================================================

    # frage_station
    def eingabe_station(self, prompt):
        """Fragt den Benutzer nach der gewünschten Station und validiert die Eingabe
        
        Args:
            prompt (str): Anzeigetext für Start- oder Zielstation (z. B. "Start-Station: ")
            
        Returns: Station: gefundenes Station-Objekt aus dem Netzwerk"""
        
        while True:
            eingabe = input(prompt)
            norm = self._normalisiere(eingabe)
            norm = self._ersetze_kuerzel(norm)

            # alle Stationen aus Netzwerk holen
            alle_stationen = list(self.netzwerk.stationen.keys())
            
            # alle Stationen normalisieren und Kürzel ersetzen
            norm_zu_original = {
            self._ersetze_kuerzel(self._normalisiere(s)): s
            for s in alle_stationen}

            # Fuzzy-Match suchen
            match = self._finde_fuzzy_match(norm, list(norm_zu_original.keys()), 0.8)

            
            if match:
                original_name = norm_zu_original[match]  # ← Zurück zum Original!
                station = self.netzwerk.get_station(original_name)
                return station
            
            else:
                print("Station nicht gefunden. Bitte erneut eingeben.\n")
                
    # Wunschzeit
    def frage_wunschzeit(self):
        """Fragt den Benutzer nach der gewünschten Zeit für Abfahrt
        
        Returns:
            datetime.time: Die eingegebene Zeit als datetime-Objekt"""
        
        while True:
            eingabe = input("Wann möchten Sie fahren? (HH:MM): ")

            try:
                zeit = datetime.strptime(eingabe, "%H:%M")  # Validierung des Formats
                return zeit # datetime_objekt zurückgeben
            except ValueError:
                print("Ungültiges Zeitformat. Bitte geben Sie die Zeit im Format HH:MM ein.")

#==============================================================================

    # einzel/mehrticket
    def frage_einzel_mehrticket(self):
        """Fragt den Benutzer, ob er ein Einzelticket oder Mehrticket möchte
        
        Returns:
            bool: False für Einzelticket, True für Mehrfahrtenticket"""
        
        while True:
            eingabe = input("Möchten Sie ein Einzelticket oder Mehrticket? (einzelticket/mehrticket): ")
            norm = self._normalisiere(eingabe)
            optionen = ["einzelticket", "einzel", "mehrticket", "mehr"]

            match = self._finde_fuzzy_match(norm, optionen, 0.8)
            if not match:
                print("Ungültige Eingabe. Bitte geben Sie 'einzelticket' oder 'mehrticket' ein.")
                continue
        
            if match in ["einzelticket", "einzel"]:
                return False  # Einzelticket
            else:
                return True  # Mehrticket
#==============================================================================

    # Sozialrabatt
    def frage_sozialrabatt(self):
        """Fragt den Benutzer, ob er Anspruch auf Sozialrabatt hat
        
        Returns:
            Bool: True, wenn Anspruch auf Sozialrabatt besteht, sonst False"""
        
        while True:
            eingabe = input("Haben Sie Anspruch auf Sozialrabatt? (ja/nein): ")
            norm = self._normalisiere(eingabe)

            if norm == "ja": # alternativ ["ja", "yes", "y"] für mehr Flexibilität
                return True  # Sozialrabatt
            elif norm == "nein": # alternativ ["nein", "no", "n"] für mehr Flexibilität
                return False  # Kein Rabatt
            else:
                print("Ungültige Eingabe. Bitte geben Sie 'ja' oder 'nein' ein.")   

#==============================================================================

# Karte/Bar-Zahlung
    def frage_zahlart(self):
        """Fragt den Benutzer, ob er mit Karte oder Bar bezahlen möchte"""

        while True:
            eingabe = input("Möchten Sie mit Karte oder Bar bezahlen? (karte/bar): ")
            norm = self._normalisiere(eingabe)
            optionen = ["kartenzahlung", "karte", "barzahlung", "bar"]

            match = self._finde_fuzzy_match(norm, optionen, 0.8)
            if not match:
                print("Ungültige Eingabe. Bitte geben Sie 'karte' oder 'bar' ein.")
                continue
        
            if match in ["kartenzahlung", "karte"]:
                return False  # Kartenzahlung
            else:
                return True  # Barzahlung
            

#==============================================================================
if __name__ == "__main__":
    
    import daten
    from netzwerk import Netzwerk

    # Setup
    linien_daten = [{"name": "U1", "stationen": daten.linie1_stationen, "fahrtzeiten": daten.linie1_fahrtzeiten}]
    netz = Netzwerk(linien_daten)
    netz.setze_haltezeiten(daten.haltezeiten_speziell)
    validator = EingabeValidator(netz)

    # 1. Station
    print("\n--- Station ---")
    station = validator.eingabe_station("Station: ")
    print(f">>> Gefunden: {station.name}")

    # # 2. Wunschzeit
    # print("\n--- Wunschzeit ---")
    # zeit = validator.frage_wunschzeit()
    # print(f">>> Gefunden: {zeit.strftime('%H:%M')}")

    # # 3. Einzel / Mehrticket
    # print("\n--- Ticketart ---")
    # ist_mehrticket = validator.frage_einzel_mehrticket()
    # print(f">>> Mehrticket: {ist_mehrticket}")

    # # 4. Sozialrabatt
    # print("\n--- Sozialrabatt ---")
    # hat_rabatt = validator.frage_sozialrabatt()
    # print(f">>> Sozialrabatt: {hat_rabatt}")

    # # 5. Zahlart
    # print("\n--- Zahlart ---")
    # ist_bar = validator.frage_zahlart()
    # print(f">>> Barzahlung: {ist_bar}")