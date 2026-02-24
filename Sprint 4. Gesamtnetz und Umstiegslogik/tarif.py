class Ticket:
    def __init__(self, anzahl_stationen, ist_mehrfahrt=False, hat_sozialrabatt=False, ist_barzahlung=False):
        self.anzahl_stationen = anzahl_stationen
        self.ist_mehrfahrt = ist_mehrfahrt
        self.hat_sozialrabatt = hat_sozialrabatt
        self.ist_barzahlung = ist_barzahlung

    def kategorie_bestimmen(self):
        if self.anzahl_stationen <= 3:
            return "kurz"
        if self.anzahl_stationen <= 8:
            return "mittel"
        else:
            return "lang"

    def setze_mehrfahrt(self, wert):
        self.ist_mehrfahrt = wert

    def setze_sozialrabatt(self, wert):
        self.hat_sozialrabatt = wert

    def zahlart_setzen(self, ist_bar):
        self.ist_barzahlung = ist_bar

    def get_kategorie(self):
        return self.kategorie_bestimmen()

    def __str__(self):
        text = "Ticket: " + self.get_kategorie()
        text = text + " (" + str(self.anzahl_stationen) + " Stationen)"

        if self.ist_mehrfahrt:
            text = text + ", ist Mehrfahrt"
        if self.hat_sozialrabatt:
            text = text + ", mit Sozialrabatt"
        if self.ist_barzahlung:
            text = text + ", Barzahlung"

        return text


class Tarif:
    """Verwaltet Preisberechnung nach Tariftabelle"""

    def __init__(self):
        """Erstellt Tarif-Objekt mit Preistabelle"""

        # Preistabelle: {kategorie: {einzelticket: preis, mehrfahrt: preis}}
        self.preistabelle = {
            "kurz": {
                "einzelticket": 1.50,
                "mehrfahrt": 5.00
            },
            "mittel": {
                "einzelticket": 2.00,
                "mehrfahrt": 7.00
            },
            "lang": {
                "einzelticket": 3.00,
                "mehrfahrt": 10.00
            }
        }

    def hole_basispreis(self, ticket):
        """Holt Basispreis aus Tabelle

        Args:
            ticket (Ticket): Ticket-Objekt

        Returns:
            float: Basispreis
        """
        kategorie = ticket.get_kategorie()

        if ticket.ist_mehrfahrt:
            return self.preistabelle[kategorie]["mehrfahrt"]
        else:
            return self.preistabelle[kategorie]["einzelticket"]

    def berechne_preis(self, ticket):
        """Berechnet Endpreis

            Args:
            ticket (Ticket): Ticket-Objekt

            Returns:
        float: Endpreis in Euro
        """

        # Schritt 1: Basispreis holen
        basispreis = self.hole_basispreis(ticket)
        # Schritt 2: Alle prozentualen Änderungen summieren
        prozent_aenderung = 0.0

        if not ticket.ist_mehrfahrt:
            prozent_aenderung += 0.10  # +10% Einzelticket-Aufschlag

        if ticket.hat_sozialrabatt:
            prozent_aenderung -= 0.20  # -20% Sozialrabatt

        if ticket.ist_barzahlung:
            prozent_aenderung += 0.15  # +15% Barzahlungs-Gebühr

        # Schritt 3: Gesamtänderung auf Basispreis anwenden
        preis = basispreis * (1 + prozent_aenderung)

        # Schritt 4: Runden auf 2 Nachkommastellen
        endpreis = round(preis, 2)

        return endpreis


# ==============================================================================
# Test

if __name__ == "__main__":
    tarif = Tarif()

    # Stationsanzahl eingeben
    anzahl = int(input("Stationsanzahl: "))

    # Ticketart
    eingabe = input("Mehrfahrtenticket? (ja/nein): ").strip().lower()
    ist_mehrfahrt = eingabe == "ja"

    # Sozialrabatt
    eingabe = input("Sozialrabatt? (ja/nein): ").strip().lower()
    hat_sozialrabatt = eingabe == "ja"

    # Zahlart
    eingabe = input("Barzahlung? (ja/nein): ").strip().lower()
    ist_barzahlung = eingabe == "ja"

    # Ticket erstellen und Preis berechnen
    ticket = Ticket(anzahl, ist_mehrfahrt, hat_sozialrabatt, ist_barzahlung)
    preis = tarif.berechne_preis(ticket)

    # Ausgabe
    print()
    print(f"Ticket:     {ticket}")
    print(f"Basispreis: {tarif.hole_basispreis(ticket):.2f} €")
    print(f"Endpreis:   {preis:.2f} €")