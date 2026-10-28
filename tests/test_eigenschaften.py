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


def test_stilauswahl_fuer_rahmen_und_linie(qapp):
    from kern.etikett import Linie
    leiste, gemeldet = _leiste()
    rahmen = Rahmen()
    leiste.zeige(rahmen)
    feld = leiste.felder["stil"]
    feld.setCurrentIndex(feld.findData("wellen"))
    assert rahmen.stil == "wellen" and gemeldet
    linie = Linie()
    leiste.zeige(linie)
    feld = leiste.felder["stil"]
    assert feld.count() == 8
    feld.setCurrentIndex(feld.findData("ornament"))
    assert linie.stil == "ornament"
