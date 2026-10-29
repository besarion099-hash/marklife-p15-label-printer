# -*- coding: utf-8 -*-
"""Menuepunkt "Über": wer das Programm wann gemacht hat, und die Version."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QMessageBox

VERSION = "1.0"
STAND = "29.10.2026"            # Datum dieser Version
BEGONNEN = "28.10.2026"
AUTOR = "Besarion"
MITARBEIT = "Claude (Anthropic) über Claude Code"
SYMBOL = Path(__file__).resolve().parent / "symbol.png"


def text():
    return (f"<h3>Etikettendrucker {VERSION}</h3>"
            "<p>Etiketten gestalten und auf dem Marklife P15 drucken.</p>"
            "<table cellspacing='4'>"
            f"<tr><td><b>Version:</b></td><td>{VERSION} vom {STAND}</td></tr>"
            f"<tr><td><b>Gemacht von:</b></td><td>{AUTOR}</td></tr>"
            f"<tr><td><b>Programmiert mit:</b></td><td>{MITARBEIT}</td></tr>"
            f"<tr><td><b>Begonnen:</b></td><td>{BEGONNEN}</td></tr>"
            "</table>"
            "<p style='color:#666'>Aufkleber-Symbole: Tabler Icons (MIT-Lizenz).</p>")


def ueber_zeigen(eltern):
    kasten = QMessageBox(eltern)
    kasten.setWindowTitle("Über Etikettendrucker")
    kasten.setTextFormat(Qt.TextFormat.RichText)
    kasten.setText(text())
    bild = QPixmap(str(SYMBOL))
    if not bild.isNull():
        kasten.setIconPixmap(bild.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation))
    kasten.exec()
