# -*- coding: utf-8 -*-
from hilfen import FalscheVerbindung, warten
from kern.einstellungen import Einstellungen
from kern.etikett import Etikett, Text


def _csv(tmp_path):
    pfad = tmp_path / "s.csv"
    pfad.write_text("Name;Nummer\nAnna;1\nBernd;2\nCarla;3\n", encoding="utf-8")
    return pfad


def _dialog(inhalt="{{Name}}", verbindung=None):
    from gui.seriendruck import SerienDialog
    etikett = Etikett(30, 15, [Text(inhalt=inhalt, breite_mm=28, hoehe_mm=13)])
    dialog = SerienDialog(etikett, Einstellungen(port="COM13"), None,
                          verbindung or FalscheVerbindung())
    dialog.melden = lambda titel, text: dialog.meldungen.append(text)
    dialog.meldungen = []
    return dialog


def test_laden_und_vorschau(qapp, tmp_path):
    dialog = _dialog()
    assert dialog.lade(_csv(tmp_path))
    assert dialog.ansicht.rowCount() == 3 and dialog.ansicht.columnCount() == 2
    assert dialog.hinweis.text() == ""
    assert not dialog.vorschau.pixmap().isNull()
    assert (dialog.von.value(), dialog.bis.value()) == (1, 3)
    assert dialog.drucken_knopf.isEnabled()


def test_fehlender_platzhalter(qapp, tmp_path):
    dialog = _dialog("{{Nachname}}")
    dialog.lade(_csv(tmp_path))
    assert "{{Nachname}}" in dialog.hinweis.text()


def test_kaputte_datei(qapp, tmp_path):
    pfad = tmp_path / "leer.csv"
    pfad.write_text("", encoding="utf-8")
    dialog = _dialog()
    assert not dialog.lade(pfad)
    assert dialog.meldungen and "keine Zeilen" in dialog.meldungen[0]


def test_druck_zeilen_zwei_bis_drei(qapp, tmp_path):
    verbindung = FalscheVerbindung()
    dialog = _dialog(verbindung=verbindung)
    dialog.lade(_csv(tmp_path))
    dialog.von.setValue(2)
    dialog.kopien.setValue(2)
    dialog.starte_druck()
    warten(qapp, lambda: not dialog._faden.isRunning())
    assert len(verbindung.gesendet) == 4
    assert dialog.balken.value() == 4


def test_abriss_setzt_von_zum_weitermachen(qapp, tmp_path):
    dialog = _dialog(verbindung=FalscheVerbindung(kaputt_ab=1))
    dialog.lade(_csv(tmp_path))
    dialog.starte_druck()
    warten(qapp, lambda: not dialog._faden.isRunning())
    assert dialog.von.value() == 2
    assert "abgerissen" in dialog.meldungen[0]
