# -*- coding: utf-8 -*-
"""Bildschirmfotos fuer README und Anleitung, auf Deutsch und Englisch.

Aufruf: venv\\Scripts\\python.exe screenshots.py
Ergebnis: docs\\screenshots\\<sprache>-<ansicht>.png. Die Fenster werden mit
einem erfundenen P15 auf COM13 gebaut; Drucker und Einstellungen bleiben
unberuehrt (Einstellungen in einem Temp-Ordner).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))

from PySide6.QtCore import QEvent  # noqa: E402
from PySide6.QtGui import QIcon  # noqa: E402
from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

ZIEL = HIER / "docs" / "screenshots"
P15 = None


def _ruhig(app):
    """Ereignisse abarbeiten, auch das verzoegerte Loeschen alter Widgets."""
    for _ in range(3):
        app.processEvents()
        QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def _foto(app, fenster, name):
    fenster.show()
    _ruhig(app)
    fenster.grab().save(str(ZIEL / f"{name}.png"))
    fenster.close()


def _beispiel(fenster, texte):
    """Ein Etikett wie aus dem Alltag: Kraeuter-Glas mit Lorbeerkranz."""
    from kern import etikett as et
    fenster.leiste.groesse.setCurrentIndex(fenster.leiste.groesse.findData("40 x 12 mm"))
    b = fenster.etikett.breite_mm - fenster.e.rand_ende_mm
    fenster.etikett.elemente += [
        et.Rahmen(x_mm=0, y_mm=0, breite_mm=b, hoehe_mm=12, stil="kranz"),
        et.Text(x_mm=3, y_mm=2.5, breite_mm=b - 6, hoehe_mm=7, inhalt=texte,
                schrift="Segoe UI", groesse_pt=11, fett=True, ausrichtung="mitte"),
    ]
    fenster.flaeche.neu_zeichnen()
    fenster.flaeche.waehle(1)


def sprache_fotografieren(app, code, ordner):
    from gui.aufkleber import AufkleberDialog
    from gui.einrichtung import EinrichtungsAssistent
    from gui.fenster import Hauptfenster
    from gui.formen import FormenDialog
    from gui.sprachwahl import qt_uebersetzen
    from gui.ueber import text
    from hilfen import FalscheVerbindung
    from kern import aufkleber, sprache
    from kern.anschluss import Port
    from kern.sprache import t

    sprache.setze(code)
    qt_uebersetzen(app, code)
    p15 = Port("COM13", "P15_ZF39F (COM13)", True)
    fenster = Hauptfenster(ordner / f"{code}.json", lambda: [p15], FalscheVerbindung())
    fenster.resize(1180, 560)
    _beispiel(fenster, "Basilikum" if code == "de" else "Basil")
    _foto(app, fenster, f"{code}-hauptfenster")

    _foto(app, FormenDialog("rahmen"), f"{code}-rahmen")
    _foto(app, FormenDialog("linie"), f"{code}-linien")
    dialog = AufkleberDialog(aufkleber.katalog())
    dialog.kategorien.setCurrentRow(3)
    _foto(app, dialog, f"{code}-aufkleber")

    assistent = EinrichtungsAssistent(lambda: [p15], oeffnen=lambda: None)
    assistent.show()
    _ruhig(app)
    assistent.koppeln.suchen()
    _foto(app, assistent, f"{code}-einrichtung")

    kasten = QMessageBox()
    kasten.setWindowTitle(t("Über Etikettendrucker"))
    kasten.setText(text())
    from gui.ueber import SYMBOL
    from PySide6.QtGui import QPixmap
    kasten.setIconPixmap(QPixmap(str(SYMBOL)).scaled(96, 96))
    _foto(app, kasten, f"{code}-ueber")


def main():
    ZIEL.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(HIER / "tests"))            # FalscheVerbindung
    app = QApplication(sys.argv)
    from gui import aussehen
    from gui.app import SYMBOL
    from gui.sprachwahl import SprachDialog
    app.setWindowIcon(QIcon(str(SYMBOL)))
    aussehen.anwenden(app)
    with tempfile.TemporaryDirectory() as ordner:
        for code in ("de", "en"):
            sprache_fotografieren(app, code, Path(ordner))
    _foto(app, SprachDialog("en"), "sprachwahl")
    print(f"Fertig: {ZIEL}")


if __name__ == "__main__":
    main()
