# -*- coding: utf-8 -*-
"""Menuepunkt "Über": wer das Programm wann gemacht hat, und die Version."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QMessageBox

from kern import sprache
from kern.sprache import t

VERSION = "1.1"
STAND = date(2026, 10, 29)            # Datum dieser Version
BEGONNEN = date(2026, 10, 28)
AUTOR = "Besarion"
MITARBEIT = "Claude (Anthropic), Claude Code"
GITHUB = "https://github.com/besarion099-hash/marklife-p15-label-printer"
SYMBOL = Path(__file__).resolve().parent / "symbol.png"


def datum(tag: date) -> str:
    return tag.strftime("%d.%m.%Y") if sprache.aktuell() == "de" else tag.isoformat()


def text():
    return (f"<h3>{t('Etikettendrucker')} {VERSION}</h3>"
            f"<p>{t('Etiketten gestalten und auf dem Marklife P15 drucken.')}</p>"
            "<table cellspacing='4'>"
            f"<tr><td><b>{t('Version:')}</b></td>"
            f"<td>{t('{version} vom {datum}', version=VERSION, datum=datum(STAND))}</td></tr>"
            f"<tr><td><b>{t('Gemacht von:')}</b></td><td>{AUTOR}</td></tr>"
            f"<tr><td><b>{t('Programmiert mit:')}</b></td><td>{MITARBEIT}</td></tr>"
            f"<tr><td><b>{t('Begonnen:')}</b></td><td>{datum(BEGONNEN)}</td></tr>"
            f"<tr><td><b>GitHub:</b></td><td><a href='{GITHUB}'>{GITHUB[8:]}</a></td></tr>"
            "</table>"
            f"<p style='color:#666'>{t('Aufkleber-Symbole: Tabler Icons (MIT-Lizenz).')}</p>")


def ueber_zeigen(eltern):
    kasten = QMessageBox(eltern)
    kasten.setWindowTitle(t("Über Etikettendrucker"))
    kasten.setTextFormat(Qt.TextFormat.RichText)
    kasten.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
    kasten.setText(text())
    bild = QPixmap(str(SYMBOL))
    if not bild.isNull():
        kasten.setIconPixmap(bild.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation))
    kasten.exec()
