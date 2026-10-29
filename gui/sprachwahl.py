# -*- coding: utf-8 -*-
"""Sprache waehlen beim ersten Start, und Qts eigene Texte (Ja/Nein, OK,
Abbrechen in Standard-Dialogen) in derselben Sprache."""

from __future__ import annotations

from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from kern import sprache

_uebersetzer = []                     # Python-Referenz halten, sonst raeumt Qt ihn ab


class SprachDialog(QDialog):
    """Zwei grosse Knoepfe; zweisprachig, weil die Sprache noch unbekannt ist."""

    def __init__(self, vorschlag="de", eltern=None):
        super().__init__(eltern)
        self.setWindowTitle("Sprache / Language")
        self.gewaehlt = vorschlag
        frage = QLabel("Bitte die Sprache wählen.\nPlease choose your language.")
        knoepfe = QHBoxLayout()
        for code, name in sprache.SPRACHEN:
            knopf = QPushButton(name)
            knopf.setMinimumSize(150, 48)
            knopf.setAutoDefault(code == vorschlag)
            knopf.setDefault(code == vorschlag)
            knopf.clicked.connect(lambda *_, c=code: self._waehlen(c))
            knoepfe.addWidget(knopf)
        spalte = QVBoxLayout(self)
        spalte.addWidget(frage)
        spalte.addSpacing(8)
        spalte.addLayout(knoepfe)
        spalte.addSpacing(4)
        spalte.addWidget(QLabel("<small>Später änderbar: Menü „Sprache / Language“.<br>"
                                "Can be changed later in the “Sprache / Language” menu."
                                "</small>"))

    def _waehlen(self, code):
        self.gewaehlt = code
        self.accept()


def sprache_fragen(vorschlag="de") -> str:
    """Gewaehlte Sprache; wird das Fenster geschlossen, gilt der Vorschlag."""
    dialog = SprachDialog(vorschlag)
    dialog.exec()
    return dialog.gewaehlt


def qt_uebersetzen(app, code: str) -> None:
    """Qts mitgelieferte Uebersetzung (qtbase_de.qm) laden oder entfernen, dazu das
    Zahlenformat (Komma oder Punkt) fuer alle danach gebauten Felder."""
    QLocale.setDefault(QLocale(QLocale.Language.English if code == "en"
                               else QLocale.Language.German))
    while _uebersetzer:
        app.removeTranslator(_uebersetzer.pop())
    if code == "en":
        return                         # Qt ist von Haus aus Englisch
    uebersetzer = QTranslator(app)
    ordner = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if uebersetzer.load(f"qtbase_{code}", ordner):
        app.installTranslator(uebersetzer)
        _uebersetzer.append(uebersetzer)
