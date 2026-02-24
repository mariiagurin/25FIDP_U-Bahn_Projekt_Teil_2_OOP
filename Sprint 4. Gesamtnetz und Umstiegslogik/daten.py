# ==============================================================================
# Linie U1
# ==============================================================================

linie1_stationen = [
    "Langwasser Süd", "Gemeinschaftshaus", "Langwasser Mitte",
    "Scharfreiterring", "Langwasser Nord", "Messe",
    "Bauernfeindstraße", "Hasenbuck", "Frankenstraße",
    "Maffeiplatz", "Aufseßplatz", "Hauptbahnhof",
    "Lorenzkirche", "Weißer Turm", "Plärrer",
    "Gostenhof", "Bärenschanze", "Maximilianstraße",
    "Eberhardshof", "Muggenhof", "Stadtgrenze",
    "Jakobinenstraße", "Fürth Hbf."
]

linie1_fahrtzeiten          = [3, 2, 2, 3, 2, 3, 2, 2, 2, 1, 2, 2, 3, 2, 2, 1, 2, 2, 2, 3, 2, 3]
linie1_betrieb_start        = "05:00"
linie1_betrieb_ende         = "23:00"
linie1_takt                 = 10
linie1_haltezeit_endstation = 60   # Sekunden
linie1_haltezeit_umstieg    = 60   # Sekunden
linie1_haltezeit_standard   = 30   # Sekunden


# ==============================================================================
# Linie U2
# ==============================================================================

linie2_stationen = [
    "Röthenbach", "Hohe Marter", "Schweinau",
    "St. Leonhard", "Rothenburger Straße", "Plärrer",
    "Opernhaus", "Hauptbahnhof", "Wöhrder Wiese",
    "Rathenauplatz", "Rennweg", "Schoppershof",
    "Nordostbahnhof", "Herrnhütte", "Ziegelstein",
    "Flughafen"
]

linie2_fahrtzeiten          = [2, 2, 2, 2, 3, 2, 2, 2, 1, 2, 2, 2, 3, 2, 3]
linie2_betrieb_start        = "05:00"   # TODO: echte Betriebszeiten eintragen
linie2_betrieb_ende         = "23:00"   # TODO: echte Betriebszeiten eintragen
linie2_takt                 = 10        # TODO: echten Takt eintragen
linie2_haltezeit_endstation = 60        # TODO: echte Haltezeit eintragen
linie2_haltezeit_umstieg    = 60        # TODO: echte Haltezeit eintragen
linie2_haltezeit_standard   = 30        # TODO: echte Haltezeit eintragen


# ==============================================================================
# Linie U3
# ==============================================================================

linie3_stationen = [
    "Gustav-Adolf-Straße", "Sündersbühl", "Rothenburger Straße",
    "Plärrer", "Opernhaus", "Hauptbahnhof",
    "Wöhrder Wiese", "Rathenauplatz", "Maxfeld",
    "Kaulbachplatz", "Friedrich-Ebert-Platz"
]

linie3_fahrtzeiten          = [4, 2, 3, 2, 2, 2, 1, 2, 3, 2]
linie3_betrieb_start        = "05:00"   # TODO: echte Betriebszeiten eintragen
linie3_betrieb_ende         = "23:00"   # TODO: echte Betriebszeiten eintragen
linie3_takt                 = 10        # TODO: echten Takt eintragen
linie3_haltezeit_endstation = 60        # TODO: echte Haltezeit eintragen
linie3_haltezeit_umstieg    = 60        # TODO: echte Haltezeit eintragen
linie3_haltezeit_standard   = 30        # TODO: echte Haltezeit eintragen


# ==============================================================================
# Umstiegszeiten (Minuten)
# ==============================================================================

umstiegszeit_hauptknoten = 5   # Hauptknoten: 3+ Linien (Hauptbahnhof, Plärrer)
umstiegszeit_knoten      = 3   # Knoten:      2 Linien  (alle anderen)