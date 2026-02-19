# Sprint 3: Reiseinformationen und Tariflogik

### Kurzfassung

Ziel dieses Sprints ist die fachliche Vervollständigung der Reiseauskunft. Der Fahrgast erhält nun präzise Informationen über die Ankunftszeit und die individuellen Fahrtkosten. Zudem wird das System gegenüber fehlerhaften Benutzereingaben abgesichert.

## User Stories und fachliche Spezifikationen

### User Story 3.1: Verkehrsbetrieb
**„Wenn der Benutzer eine falsche Eingabe macht, darf das Programm nicht abstürzen. Kleine Abweichungen bei der Eingabe sollen möglich sein und die Ausgabe der gewünschten Information nicht behindern.“**

* **Normalisierungs-Pflicht:** Das System muss die Eingabe vor dem Vergleich händisch vorverarbeiten:
    * Entfernen von führenden/folgenden Leerzeichen.
    * Umwandlung in Kleinschreibung.
    * Vereinheitlichung von Sonderzeichen (Bindestriche zu Leerzeichen).
    * Ersetzung von Umlauten (ä -> ae, etc.) und ß (-> ss).
* **Ersetzung von Kürzeln (Mapping):** Das System muss vordefinierte Abkürzungen in der Benutzereingabe erkennen und durch die entsprechenden Vollwörter aus der Haltestellenliste ersetzen (z. B. wird aus "Hbf." automatisch "Hauptbahnhof", aus "Str." wird "Straße" und aus "Fr.-" wird "Friedrich-"). Hierbei muss darauf geachtet werden, dass die Eindeutigkeit erhalten bleibt - siehe dazu Testfälle und Anmerkungen unten in diesem Dokument.
* **Fuzzy-Matching:** Nach der Normalisierung muss das System eine Übereinstimmung von mindestens 80 % zum Datenbestand erkennen.
* **Fehlerbehandlung:** Bei nicht eindeutigen Eingaben muss eine freundliche Fehlermeldung ausgegeben und die Eingabe wiederholt werden.

### User Story 3.2: Verkehrsbetrieb
**„Als Verkehrsplaner möchten wir ein Rabattsystem implementieren, das unserem Selbstverständnis als sozialem Unternehmen gerecht wird. Außerdem möchten wir Anreize für bargeldloses Zahlen schaffen und die Kundenbindung durch Mehrfachkarten erhöhen.“**

> **Hinweis:** Preis- und Rabattmodelle entsprichen den Spezifikationen aus Teil 1 des U-Bahn-Projektes (S5-01 bis S5-04 im Dokument SPRINT5_BACKLOG.md). In Teil 1 des Projektes erstellter Code kann also als Vorlage für die Implementierung in diesem Sprint in OOP dienen.

* **(Ticket-Kategorisierung):** Die Wahl des Tickets richtet sich nach der Anzahl der Stationen:
    * **Kurzticket:** 1 bis 3 Stationen.
    * **Mittelticket:** 1 bis 8 Stationen.
    * **Langticket:** beliebig viele Stationen.
* **(Ticket-Art):** Der Fahrgast kann zwischen Einzeltickets und Mehrfahrtentickets (4 Fahrten) wählen.
* **(Preisfindung):** Die Berechnung erfolgt auf Basis der in Teil 1 definierten Preise und Regeln:
    * **Basispreise:**
        * Einzelticket: Kurz 1,50 €, Mittel 2 €, Lang 3 €.
        * Mehrfahrtenticket: Kurz 5 €, Mittel 7 €, Lang 10 €.
    * **Konditionen:**
        * Ticketart-Zuschlag: +10% für Einzeltickets.
        * Sozialrabatt: -20% auf den Preis.
        * Zahlart-Zuschlag: +15% bei Barzahlung.

**Wichtiger Hinweis zur Preisberechnung**

Die Rabatte bzw. Zuschläge werden zunächst addiert, d.h. bei Einzelticket (+10 %) und Sozialrabatt (-20 %) ergibt sich ein Gesamtrabatt (!) von 10 % (10 % - 20 % = -10 %), also ein Faktor von 0.9, mit dem der Grundpreis (z. B. 1,50 € für die Kurzstrecke) multipliziert wird.

