# -*- coding: utf-8 -*-
from kern.etikett import Barcode, Rahmen, Text


def _leiste():
    from gui.eigenschaften import Eigenschaften
    leiste = Eigenschaften()
    gemeldet = []
    leiste.geaendert.connect(lambda: gemeldet.append(True))
    return leiste, gemeldet


def test_zahl_schreibt_ins_element(qapp):
    leiste, gemeldet = _leiste()
    element = Rahmen()
    leiste.zeige(element)
    leiste.felder["x_mm"].setValue(7.5)
    assert element.x_mm == 7.5 and gemeldet


def test_textfelder(qapp):
    leiste, _ = _leiste()
    element = Text()
    leiste.zeige(element)
    assert {"inhalt", "schrift", "groesse_pt", "fett", "ausrichtung"} <= set(leiste.felder)
    leiste.felder["inhalt"].setPlainText("Zwei\nZeilen")
    leiste.felder["fett"].setChecked(True)
    leiste.felder["ausrichtung"].setCurrentIndex(1)
    assert element.inhalt == "Zwei\nZeilen"
    assert element.fett is True
    assert element.ausrichtung == "mitte"


def test_auswahlfeld_mit_zahlenwert(qapp):
    leiste, _ = _leiste()
    element = Barcode()
    leiste.zeige(element)
    leiste.felder["drehung"].setCurrentIndex(1)
    leiste.felder["art"].setCurrentIndex(1)
    assert element.drehung == 90 and element.art == "ean13"


def test_aktualisieren_ohne_signal(qapp):
    leiste, gemeldet = _leiste()
    element = Rahmen()
    leiste.zeige(element)
    element.x_mm = 3.0
    leiste.aktualisieren()
    assert leiste.felder["x_mm"].value() == 3.0
    assert gemeldet == []


def test_nichts_gewaehlt(qapp):
    leiste, _ = _leiste()
    leiste.zeige(Rahmen())
    leiste.zeige(None)
    assert leiste.felder == {} and leiste.element is None


def test_formknopf_oeffnet_galerie_fuer_rahmen_und_linie(qapp):
    from kern.etikett import Linie
    leiste, gemeldet = _leiste()
    gefragt = []
    leiste.form_waehlen = lambda art, jetzt, eltern: gefragt.append((art, jetzt)) or "wellen"
    rahmen = Rahmen()
    leiste.zeige(rahmen)
    leiste.felder["stil"].click()
    assert gefragt == [("rahmen", "einfach")]
    assert rahmen.stil == "wellen" and gemeldet
    assert "Wellenrand" in leiste.felder["stil"].text()        # Knopf zeigt die neue Form
    linie = Linie()
    leiste.zeige(linie)
    leiste.form_waehlen = lambda art, jetzt, eltern: None          # abgebrochen
    leiste.felder["stil"].click()
    assert linie.stil == "durchgezogen"
    linie.y_mm, linie.hoehe_mm = 5.5, 1.0
    leiste.form_waehlen = lambda art, jetzt, eltern: "ranke"       # braucht 4 mm
    leiste.felder["stil"].click()
    assert (linie.stil, linie.y_mm, linie.hoehe_mm) == ("ranke", 4.0, 4.0)
