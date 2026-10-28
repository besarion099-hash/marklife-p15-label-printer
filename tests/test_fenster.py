# -*- coding: utf-8 -*-
import pytest

from hilfen import FalscheVerbindung, warten
from kern.anschluss import Port

P15 = Port("COM13", "P15_ZF39F (COM13)", True)


def _fenster(tmp_path, verbindung=None, gefunden=(P15,)):
    from gui.fenster import Hauptfenster
    fenster = Hauptfenster(tmp_path / "e.json", lambda: list(gefunden),
                           verbindung or FalscheVerbindung())
    fenster.melden = lambda titel, text: pytest.fail(f"{titel}: {text}")
    return fenster


def test_neues_element_wird_gewaehlt(qapp, tmp_path):
    fenster = _fenster(tmp_path)
    fenster.neues_element("text")
    assert len(fenster.etikett.elemente) == 1
    assert fenster.flaeche.auswahl == 0
    assert fenster.eigenschaften.element is fenster.etikett.elemente[0]


def test_alle_werkzeuge_ausser_bild(qapp, tmp_path):
    fenster = _fenster(tmp_path)
    for art in ("text", "qr", "barcode", "rahmen", "linie"):
        fenster.neues_element(art)
    assert len(fenster.etikett.elemente) == 5
    assert fenster.flaeche.fehler == {}


def test_drucken_sendet_ein_etikett(qapp, tmp_path):
    verbindung = FalscheVerbindung()
    fenster = _fenster(tmp_path, verbindung)
    fenster.neues_element("text")
    fenster.drucken()
    warten(qapp, lambda: not fenster._faden.isRunning())
    assert verbindung.port == "COM13"
    assert len(verbindung.gesendet) == 1
    assert verbindung.gesendet[0][:8] == bytes.fromhex("10FFF102 1F70010A")
    assert (tmp_path / "e.json").exists()


def test_groesse_aendern_passt_etikett_an(qapp, tmp_path):
    fenster = _fenster(tmp_path)
    fenster.leiste.groesse.setCurrentText("50 x 15 mm")
    assert (fenster.etikett.breite_mm, fenster.etikett.hoehe_mm) == (50.0, 15.0)


def test_vorlage_speichern_und_oeffnen(qapp, tmp_path):
    erstes = _fenster(tmp_path)
    erstes.leiste.groesse.setCurrentText("40 x 12 mm")
    erstes.neues_element("rahmen")
    erstes.speichern_pfad(tmp_path / "a.etikett.json")
    zweites = _fenster(tmp_path)
    zweites.oeffnen_pfad(tmp_path / "a.etikett.json")
    assert zweites.etikett == erstes.etikett
    assert zweites.leiste.groesse.currentText() == "40 x 12 mm"
    assert zweites.pfad.name == "a.etikett.json"


def test_kaputte_vorlage_wird_gemeldet(qapp, tmp_path):
    pfad = tmp_path / "kaputt.etikett.json"
    pfad.write_text("{", encoding="utf-8")
    fenster = _fenster(tmp_path)
    meldungen = []
    fenster.melden = lambda titel, text: meldungen.append(text)
    fenster.oeffnen_pfad(pfad)
    assert meldungen and fenster.pfad is None


def test_neue_elemente_bleiben_im_bedruckbaren_teil(qapp, tmp_path):
    fenster = _fenster(tmp_path)
    fenster.leiste.groesse.setCurrentText("40 x 12 mm")
    for art in ("text", "barcode", "rahmen", "linie"):
        fenster.neues_element(art)
    assert not any(fenster.flaeche.ausserhalb(e) for e in fenster.etikett.elemente)
