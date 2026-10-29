# -*- coding: utf-8 -*-
import ast
import string
from pathlib import Path

import pytest

from kern import sprache
from kern.sprache_en import EN

WURZEL = Path(__file__).resolve().parent.parent


def markierte_texte():
    """Alle Texte in t("...") und N_("...") im Programmcode."""
    gefunden = {}
    for datei in sorted((WURZEL / "kern").glob("*.py")) + sorted((WURZEL / "gui").glob("*.py")):
        baum = ast.parse(datei.read_text(encoding="utf-8"))
        for knoten in ast.walk(baum):
            if (isinstance(knoten, ast.Call) and isinstance(knoten.func, ast.Name)
                    and knoten.func.id in ("t", "N_") and knoten.args
                    and isinstance(knoten.args[0], ast.Constant)
                    and isinstance(knoten.args[0].value, str)):
                gefunden.setdefault(knoten.args[0].value, f"{datei.name}:{knoten.lineno}")
    return gefunden


def anzeige_namen():
    """Namen, die aus Datenlisten kommen: Formen und Aufkleber-Kategorien."""
    from kern import aufkleber, stile
    namen = [text for _, text in stile.RAHMENSTILE + stile.LINIENSTILE]
    namen += [name for name, _, _ in aufkleber.KATEGORIEN]
    return namen + [aufkleber.EIGENE]


def platzhalter(text):
    return {feld for _, feld, _, _ in string.Formatter().parse(text) if feld}


def test_jeder_markierte_text_hat_englisch():
    fehlend = {text: ort for text, ort in markierte_texte().items() if text not in EN}
    assert not fehlend, "\n".join(f"{ort}: {text!r}" for text, ort in fehlend.items())


def test_formen_und_kategorien_haben_englisch():
    fehlend = sorted({name for name in anzeige_namen() if name not in EN})
    assert not fehlend, fehlend


def test_platzhalter_stimmen_ueberein():
    falsch = [text for text, englisch in EN.items() if platzhalter(text) != platzhalter(englisch)]
    assert not falsch, falsch


def test_keine_verwaisten_uebersetzungen():
    benutzt = set(markierte_texte()) | set(anzeige_namen())
    verwaist = sorted(set(EN) - benutzt)
    assert not verwaist, verwaist


@pytest.fixture
def englisch():
    sprache.setze("en")
    yield
    sprache.setze("de")


def test_t_uebersetzt_und_setzt_ein(englisch):
    assert sprache.t("Drucken") == "Print"
    assert sprache.t("Unbekannter Text {x}", x=1) == "Unbekannter Text 1"


def test_unbekannte_sprache_ist_deutsch():
    sprache.setze("fr")
    assert sprache.aktuell() == "de" and sprache.t("Drucken") == "Drucken"


def test_einstellung_sprache_wird_geprueft(tmp_path):
    import json
    from kern import einstellungen
    pfad = tmp_path / "e.json"
    pfad.write_text(json.dumps({"sprache": "fr"}), encoding="utf-8")
    assert einstellungen.laden(pfad).sprache == ""
    einstellungen.sprache_setzen("en", pfad)
    assert einstellungen.laden(pfad).sprache == "en"


def _fenster(tmp_path):
    from gui.fenster import Hauptfenster
    from hilfen import FalscheVerbindung
    return Hauptfenster(tmp_path / "e.json", lambda: [], FalscheVerbindung())


def test_fenster_auf_englisch(qapp, tmp_path, englisch):
    from PySide6.QtWidgets import QToolBar
    fenster = _fenster(tmp_path)
    menues = [a.text() for a in fenster.menuBar().actions()]
    assert menues == ["&File", "&Printer", "Sprache / &Language", "&About"]
    knoepfe = [a.text() for a in fenster.findChild(QToolBar).actions() if not a.isSeparator()]
    assert knoepfe[0] == "Text" and knoepfe[-1] == "Batch print …"
    assert fenster.leiste.knopf.text().strip() == "Print"
    assert fenster.windowTitle() == "Label Printer – new label"
    fenster.neues_element("rahmen")
    assert fenster.eigenschaften.felder["stil"].text() == "simple …"


def test_sprachwechsel_meldet_und_merkt_sich(qapp, tmp_path):
    from kern import einstellungen
    fenster = _fenster(tmp_path)
    gemeldet = []
    fenster.sprache_gewechselt.connect(lambda: gemeldet.append(True))
    try:
        fenster.sprache_waehlen("en")
        assert gemeldet == [True] and sprache.aktuell() == "en"
        assert einstellungen.laden(tmp_path / "e.json").sprache == "en"
        fenster.sprache_waehlen("en")                     # gleiche Sprache: nichts tun
        assert gemeldet == [True]
    finally:
        sprache.setze("de")


def test_neues_fenster_uebernimmt_das_etikett(qapp, tmp_path):
    alt = _fenster(tmp_path)
    alt.leiste.groesse.setCurrentText("50 x 15 mm")
    alt.neues_element("text")
    alt.pfad = tmp_path / "x.etikett.json"
    neu = _fenster(tmp_path)
    neu.uebernehmen_von(alt)
    assert neu.etikett is alt.etikett and neu.flaeche.auswahl == 0
    assert neu.leiste.groesse_mm() == (50.0, 15.0)
    assert "x.etikett.json" in neu.windowTitle()


def test_sprachdialog_liefert_die_wahl(qapp):
    from gui.sprachwahl import SprachDialog
    dialog = SprachDialog("en")
    assert dialog.gewaehlt == "en"
    dialog._waehlen("de")
    assert dialog.gewaehlt == "de"
