# -*- coding: utf-8 -*-
"""Englische Texte zu den deutschen Quelltexten (siehe kern.sprache).

Schluessel = deutscher Text genau wie im Code, Wert = englische Fassung mit
denselben Platzhaltern. tests/test_sprache.py prueft Vollstaendigkeit.
"""

EN = {
    # --- Verbindung, Codes, Druck -------------------------------------------------
    "Der Port {port} lässt sich nicht öffnen: {text}": "Cannot open port {port}: {text}",
    "Der Drucker an {port} ist nicht erreichbar.\n\nBitte prüfen:\n"
    "• Ist er eingeschaltet? (Nach einer Pause schaltet er sich ab.)\n"
    "• Ist das Handy noch mit ihm verbunden? Dann dort Bluetooth ausschalten.\n\n"
    "Technisch: {text}":
        "The printer on {port} cannot be reached.\n\nPlease check:\n"
        "• Is it switched on? (It turns itself off after a while.)\n"
        "• Is a phone still connected to it? Then turn off Bluetooth on the phone.\n\n"
        "Technical details: {text}",
    "Die Verbindung zu {port} ist abgerissen: {fehler}": "The connection to {port} was lost: {fehler}",
    "Der QR-Code ist leer.": "The QR code is empty.",
    "Der QR-Code braucht mindestens {anzahl} Punkte, das Feld hat {feld}. "
    "Feld größer machen oder Text kürzen.":
        "The QR code needs at least {anzahl} dots, the field has {feld}. "
        "Make the field bigger or shorten the text.",
    "Der Barcode braucht mindestens {anzahl} Punkte Breite, das Feld hat {feld}.":
        "The barcode needs at least {anzahl} dots of width, the field has {feld}.",
    "Das Feld ist zu niedrig für einen Barcode.": "The field is too low for a barcode.",
    "Der Text ist zu lang für einen QR-Code.": "The text is too long for a QR code.",
    "Der Inhalt lässt sich nicht als Barcode darstellen: {fehler}":
        "The content cannot be shown as a barcode: {fehler}",
    "Ein EAN-13 braucht 12 oder 13 Ziffern.": "An EAN-13 needs 12 or 13 digits.",
    "Die Prüfziffer stimmt nicht, richtig wäre {richtig}.":
        "The check digit is wrong, it should be {richtig}.",
    "Unbekannte Barcode-Art: {art}": "Unknown barcode type: {art}",
    "Der Barcode ist leer.": "The barcode is empty.",
    "Element {nr}: {meldung}": "Element {nr}: {meldung}",
    "Kein Drucker gewählt.": "No printer selected.",
    "↑ OBEN {grad}°": "↑ UP {grad}°",
    "Das Bild ist leer.": "The image is empty.",
    "Das Bild ist zu groß für den Drucker.": "The image is too large for the printer.",
    "Unbekannter Papiertyp: {wert}": "Unknown paper type: {wert}",
    "Unbekannte Dichte: {wert}": "Unknown density: {wert}",

    # --- Windows-Drucker einrichten ---------------------------------------------------
    'Windows-Drucker "{name}" ist an {port} eingerichtet.':
        'Windows printer "{name}" is set up on {port}.',
    "Der Download ist unerwartet groß.": "The download is unexpectedly large.",
    "Der geladene Installer ist nicht vom Hersteller signiert und wurde nicht gestartet.":
        "The downloaded installer is not signed by the manufacturer and was not started.",
    "Der Treiber-Installer wurde abgebrochen oder die Rückfrage nach "
    "Administratorrechten abgelehnt.":
        "The driver installer was cancelled or the administrator prompt was declined.",
    "Geht nur unter Windows.": "Only works on Windows.",
    "Die Windows-Rückfrage nach Administratorrechten wurde abgelehnt oder ist gescheitert.":
        "The Windows administrator prompt was declined or failed.",
    "Download vom Hersteller ging nicht ({fehler}).\nVon Hand: {seite}":
        "Download from the manufacturer failed ({fehler}).\nManual download: {seite}",
    "Der Download enthält keinen Treiber-Installer. Von Hand: {seite}":
        "The download contains no driver installer. Manual download: {seite}",
    "Unbekannter Fehler": "Unknown error",

    # --- Vorlagen und Tabellen ----------------------------------------------------------
    "Die Datei enthält keine Vorlage.": "The file does not contain a template.",
    "Der Datei fehlt die Fassungsnummer.": "The file has no format version.",
    "Die Vorlage stammt aus einer neueren Fassung ({fassung}) dieses Programms.":
        "The template comes from a newer version ({fassung}) of this program.",
    "Unbekannte Elementart: {art}": "Unknown element type: {art}",
    "Die Vorlage ist beschädigt: {fehler}": "The template is damaged: {fehler}",
    "Die Datei lässt sich nicht lesen: {fehler}": "Cannot read the file: {fehler}",
    "ja": "yes",
    "nein": "no",
    "Die Datei enthält keine Zeilen.": "The file contains no rows.",
    "Spalte {nr}": "Column {nr}",
    "Die Datei lässt sich nicht öffnen: {fehler}": "Cannot open the file: {fehler}",
    "Die Excel-Datei lässt sich nicht lesen: {fehler}": "Cannot read the Excel file: {fehler}",
    "Dateien vom Typ {endung} kann der Serien-Druck nicht lesen. "
    "Bitte CSV oder Excel (.xlsx) nehmen.":
        "Batch printing cannot read files of type {endung}. Please use CSV or Excel (.xlsx).",
    "(ohne Endung)": "(no extension)",

    # --- Programm allgemein ------------------------------------------------------------
    "Etikettendrucker": "Label Printer",
    "Unerwarteter Fehler:\n{fehler}\n\nEinzelheiten in {datei}.":
        "Unexpected error:\n{fehler}\n\nDetails in {datei}.",
    "Unerwarteter Fehler: {fehler}": "Unexpected error: {fehler}",

    # --- Aufkleber -----------------------------------------------------------------------
    "Aufkleber": "Stickers",
    "Suchen (englische Stichwörter, z. B. heart, flower, cake) …":
        "Search (English keywords, e.g. heart, flower, cake) …",
    "{anzahl} Aufkleber": "{anzahl} stickers",
    "Keine Aufkleber gefunden. install.bat lädt die freie Sammlung; eigene Grafiken in "
    "den Ordner aufkleber\\eigene legen.":
        "No stickers found. install.bat downloads the free collection; put your own "
        "graphics into the folder aufkleber\\eigene.",

    # --- Bild ----------------------------------------------------------------------------
    "Bild": "Image",
    "Das Bild lässt sich nicht lesen:\n{fehler}": "Cannot read the image:\n{fehler}",

    # --- Druckleiste -----------------------------------------------------------------
    "Eigene Größe": "Custom size",
    "Etiketten mit Lücke": "Labels with gap",
    "Endlospapier": "Continuous paper",
    "Etiketten mit schwarzer Marke": "Labels with black mark",
    "hell": "light",
    "normal": "normal",
    "dunkel": "dark",
    "Drucker neu suchen": "Search for printers again",
    "Drucker:": "Printer:",
    "Größe:": "Size:",
    "Papier:": "Paper:",
    "Dichte:": "Density:",
    "Kopien:": "Copies:",
    "Kein Drucker gefunden – einschalten und in Windows koppeln":
        "No printer found – switch it on and pair it in Windows",
    "Drucken": "Print",

    # --- Eigenschaften ---------------------------------------------------------------
    "Text": "Text",
    "QR-Code": "QR code",
    "Barcode": "Barcode",
    "Rahmen": "Frame",
    "Linie": "Line",
    "links": "left",
    "Mitte": "center",
    "rechts": "right",
    "Schwelle (Grafik, Logo)": "Threshold (graphic, logo)",
    "Fehlerverteilung (Foto)": "Dithering (photo)",
    "Links (mm)": "Left (mm)",
    "Oben (mm)": "Top (mm)",
    "Breite (mm)": "Width (mm)",
    "Höhe (mm)": "Height (mm)",
    "Drehung": "Rotation",
    "Element löschen": "Delete element",
    "Andere Form aus der Galerie wählen": "Choose another shape from the gallery",
    "Form": "Shape",
    "Bild wählen": "Choose image",
    "Bilder (*.png *.jpg *.jpeg *.bmp *.gif)": "Images (*.png *.jpg *.jpeg *.bmp *.gif)",
    "Schrift": "Font",
    "Größe (pt)": "Size (pt)",
    "fett": "bold",
    "Ausrichtung": "Alignment",
    "Kein Element gewählt.\n\nLinks ein Werkzeug anklicken\noder ein Element auf dem Etikett.":
        "No element selected.\n\nClick a tool on the left\nor an element on the label.",
    "Inhalt": "Content",
    "Art": "Type",
    "Klartext darunter": "Plain text below",
    "Umwandlung": "Conversion",
    "Anderes Bild …": "Other image …",
    "Strich (mm)": "Stroke (mm)",
    "Ecken (mm)": "Corners (mm)",

    # --- Einrichtungs-Assistent ----------------------------------------------------------
    "<ol><li>Den P15 einschalten. Ist ein Handy mit ihm verbunden, dort Bluetooth "
    "ausschalten oder die Marklife-App schließen.</li><li>Auf <b>„Bluetooth-Einstellungen "
    "öffnen“</b> klicken, dann <b>Gerät hinzufügen › Bluetooth</b>.</li><li>Den Eintrag "
    "<b>P15_…</b> wählen, <i>nicht</i> den mit <b>_BLE</b> am Ende. Fragt Windows nach "
    "einer PIN, ist es meist 0000.</li></ol><p>Sobald Windows den Drucker gekoppelt hat, "
    "erscheint er unten.</p>":
        "<ol><li>Switch on the P15. If a phone is connected to it, turn off Bluetooth on "
        "the phone or close the Marklife app.</li><li>Click <b>“Open Bluetooth settings”</b>, "
        "then <b>Add device › Bluetooth</b>.</li><li>Choose the entry <b>P15_…</b>, "
        "<i>not</i> the one ending in <b>_BLE</b>. If Windows asks for a PIN, it is "
        "usually 0000.</li></ol><p>As soon as Windows has paired the printer, it appears "
        "below.</p>",
    "1. Drucker per Bluetooth koppeln": "1. Pair the printer via Bluetooth",
    "Bluetooth-Einstellungen öffnen": "Open Bluetooth settings",
    "2. Als Windows-Drucker einrichten (freiwillig)": "2. Set up as a Windows printer (optional)",
    "Der Etikettendrucker braucht das nicht, er druckt direkt. Wer aber auch aus Word, dem "
    "Browser oder anderen Programmen auf den P15 drucken will, richtet hier den "
    "Windows-Drucker <b>„Marklife P15“</b> mit dem Treiber des Herstellers ein. Fehlt der "
    "Treiber noch, fragt Windows einmal nach Administratorrechten.":
        "The Label Printer does not need this, it prints directly. If you also want to "
        "print to the P15 from Word, your browser or other programs, set up the Windows "
        "printer <b>“Marklife P15”</b> with the manufacturer's driver here. If the driver "
        "is missing, Windows asks once for administrator rights.",
    "Windows-Drucker „Marklife P15“ einrichten": "Set up Windows printer “Marklife P15”",
    "Jetzt einrichten": "Set up now",
    "3. Fertig": "3. Done",
    "Der Etikettendrucker druckt jetzt auf <b>{name}</b>.<br><br>Tipp: Sitzt der Druck "
    "nicht ganz auf dem Etikett, hilft <b>Drucker › Lage feinjustieren</b>.":
        "The Label Printer now prints to <b>{name}</b>.<br><br>Tip: If the print is not "
        "quite on the label, use <b>Printer › Fine-tune position</b>.",
    "Drucker einrichten": "Printer setup",
    "Weiter >": "Next >",
    "< Zurück": "< Back",
    "Fertig": "Finish",
    "Abbrechen": "Cancel",
    "Wird an {port} eingerichtet (bisher an {alt}).": "Will be set up on {port} (currently {alt}).",
    "Wird an {port} eingerichtet.": "Will be set up on {port}.",
    "Der Treiber kommt vom Hersteller: Das Programm lädt ihn von marklifeprinter.com "
    "(ca. 6 MB), prüft die Signatur und startet das Installationsprogramm des Herstellers. "
    "Dort einfach durchklicken.":
        "The driver comes from the manufacturer: the program downloads it from "
        "marklifeprinter.com (about 6 MB), checks its signature and starts the "
        "manufacturer's installer. Just click through it.",
    "Noch kein P15 gekoppelt – suche alle 2 Sekunden …":
        "No P15 paired yet – searching every 2 seconds …",
    "Gefunden: {name}": "Found: {name}",
    "Schon eingerichtet: „{name}“ an {port}.": "Already set up: “{name}” on {port}.",
    "Haken entfernen, um ohne Windows-Drucker weiterzugehen.":
        "Untick the box to continue without a Windows printer.",
    "Hat nicht geklappt: {fehler}": "That did not work: {fehler}",

    # --- Hauptfenster ------------------------------------------------------------------
    "Etikett-Vorlagen (*.etikett.json)": "Label templates (*.etikett.json)",
    "Bild …": "Image …",
    "Aufkleber …": "Stickers …",
    "Rahmen …": "Frame …",
    "Linie …": "Line …",
    "Werkzeuge": "Tools",
    "Serien-Druck …": "Batch print …",
    "&Datei": "&File",
    "&Neu": "&New",
    "Ö&ffnen …": "&Open …",
    "&Speichern": "&Save",
    "Speichern &unter …": "Save &as …",
    "Se&rien-Druck …": "&Batch print …",
    "&Beenden": "E&xit",
    "D&rucker": "&Printer",
    "&Einrichten (Bluetooth, Windows-Drucker) …": "&Setup (Bluetooth, Windows printer) …",
    "&Ausrichtung testen …": "&Test orientation …",
    "&Lage feinjustieren …": "&Fine-tune position …",
    "Drucker &neu suchen": "Search for printers &again",
    "Ü&ber": "&About",
    "Vorlage öffnen": "Open template",
    "Vorlage speichern": "Save template",
    "neues Etikett": "new label",
    "Etikettendrucker – {name}": "Label Printer – {name}",
    "Drucke": "Printing",
    "Testdruck": "Test print",
    "Welches Etikett zeigt den Pfeil nach oben?": "Which label shows the arrow pointing up?",
    "Lage feinjustieren": "Fine-tune position",
    "Druck verschieben in mm (+ nach rechts, − nach links):":
        "Shift the print in mm (+ to the right, − to the left):",
    "Ausrichtung testen": "Test orientation",
    "Es werden zwei Etiketten gedruckt, je eines mit 90° und 270° Drehung. (0° und 180° "
    "passen nicht: Der P15 druckt das Etikett der Länge nach, quer ist sein Druckkopf nur "
    "14 mm breit.) Danach fragt das Programm, welches den Pfeil nach oben zeigt und lesbar "
    "ist.\n\nWeiter?":
        "Two labels will be printed, one rotated 90° and one 270°. (0° and 180° do not fit: "
        "the P15 prints along the label, across it its print head is only 14 mm wide.) "
        "Afterwards the program asks which one shows the arrow pointing up and is "
        "readable.\n\nContinue?",
    "Drehung {wahl} gespeichert.": "Rotation {wahl} saved.",
    "Versatz {wert} mm gespeichert.": "Offset {wert} mm saved.",
    "Drucker {name} gewählt.": "Printer {name} selected.",
    "{anzahl} Etikett(en) gesendet.": "{anzahl} label(s) sent.",
    "{meldung}\n\n{anzahl} Etikett(en) waren schon gesendet.":
        "{meldung}\n\n{anzahl} label(s) had already been sent.",
    "Neu": "New",
    "Das aktuelle Etikett verwerfen?": "Discard the current label?",
    "Speichern ging nicht:\n{fehler}": "Saving failed:\n{fehler}",
    "{was}: {a} von {g}": "{was}: {a} of {g}",

    # --- Galerie, Serien-Druck, Über ------------------------------------------------------
    "Rahmen wählen": "Choose frame",
    "Linie wählen": "Choose line",
    "Serien-Druck": "Batch print",
    "Tabelle wählen …": "Choose table …",
    "Noch keine Datei gewählt (CSV oder Excel).": "No file chosen yet (CSV or Excel).",
    "Schließen": "Close",
    "Tabelle wählen": "Choose table",
    "Tabellen (*.csv *.xlsx)": "Tables (*.csv *.xlsx)",
    "{meldung}\n\n{fertig} Etikett(en) sind fertig. „Zeilen von“ steht jetzt auf {zeile}, "
    "damit es dort weitergeht.":
        "{meldung}\n\n{fertig} label(s) are done. “Rows from” is now set to {zeile} so "
        "you can continue from there.",
    "Diese Platzhalter haben keine Spalte: {namen}": "These placeholders have no column: {namen}",
    "Zeilen von": "Rows from",
    "bis": "to",
    "Kopien je Zeile": "Copies per row",
    "Über Etikettendrucker": "About Label Printer",
    "Etiketten gestalten und auf dem Marklife P15 drucken.":
        "Design labels and print them on the Marklife P15.",
    "Version:": "Version:",
    "{version} vom {datum}": "{version} of {datum}",
    "Gemacht von:": "Made by:",
    "Programmiert mit:": "Programmed with:",
    "Begonnen:": "Started:",
    "Aufkleber-Symbole: Tabler Icons (MIT-Lizenz).": "Sticker symbols: Tabler Icons (MIT license).",

    # --- Rahmenformen ----------------------------------------------------------------------
    "einfach": "simple",
    "doppelt": "double",
    "dick-dünn": "thick-thin",
    "dreifach": "triple",
    "gestrichelt": "dashed",
    "gepunktet": "dotted",
    "Linie mit Punkten": "line with dots",
    "abgerundet": "rounded",
    "Kapsel": "capsule",
    "oval": "oval",
    "Doppel-Oval": "double oval",
    "abgeschrägt": "chamfered",
    "abgeschrägt doppelt": "chamfered double",
    "Ticket": "ticket",
    "Plakette": "plaque",
    "viktorianisch": "Victorian",
    "Eckwinkel": "corner brackets",
    "Eckrauten": "corner diamonds",
    "Eckpunkte": "corner dots",
    "Art déco Fächer": "Art Deco fan",
    "Art déco Stufen": "Art Deco steps",
    "Schnörkel": "flourish",
    "geschweifte Klammern": "curly braces",
    "Banderole": "banner",
    "Schild": "sign",
    "Wellenrand": "wavy edge",
    "Zackenrand": "zigzag edge",
    "Briefmarke": "postage stamp",
    "Kordel": "rope",
    "Schienen": "rails",
    "Perlen": "pearls",
    "Kreise": "circles",
    "Sterne": "stars",
    "Herzen": "hearts",
    "Lorbeer-Ecken": "laurel corners",
    "Blüten-Ecken": "blossom corners",
    "Lorbeerkranz": "laurel wreath",
    "Blätterkante": "leaf border",
    "Rankenrahmen": "vine frame",
    "Blumenwiese": "flower meadow",
    "Blütenkette": "blossom chain",
    "Bergpanorama": "mountain panorama",
    "Tannenwald": "fir forest",
    "Pilze": "mushrooms",
    "Tulpenbeet": "tulip bed",
    "Lavendel": "lavender",
    "Gänseblümchen-Ecken": "daisy corners",
    "Kräuterrahmen": "herb frame",
    "Blätterrahmen": "leaf frame",

    # --- Linienformen ----------------------------------------------------------------------
    "durchgezogen": "solid",
    "lang gestrichelt": "long dashes",
    "Strich-Punkt": "dash-dot",
    "Strich-Punkt-Punkt": "dash-dot-dot",
    "Kette": "chain",
    "Rauten": "diamonds",
    "Welle": "wave",
    "Zickzack": "zigzag",
    "Sägezahn": "sawtooth",
    "Zinnen": "battlements",
    "Mäander": "meander",
    "Bögen": "arches",
    "Schwellstrich": "swelling stroke",
    "Raute in der Mitte": "diamond in the middle",
    "Kreis in der Mitte": "circle in the middle",
    "Herz in der Mitte": "heart in the middle",
    "Stern in der Mitte": "star in the middle",
    "drei Punkte": "three dots",
    "Punkte an den Enden": "dots at the ends",
    "Pfeil": "arrow",
    "Doppelpfeil": "double arrow",
    "Blattranke": "leaf vine",
    "Art déco": "Art Deco",
    "Lorbeerzweig": "laurel branch",
    "Zweige zur Blüte": "branches to a blossom",
    "Blätter in der Mitte": "leaves in the middle",
    "Blütenranke": "blossom vine",
    "Blumenreihe": "row of flowers",
    "Gras mit Blumen": "grass with flowers",
    "Tulpen": "tulips",
    "Gänseblümchen": "daisies",
    "Rosmarinzweig": "rosemary sprig",
    "Blätter mit Adern": "veined leaves",
    "Bergkette": "mountain range",

    # --- Aufkleber-Kategorien (wie in der Marklife-App) -----------------------------------
    "Blumenladen-Geschenk": "Flower shop & gifts",
    "Achten Sie auf die Warnung": "Warnings",
    "Schmuck": "Jewelry",
    "Pflanze": "Plants",
    "Zahlen": "Numbers",
    "Sport": "Sports",
    "Medikamente": "Medicine",
    "Kleideraufbewahrung": "Clothes storage",
    "Schuh": "Shoes",
    "Kommunikationsstärke": "Communication",
    "Wetter": "Weather",
    "Mathematik": "Math",
    "digitale Geräte": "Digital devices",
    "Supermarkt": "Supermarket",
    "Marke": "Brands",
    "Baby Produkte": "Baby products",
    "Mutter und Kind": "Mother and child",
    "Meine Aufkleber": "My stickers",
}