### User Story 3.3: Fahrgast
**„Ich möchte nach Eingabe meines Ziels sehen, wann ich dort ankomme und was die Fahrt kostet, um Planungssicherheit zu haben.“**

* Das System muss die voraussichtliche Ankunftszeit am Zielort berechnen und anzeigen.
* Dem Fahrgast muss nach Beantwortung der Tarif-Fragen der endgültige Ticketpreis klar ausgewiesen werden.
* Die Zusammenfassung der Reise (Start, Ziel, Abfahrt, Ankunft und Endpreis, Zeitstempel) bildet den Abschluss des Beratungsvorgangs.

---

## Abnahmekriterien für das Inkrement (Code)
1. Der Code jeder Gruppe muss auf der Fork dieser Gruppe zugänglich sein.
2. Stationseingaben werden korrekt verarbeitet, auch wenn sie nur zu 80 % korrekt sind oder Abkürzungen (Hbf., Str.) enthalten.
3. Die Ankunftszeit an der Zielstation wird korrekt ausgegeben.
4. Die Preisberechnung liefert für alle Kombinationen (Ticket-Typ, Rabatt, Zahlart) korrekte Ausgaben.
5. Der Fahrgast erhält eine abschließende Übersicht aller relevanten Reisedaten.

---

## Liste der Testfälle für die Abnahme

### Testfälle zu Abnahmekriterium 2.
| Nr. | Eingabe-Typ                | Benutzereingabe   | Erwartete Ausgabe / Reaktion | Logik-Prüfung                    |
| :--- |:---------------------------|:------------------| :--- |:---------------------------------|
| 1 | **exakte Übereinstimmung** | `Messe`           | `Messe` erkannt | Standardfall                     |
| 2 | **Mapping & Punkt**        | `Fürth Hbf.`      | `Fürth Hauptbahnhof` erkannt | Abkürzung mit Punkt              |
| 3 | **Kleinschreibung**        | `aufseßplatz`     | `Aufseßplatz` erkannt | Klein- und Großschreibung        |
| 4 | **ß-Ersetzung**            | `Aufsessplatz`    | `Aufseßplatz` erkannt | ß vs. ss Handling                |
| 5 | **Umlaute**                | `Baerenchanze`    | `Bärenschanze` erkannt | ae -> ä Konvertierung            |
| 6 | **Tippfehler (80%)**       | `Maffeiplat`      | `Maffeiplatz` erkannt | Fehlendes 'z'                    |
| 7 | **Tippfehler (80%)**       | `Jakobinenstrase` | `Jakobinenstraße` erkannt | Buchstabendreher/Fehler          |
| 8 | **Leerzeichen**            | `  Gostenhof  `   | `Gostenhof` erkannt | Trim / Strip Funktion            |
| 9 | **langer Name**            | `Langwasser Nord` | `Langwasser Nord` erkannt | Mehrwort-Erkennung               |
| 10 | **nicht eindeutig**        | `Hauptbahnhof`    | `Hauptbahnhof` erkannt | Korrekte Wahl (nicht Fürth)      |
| 11 | **zu ungenau**             | `Wasser`          | Fehlermeldung | < 80% (zu viele Treffer möglich) |
| 12 | **linienfremd**            | `Flughafen`       | Fehlermeldung | Station existiert nicht auf U1   |

Erläuterung zu Testfall 10 & 12:

    Testfall 8: Hier ist vor und nach Gostenhof ein Leerzeichen: ' Gostenhof '     

    Testfall 10: Da die Eingabe exakt "Hauptbahnhof" lautet, muss das System diesen auch wählen und nicht den "Fürth Hauptbahnhof", da hier ein 100% Match vorliegt.

    Testfall 12: Da die U2/U3 noch nicht implementiert sind, muss das System den "Flughafen" als unbekannt ablehnen, um die Integrität der U1-Reiseplanung zu wahren.

### Testfälle zu Abnahmekriterium 3.

