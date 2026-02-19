# Sprint 4 Backlog

---
> ## HINWEIS bis Mittwoch, 25.02., bitte erstmal auf Implementierung des Netzplans und Umstiegslogik konzentrieren!
---

## Zusammenfassung
Der wesentliche Schwerpunkt im Sprint ist die Implementierung der Logik für den Umstieg. Ein zweiter Schwerpunkt ist die Erstellung eines Adapters.

---

## User Story 4.1: Verkehrsbetrieb (Kunde)
**„Die Fahrkartenautomaten arbeiten korrekt für U1. Nun soll das gesamte Netz einbezogen werden.“**

### Abnahmekriterien US 4.1:
* **4.1.1** Alle Stationen der Linien U1, U2 und U3 sind vollständig im System hinterlegt.
* **4.1.2** Die Datenstruktur (Graph) bildet alle Linienverläufe des Gesamtnetzes ab.
* **4.1.3** Die Streckenberechnung liefert korrekte Ergebnisse für Start- und Zielpunkte auf unterschiedlichen Linien.

> Eine Liste mit allen Haltestellen ist in der Datei Netzplan zu finden.

---

## User Story 4.2: Fahrgast
**„Da mein Ziel auf einer anderen Linie liegt, muss ich umsteigen. Ich möchte sicher sein, dass ich genug Zeit habe, meinen Anschlusszug zu erreichen.“**

### Abnahmekriterien US 4.2:
* **4.2.1** Das System identifiziert gültige Umstiegsstationen (Knotenpunkte) zwischen den Linien.
* **4.2.2** Die Umstiegslogik berücksichtigt eine definierte Mindestumstiegszeit (Puffer) zwischen Ankunft und Abfahrt.
* **4.2.3** Bei der Routenausgabe werden die Abfahrtszeiten der Anschlusszüge an den Knotenpunkten korrekt angezeigt.

---

## User Story 4.3: Fahrgast
**„Ich möchte möglichst schnell ans Ziel kommen. Wenn ich dadurch nicht früher ankomme, bleibe ich lieber sitzen, statt umzusteigen. Der Automat soll mir nur dann einen Umstieg empfehlen, wenn dieser sinnvoll ist.“**

### Abnahmekriterien US 4.3:
* **4.3.1** Der Suchalgorithmus bevorzugt bei zeitlich gleichwertigen Verbindungen die Route mit der geringsten Anzahl an Umstiegen.
* **4.3.2** Die Gesamtfahrzeit wird inklusive der realen Aufenthaltszeiten an den Umstiegsstationen berechnet und ausgegeben.

---

## User Story 4.4: Verkehrsbetrieb (Kunde)
**„Als Verkehrsbetrieb (Kunde) wünschen wir uns, dass bei der Eingabe der Uhrzeit keine Gedanken zu Trennzeichen oder führenden Nullen notwendig sind.“**

### Abnahmekriterien US 4.4:
* **4.4.1** Das System akzeptiert verschiedene Trennzeichen (Doppelpunkt, Punkt, Komma, Leerzeichen) sowie Eingaben ohne Trenner.
* **4.4.2** Einstellige Stunden- oder Minutenangaben werden automatisch mit führenden Nullen vervollständigt (z. B. „9“ zu „09:00“).
* **4.4.3** Kurzeingaben (nur Stunden) werden als volle Stunde interpretiert.
* **4.4.4** Das System validiert die Eingabe auf logische Korrektheit (00:00 bis 23:59) und gibt bei Fehlern einen Hinweis aus.
* **4.4.5** Nach der Eingabe wird der Wert im UI einheitlich im Format HH:mm dargestellt.

---

## User Story 4.5: Verkehrsbetrieb (Kunde)
**„Um eine gleichbleibend hohe Softwarequalität sicherzustellen, möchte der Verkehrsbetrieb (Kunde), dass alle Modullösungen über eine Schnittstelle (Adapter) geprüft werden. Dadurch soll die automatisierte Abnahme effizient, standardisiert und vergleichbar erfolgen.“**

### Abnahmekriterien US 4.5:
* **4.5.1** Für den Code ist ein Adapter nach dem vorgegebenen Muster implementiert.
* **4.5.2** Der Adapter übersetzt die spezifischen internen Datenstrukturen der Gruppe in das standardisierte Format des zentralen Testskripts.
* **4.5.3** Das Testskript kann alle automatisierten Testfälle (z. B. aus US 4.1 bis 4.4) ohne manuelle Anpassungen am Gruppen-Code ausführen.
* **4.5.4** Der Adapter fängt Inkompatibilitäten ab und liefert im Fehlerfall standardisierte Rückmeldungen an die Testumgebung.
```
---

### Adapter 
Eingabe:
Start-Haltestelle exakt so geschrieben wie vorgegeben: eingabe_start = <Haltestellenname>
Ziel-Haltestelle ebenso: eingabe_ziel = <Haltestellenname>
gewünschte Startzeit: eingabe_startzeit = <HHMM> (Verzicht auf Doppelpunkt ist hier bewusst!)
Fehlermeldung vom Adapter: fehler = True

Ausgabe:
Abfahrtzeit für Fahrgast an Starthaltestelle: ausgabe_startzeit = <HH:MM>
Ankunfzszeit für Fahrgast an Zielhaltestelle: ausgabe_zielzeit = <HH:MM>
Nennung der Bahnlinien, die auf der Route benutzt werden: bahnlinien_gesamtfahrt = <[U1,...]>
Fahrtroute, alle angefahrenen Haltestellen und jeweils Abfahrt- und Ankunftszeiten: route = <{"Haltestellename":["Bahnlinie", HH:MM:SS, HH:MM:SS], ...}> --> bei Start und Ziel sind jeweils Abfahrts- und Ankunftszeit identisch
Angabe der Umstiegshaltestelle(n): umstieg_haltestellen = <["Haltestellenname", ...]>
Angabe zu Umstiegen auf die Sekunde genau: umstiege_exakt = <{"Haltestellename":[HH:MM:SS, HH:MM:SS], ...}>
Angabe zu Umstiegen wie an Fahrgast ausgegeben: umstiege_fahrgast = <{"Haltestellename":[HH:MM:SS, HH:MM:SS], ...}>
Angabe der Bahnlinie bei Umstiegen: umstieg_bahnlinien = <[U1, ...]>
Gesamtdauer der Fahrt: dauer_gesamtfahrt = <HH:MM:SS>
