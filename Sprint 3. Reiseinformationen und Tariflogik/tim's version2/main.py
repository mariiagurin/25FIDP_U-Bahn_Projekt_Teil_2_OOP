import daten
from netzwerk import Netzwerk
from fahrplan import ZugManager
from eingabe_validator import EingabeValidator
from tarif import Tarif, Ticket


if __name__ == "__main__":

    # 1. Netzwerk erstellen
    linien_daten = linien_daten = [
    {
        "name": "U1",
        "stationen": daten.linie1_stationen,
        "fahrtzeiten": daten.linie1_fahrtzeiten 
    }
]
    netz = Netzwerk(linien_daten)
    netz.setze_haltezeiten(daten.haltezeiten_speziell)

    # 2. ZugManager erstellen
    # fahrtzeiten_daten = {
    #     "U1": daten.linie1_fahrtzeiten
    # }
    betrieb_daten = {
        "U1": {
            "start": daten.linie1_betrieb_start,
            "ende": daten.linie1_betrieb_ende,
            "takt": daten.linie1_takt
        }
    }
    zugmanager = ZugManager(netz, betrieb_daten)

    # 3. Validator und Tarif erstellen
    validator = EingabeValidator(netz)
    tarif = Tarif()

    
    # 4. Start / Ziel eingeben

    while True:
        start = validator.eingabe_station("Start-Station: ")
        ziel = validator.eingabe_station("Ziel-Station: ")

        route = netz.finde_route(start.name, ziel.name)

        if route:
            break
        else:
            print("\nKeine Route gefunden! Bitte andere Stationen wählen.\n")

    
    # 5. Wunschzeit eingeben

    wunschzeit_obj = validator.frage_wunschzeit()
    wunschzeit = wunschzeit_obj.strftime("%H:%M")

   
    # 6. Nächsten Zug finden

    ergebnis = zugmanager.finde_naechsten_zug(start, ziel, wunschzeit)

    if not ergebnis:
        print("\nKein Zug mehr heute!")

    else:
        zug, abfahrt, ankunft = ergebnis

        
        # 7. Ticket-Informationen abfragen
        
        ist_mehrticket = validator.frage_einzel_mehrticket()
        hat_sozialrabatt = validator.frage_sozialrabatt()
        ist_bar = validator.frage_zahlart()

        
        # 8. Preis berechnen

        anzahl_stationen = len(route) - 1
        ticket = Ticket(
            anzahl_stationen,
            ist_mehrfahrt=ist_mehrticket,
            hat_sozialrabatt=hat_sozialrabatt,
            ist_barzahlung=ist_bar
        )
        preis = tarif.berechne_preis(ticket)

        # 9. Ausgabe
        
        print(f"Route:      {' -> '.join(s.name for s in route)}")
        print(f"Stationen:  {anzahl_stationen}")
        print(f"Abfahrt:    {abfahrt.strftime('%H:%M:%S')} Uhr")
        print(f"Ankunft:    {ankunft.strftime('%H:%M:%S')} Uhr")
        print(f"Preis:      {preis:.2f} €")