| Nr. | Szenario | Start-Haltestelle | Ziel-Haltestelle | Wunschzeit | Erwartete Abfahrt | Erwartete Ankunft exakt | Erwartete Ankunft aufgerundet |
|:----| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Erster Zug (Start)** | Langwasser Süd | Fürth Hbf. | 04:30 | **05:00 Uhr** | 05:59:30 | **06:00** |
| 2 | **Hauptknoten (Hbf)** | Hauptbahnhof | Plärrer | 08:02 | **08:10 Uhr** | 08:18:00 | **08:18** |
| 3 | **Richtungswechsel** | Fürth Hbf. | Stadtgrenze | 05:45 | **06:00 Uhr** | 06:06:00 | **06:06** |
| 4 | **Punktlandung** | Maffeiplatz | Aufseßplatz | 08:35 | **08:35 Uhr** | 08:36:30 | **08:37** |
| 5 | **Später Abend** | Gostenhof | Eberhardshof | 23:36 | **23:41 Uhr** | 23:47:30 | **23:48** |



### Testfälle zu Abnahmekriterium 4.

| Nr | Strecke | Start | Ziel | Ticketart | Sozialrabatt | Zahlung | Erwarteter Preis | Ausgabe korrekt? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | kurz | Langwasser Süd | Langwasser Mitte | Einzel | nein | Karte | 1,65€ | |
| 2 | kurz | Langwasser Süd | Langwasser Mitte | Einzel | nein | Bar | 1,88€ | |
| 3 | kurz | Langwasser Süd | Langwasser Mitte | Einzel | ja | Karte | 1,35€ | |
| 4 | kurz | Langwasser Süd | Langwasser Mitte | Einzel | ja | Bar | 1,58€ | |
| 5 | kurz | Langwasser Süd | Langwasser Mitte | Mehrfahrt | nein | Karte | 5,00€ | |
| 6 | kurz | Langwasser Süd | Langwasser Mitte | Mehrfahrt | nein | Bar | 5,75€ | |
| 7 | kurz | Langwasser Süd | Langwasser Mitte | Mehrfahrt | ja | Karte | 4,00€ | |
| 8 | kurz | Langwasser Süd | Langwasser Mitte | Mehrfahrt | ja | Bar | 4,75€ | |
| 9 | mittel | Langwasser Süd | Messe | Einzel | nein | Karte | 2,20€ | |
| 10 | mittel | Langwasser Süd | Messe | Einzel | nein | Bar | 2,50€ | |
| 11 | mittel | Langwasser Süd | Messe | Einzel | ja | Karte | 1,80€ | |
| 12 | mittel | Langwasser Süd | Messe | Einzel | ja | Bar | 2,10€ | |
| 13 | mittel | Langwasser Süd | Messe | Mehrfahrt | nein | Karte | 7,00€ | |
| 14 | mittel | Langwasser Süd | Messe | Mehrfahrt | nein | Bar | 8,05€ | |
| 15 | mittel | Langwasser Süd | Messe | Mehrfahrt | ja | Karte | 5,60€ | |
| 16 | mittel | Langwasser Süd | Messe | Mehrfahrt | ja | Bar | 6,65€ | |
| 17 | lang | Langwasser Süd | Hauptbahnhof | Einzel | nein | Karte | 3,30€ | |
| 18 | lang | Langwasser Süd | Hauptbahnhof | Einzel | nein | Bar | 3,75€ | |
| 19 | lang | Langwasser Süd | Hauptbahnhof | Einzel | ja | Karte | 2,70€ | |
| 20 | lang | Langwasser Süd | Hauptbahnhof | Einzel | ja | Bar | 3,15€ | |
| 21 | lang | Langwasser Süd | Hauptbahnhof | Mehrfahrt | nein | Karte | 10,00€ | |
| 22 | lang | Langwasser Süd | Hauptbahnhof | Mehrfahrt | nein | Bar | 11,50€ | |
| 23 | lang | Langwasser Süd | Hauptbahnhof | Mehrfahrt | ja | Karte | 8,00€ | |
| 24 | lang | Langwasser Süd | Hauptbahnhof | Mehrfahrt | ja | Bar | 9,50€ | |