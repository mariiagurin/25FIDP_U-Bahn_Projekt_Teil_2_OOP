import daten
from netzwerk import Netzwerk
from fahrplan import ZugManager
from eingabe_validator import EingabeValidator
from tarif import Tarif, Ticket


if __name__ == "__main__":

    # 1. Netzwerk erstellen
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
    netz = Netzwerk(linien_daten, umstiegszeiten)

    # 2. ZugManager erstellen
    betrieb_daten = {
        "U1": {"start": daten.linie1_betrieb_start, "ende": daten.linie1_betrieb_ende, "takt": daten.linie1_takt},
        "U2": {"start": daten.linie2_betrieb_start, "ende": daten.linie2_betrieb_ende, "takt": daten.linie2_takt},
        "U3": {"start": daten.linie3_betrieb_start, "ende": daten.linie3_betrieb_ende, "takt": daten.linie3_takt},
    }
    zugmanager = ZugManager(netz, betrieb_daten)

    # 3. Validator und Tarif erstellen
    validator = EingabeValidator(netz)
    tarif     = Tarif()


    # 4. Eingaben holen

    start = validator.eingabe_station("Start-Station: ")
    ziel  = validator.eingabe_station("Ziel-Station:  ")

    wunschzeit = validator.frage_wunschzeit().strftime("%H:%M")


    # 5. Beste Fahrt finden (wenigste Umstiege → früheste Ankunft)

    route, fahrten = zugmanager.finde_beste_fahrt(start.name, ziel.name, wunschzeit)

    if not route:
        print("\nKeine Route gefunden!")
    elif not fahrten:
        print("\nKein Zug mehr heute!")


    # 6. Ticket und Preis

    else:
        ticket = Ticket(
            anzahl_stationen=len(route) - 1,
            ist_mehrfahrt=validator.frage_einzel_mehrticket(),
            hat_sozialrabatt=validator.frage_sozialrabatt(),
            ist_barzahlung=validator.frage_zahlart()
        )
        preis = tarif.berechne_preis(ticket)


        # 7. Ausgabe

        segmente = route.get_segmente()

        print()
        print(f"Route:     {route}")
        print(f"Stationen: {len(route) - 1}")
        print()

        # Direkte Fahrt (kein Umstieg)
        if len(fahrten) == 1:
            linie_name, zug, abfahrt, ankunft = fahrten[0]
            print(f"Linie:     {linie_name}  (Zug {zug.startzeit.strftime('%H:%M')} Uhr)")
            print(f"Abfahrt:   {abfahrt.strftime('%H:%M:%S')} Uhr  ({route.start.name})")
            print(f"Ankunft:   {ankunft.strftime('%H:%M:%S')} Uhr  ({route.ziel.name})")

        # Mit Umstieg(en)
        else:
            umstieg_stationen = route.get_umstiegestationen()

            for i, (linie_name, zug, abfahrt, ankunft) in enumerate(fahrten):
                seg_stationen = segmente[i][1]

                if i == 0:
                    print(f"Abschnitt 1 - {linie_name}  (Zug {zug.startzeit.strftime('%H:%M')} Uhr)")
                else:
                    umstieg_name = umstieg_stationen[i - 1].name
                    print(f"Abschnitt {i + 1} - {linie_name}  (Zug {zug.startzeit.strftime('%H:%M')} Uhr)  <- Umstieg in {umstieg_name}")

                print(f"  Abfahrt:  {abfahrt.strftime('%H:%M:%S')} Uhr  ({seg_stationen[0].name})")
                print(f"  Ankunft:  {ankunft.strftime('%H:%M:%S')} Uhr  ({seg_stationen[-1].name})")
                print()

        print(f"Preis:     {preis:.2f} €")