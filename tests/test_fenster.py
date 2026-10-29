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


def test_text_und_qr_ueberlappen_nicht(qapp, tmp_path):
    fenster = _fenster(tmp_path)
    fenster.leiste.groesse.setCurrentText("40 x 12 mm")
    fenster.neues_element("text")
    fenster.neues_element("qr")
    text, qr = fenster.etikett.elemente
    text.breite_mm = qr.x_mm - 2                     # Text links daneben
    assert qr.x_mm + qr.breite_mm <= 40 - fenster.e.rand_ende_mm
    assert not fenster.flaeche.ausserhalb(qr)


def test_startordner_ist_dokumente_ohne_letzten_ordner(tmp_path):
    from pathlib import Path
    from gui.bilder import startordner
    from kern.einstellungen import Einstellungen
    assert startordner(Einstellungen()) == str(Path.home() / "Documents")
    assert startordner(Einstellungen(letzter_ordner=str(tmp_path))) == str(tmp_path)
    assert startordner(Einstellungen(letzter_ordner=str(tmp_path / "weg"))) == str(Path.home() / "Documents")


def test_werkzeug_rahmen_und_linie_fragen_die_form(qapp, tmp_path):
    from gui.fenster import Hauptfenster
    fenster = Hauptfenster(einstellungen_pfad=tmp_path / "e.json", port_quelle=lambda: [])
    antworten = iter(["briefmarke", "ranke", None])
    fenster.form_waehlen = lambda art, jetzt, eltern: next(antworten)
    fenster._werkzeug("rahmen")
    fenster._werkzeug("linie")
    fenster._werkzeug("linie")                                  # abgebrochen: nichts neu
    rahmen, linie = fenster.etikett.elemente
    assert rahmen.stil == "briefmarke"
    assert linie.stil == "ranke" and linie.hoehe_mm == 4.0      # Zierlinie bekommt Platz
    assert abs(linie.y_mm + linie.hoehe_mm / 2 - fenster.etikett.hoehe_mm / 2) < 1e-9


def test_galerie_zeigt_alle_formen(qapp):
    from gui.formen import FormenDialog
    from kern import stile
    dialog = FormenDialog("linie", jetzt="welle")
    assert dialog.raster.count() == len(stile.LINIENSTILE)
    assert dialog.raster.currentItem().text() == "Welle"
    dialog._gewaehlt(dialog.raster.item(3))
    assert dialog.gewaehlt == stile.LINIENSTILE[3][0]


def test_menue_ueber_zeigt_version_und_autor(qapp, tmp_path, monkeypatch):
    from gui import fenster as modul
    from gui.ueber import text
    gezeigt = []
    monkeypatch.setattr(modul, "ueber_zeigen", lambda eltern: gezeigt.append(eltern))
    fenster = _fenster(tmp_path)
    ueber = [a for a in fenster.menuBar().actions() if a.text().replace("&", "") == "Über"]
    assert len(ueber) == 1 and ueber[0].menu() is None      # direkt anklickbar
    ueber[0].trigger()
    assert gezeigt == [fenster]
    assert "1.0" in text() and "Besarion" in text() and "29.10.2026" in text()


def test_werkzeuge_haben_symbole(qapp, tmp_path):
    from PySide6.QtWidgets import QToolBar
    fenster = _fenster(tmp_path)
    leiste = fenster.findChild(QToolBar)
    knoepfe = [a for a in leiste.actions() if not a.isSeparator()]
    assert all(not a.icon().isNull() for a in knoepfe)
    assert knoepfe[-1].text() == "Serien-Druck …"
    assert fenster.leiste.knopf.objectName() == "haupt"
    assert not fenster.leiste.knopf.icon().isNull() and fenster.leiste.knopf.text().strip() == "Drucken"


def test_bild_nimmt_fehlerverteilung(qapp, tmp_path, monkeypatch):
    from gui import fenster as modul
    monkeypatch.setattr(modul.QFileDialog, "getOpenFileName",
                        staticmethod(lambda *a, **k: (str(tmp_path / "foto.png"), "")))
    monkeypatch.setattr(modul, "bild_lesen", lambda pfad, eltern: b"png")
    fenster = _fenster(tmp_path)
    fenster.neues_element("bild")
    assert fenster.etikett.elemente[0].verfahren == "fehlerverteilung"


def test_einrichten_uebernimmt_den_port(qapp, tmp_path):
    zweiter = Port("COM20", "P15_AB12C (COM20)", True)
    fenster = _fenster(tmp_path, gefunden=(P15, zweiter))

    class Fertig:
        port = zweiter

        def exec(self):
            return True
    fenster.assistent_bauen = lambda eltern: Fertig()
    fenster.einrichten()
    assert fenster.e.port == "COM20"
    assert fenster.leiste.port.currentData() == "COM20"
    assert (tmp_path / "e.json").exists()


def test_erster_start_ohne_drucker_bietet_assistent_an(qapp, tmp_path):
    assert _fenster(tmp_path / "a", gefunden=()).erster_start_ohne_drucker()
    assert not _fenster(tmp_path / "b").erster_start_ohne_drucker()      # P15 gekoppelt
