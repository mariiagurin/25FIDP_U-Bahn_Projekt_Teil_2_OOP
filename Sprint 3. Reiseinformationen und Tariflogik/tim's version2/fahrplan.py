from datetime import datetime, timedelta


# ==============================================================================
# KLASSE: Zug
# ==============================================================================

class Zug:
    """Repräsentiert einen einzelnen Zug als kompletten Umlauf (Hin + Rück).
    
    Holt Fahrtzeiten direkt aus dem Graph (Verbindung-Objekte).
    Kein fahrtzeiten-Parameter mehr nötig!
    
    Args:
        linie:     Linie-Objekt
        startzeit: datetime - wann fährt er an stationen[0] ab
        stationen: LIST[Station] - kompletter Umlauf [A...Z...A]
    """
    
    def __init__(self, linie, startzeit, stationen):
        self.linie = linie
        self.startzeit = startzeit  # datetime
        self.stationen = stationen  # kompletter Umlauf [A...Z...A]
    
    def get_abfahrt(self, station, ab_idx=0):
        """Wann fährt dieser Zug an der Station ab?
        
        Fahrtzeiten werden direkt aus station.nachbarn[nach].fahrtzeit geholt!
        
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
            
            # Fahrtzeit aus Graph holen!
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
        
        # Erste Station: Ankunft = Abfahrt
        if idx == 0:
            return abfahrt
        
        return abfahrt - timedelta(seconds=station.haltezeit)
    
    def __str__(self):
        return f"Zug({self.linie.name}, {self.startzeit.strftime('%H:%M')})"
    
    def __repr__(self):
        return self.__str__()


# ==============================================================================
# KLASSE: ZugManager
# ==============================================================================

class ZugManager:
    """Erstellt alle Züge für einen Tag und findet passende Verbindungen.
    
    Kein fahrtzeiten_daten Parameter mehr - Fahrtzeiten kommen aus dem Graph!
    
    Args:
        netzwerk:     Netzwerk-Objekt
        betrieb_daten: {linie_name: {"start": "05:00", "ende": "23:00", "takt": 10}}
    """
    
    def __init__(self, netzwerk, betrieb_daten):
        self.netzwerk = netzwerk
        self.zuege = []
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
    
    def finde_naechsten_zug(self, start, ziel, wunschzeit):
        """Findet nächsten Zug nach Wunschzeit von Start nach Ziel.
        
        Args:
            start:      Station-Objekt
            ziel:       Station-Objekt
            wunschzeit: STRING "08:30"
            
        Returns:
            (zug, abfahrt, ankunft) oder None
        """
        wunsch_dt = datetime.strptime(wunschzeit, "%H:%M")
        
        for zug in self.zuege:
            
            if start not in zug.stationen:
                continue
            if ziel not in zug.stationen:
                continue
            
            # Start-Abfahrt finden
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
    from netzwerk import Netzwerk

    linien_daten = [
        {
            "name": "U1",
            "stationen": daten.linie1_stationen,
            "fahrtzeiten": daten.linie1_fahrtzeiten
        }
    ]
    netz = Netzwerk(linien_daten)
    netz.setze_haltezeiten(daten.haltezeiten_speziell)

    # Kein fahrtzeiten_daten mehr!
    betrieb_daten = {
        "U1": {
            "start": daten.linie1_betrieb_start,
            "ende":  daten.linie1_betrieb_ende,
            "takt":  daten.linie1_takt
        }
    }
    manager = ZugManager(netz, betrieb_daten)
    print(f"Züge erstellt: {len(manager.zuege)}")
    print()

    testfaelle = [
        (1, "Langwasser Süd", "Fürth Hbf.",  "04:30", "05:00", "05:59:30"),
        (2, "Hauptbahnhof",   "Plärrer",      "08:02", "08:10", "08:18:00"),
        (3, "Fürth Hbf.",     "Stadtgrenze",  "05:45", "06:00", "06:06:00"),
        (4, "Maffeiplatz",    "Aufseßplatz",  "08:35", "08:35", "08:36:30"),
        (5, "Gostenhof",      "Eberhardshof", "23:36", "23:41", "23:47:30"),
    ]

    for nr, s_name, z_name, wunsch, erw_abfahrt, erw_ankunft in testfaelle:
        start = netz.get_station(s_name)
        ziel  = netz.get_station(z_name)
        ergebnis = manager.finde_naechsten_zug(start, ziel, wunsch)
        
        if ergebnis:
            zug, abfahrt, ankunft = ergebnis
            ok_ab = abfahrt.strftime("%H:%M")    == erw_abfahrt
            ok_an = ankunft.strftime("%H:%M:%S") == erw_ankunft
            status = "erfolgreich" if (ok_ab and ok_an) else "fehler"
            print(f"{status} Test {nr}: Abfahrt {abfahrt.strftime('%H:%M')} (erw: {erw_abfahrt})  "
                  f"Ankunft {ankunft.strftime('%H:%M:%S')} (erw: {erw_ankunft})")
        else:
            print(f"Test {nr}: Kein Zug gefunden!")