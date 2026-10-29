# -*- coding: utf-8 -*-
"""Aussehen: Knoepfe als Knoepfe (Rahmen, Verlauf, Druckzustand) und kleine
Symbole fuer die Werkzeuge. Farben nach dem Programmsymbol: Creme und Schwarz."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap

STIL = """
QPushButton, QToolBar QToolButton, QToolButton#klein {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fffdf7, stop:1 #ece6d6);
    border: 1px solid #a9a290;
    border-bottom: 2px solid #8a8473;
    border-radius: 6px;
    padding: 4px 12px;
    color: #1d1d1d;
}
QPushButton:hover, QToolBar QToolButton:hover, QToolButton#klein:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f3eedf);
    border-color: #6f6a5c;
}
QPushButton:pressed, QToolBar QToolButton:pressed, QToolButton#klein:pressed {
    background: #e2dbc8;
    border-bottom: 1px solid #8a8473;
    padding-top: 5px;
}
QPushButton:disabled {
    background: #f1efe9;
    color: #9a978f;
    border-color: #cfcbc0;
}
QPushButton#haupt {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a3a3a, stop:1 #151515);
    border: 1px solid #000000;
    border-bottom: 2px solid #000000;
    color: #ffffff;
    font-weight: bold;
    padding: 5px 18px;
}
QPushButton#haupt:hover { background: #2c2c2c; }
QPushButton#haupt:pressed { background: #000000; padding-top: 6px; }
QPushButton#haupt:disabled { background: #b9b6ae; border-color: #a6a39b; color: #eeeeee; }
QToolBar { spacing: 6px; padding: 6px; }
QToolBar QToolButton { padding: 3px 8px; min-width: 104px; text-align: left; }
QToolButton#klein { padding: 2px 6px; }
"""


def anwenden(app):
    app.setStyleSheet(STIL)


# --- Werkzeug-Symbole ------------------------------------------------------------

def _stift(breite=3.0):
    stift = QPen(Qt.GlobalColor.black, breite)
    stift.setCapStyle(Qt.PenCapStyle.RoundCap)
    stift.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return stift


def _text(p):
    schrift = QFont("Georgia", 34, QFont.Weight.Bold)
    p.setFont(schrift)
    p.drawText(QRectF(0, 0, 48, 48), Qt.AlignmentFlag.AlignCenter, "T")


def _qr(p):
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(Qt.GlobalColor.black)
    for x, y in ((6, 6), (30, 6), (6, 30)):              # die drei Suchmarken
        p.drawRect(QRectF(x, y, 12, 12))
        p.setBrush(Qt.GlobalColor.white)
        p.drawRect(QRectF(x + 2.5, y + 2.5, 7, 7))
        p.setBrush(Qt.GlobalColor.black)
        p.drawRect(QRectF(x + 4.5, y + 4.5, 3, 3))
    for x, y in ((22, 8), (22, 16), (26, 22), (32, 26), (38, 30), (30, 34), (22, 38),
                 (38, 38), (26, 30), (34, 22), (8, 22), (16, 24)):
        p.drawRect(QRectF(x, y, 4, 4))


def _barcode(p):
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(Qt.GlobalColor.black)
    x = 6.0
    for breite in (2, 1, 3, 1, 2, 1, 1, 3, 2, 1, 2, 1, 3, 1):
        p.drawRect(QRectF(x, 9, breite * 1.3, 30))
        x += breite * 1.3 + 1.6


def _bild(p):
    p.setPen(_stift(2.5))
    p.drawRoundedRect(QRectF(5, 9, 38, 30), 3, 3)
    p.setBrush(Qt.GlobalColor.black)
    berg = QPainterPath(QPointF(7, 37))
    for x, y in ((18, 22), (24, 29), (31, 19), (41, 37)):
        berg.lineTo(x, y)
    berg.closeSubpath()
    p.drawPath(berg)
    p.drawEllipse(QPointF(14, 17), 3, 3)


def _aufkleber(p):
    p.setPen(_stift(2.5))
    p.setBrush(Qt.GlobalColor.black)
    ecken = []
    for i in range(10):
        r = 19 if i % 2 == 0 else 8
        w = math.radians(-90 + i * 36)
        ecken.append(QPointF(24 + r * math.cos(w), 25 + r * math.sin(w)))
    p.drawPolygon(ecken)


def _rahmen(p):
    p.setPen(_stift(2.5))
    p.drawRoundedRect(QRectF(5, 12, 38, 24), 4, 4)
    p.setPen(_stift(1.2))
    p.drawRect(QRectF(10, 16, 28, 16))
    p.setBrush(Qt.GlobalColor.black)
    for x, y in ((5, 12), (43, 12), (5, 36), (43, 36)):
        p.drawEllipse(QPointF(x, y), 3, 3)


def _linie(p):
    p.setPen(_stift(2.5))
    welle = QPainterPath(QPointF(4, 24))
    for i in range(4):
        x, y = 4 + i * 10, 16 if i % 2 == 0 else 32
        welle.cubicTo(x + 3, y, x + 7, y, x + 10, 24)
    p.drawPath(welle)
    p.setBrush(Qt.GlobalColor.black)
    p.drawEllipse(QPointF(44, 24), 2.5, 2.5)


def _serie(p):
    """Drei gestaffelte Etiketten, auf dem vordersten Zeilen wie aus einer Tabelle."""
    for versatz in (12, 6, 0):
        p.setPen(_stift(2.2))
        p.setBrush(Qt.GlobalColor.white)
        p.drawRoundedRect(QRectF(4 + versatz, 22 - versatz, 30, 20), 3, 3)
    p.setPen(_stift(2.4))
    for y, laenge in ((28, 20), (34, 14)):
        p.drawLine(QPointF(9, y), QPointF(9 + laenge, y))


SYMBOLE = {"text": _text, "qr": _qr, "barcode": _barcode, "bild": _bild,
           "aufkleber": _aufkleber, "rahmen": _rahmen, "linie": _linie, "serie": _serie}


def werkzeug_symbol(art):
    """48 x 48 Punkte, schwarz auf durchsichtig; unbekannte Arten bleiben leer."""
    bild = QPixmap(48, 48)
    bild.fill(Qt.GlobalColor.transparent)
    zeichnen = SYMBOLE.get(art)
    if zeichnen is not None:
        p = QPainter(bild)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        zeichnen(p)
        p.end()
    return QIcon(bild)
