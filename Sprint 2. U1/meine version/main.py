"""
Startpunkt des Fahrplan-Programms.
Initialisiert Netzwerk und Fahrplan und steuert die Benutzereingaben

"""

from netzwerk import Netzwerk
from fahrplan import Fahrplan
from Liniendaten import (
    linie1,
    fahrtzeiten1,
    linie1_startstation,
    linie1_betriebsstart,
    linie1_betriebsende,
    linie1_takt,
    linie1_haltezeiten,
    linie1_haltezeit_standard
)

def main():
    """Netzwerk aufbauen"""
    netz = Netzwerk()
    netz.baue_graph([linie1], [fahrtzeiten1])

    # Start & Ziel abfragen
    start, ziel = netz.nutzereingabe()

    # Route berechnen
    pfad = netz.finde_kuerzesten_pfad(start, ziel)
    route_info = {
        "pfad": pfad,
        "fahrtzeit": netz.berechne_fahrtzeit(pfad),
        "ist_hinfahrt": netz.pruefe_richtung(pfad, linie1),
    }

    # Ausgabe Route
    print("\nKürzester Pfad:")
    print(" -> ".join(pfad))
    print(f"Fahrtzeit: {route_info['fahrtzeit']} min")
    print("Richtung:", "Hinfahrt" if route_info["ist_hinfahrt"] else "Rückfahrt")

    # Fahrplan
    fahrplan = Fahrplan(
        netzwerk=netz,
        linie=linie1,
        fahrtzeiten=fahrtzeiten1,
        start_station=linie1_startstation,
        betrieb_start=linie1_betriebsstart,
        betrieb_ende=linie1_betriebsende,
        takt=linie1_takt,
        haltezeiten=linie1_haltezeiten,
        haltezeit_standard=linie1_haltezeit_standard,
        )

    wunschzeit = fahrplan.frage_wunschzeit()
    abfahrt = fahrplan.finde_naechste_abfahrt(route_info, wunschzeit)

    if abfahrt:
        print(f"Nächste Bahn ab {start}: {abfahrt} Uhr")
    else:
        print("Heute keine Bahn mehr.")


if __name__ == "__main__":
    main()
