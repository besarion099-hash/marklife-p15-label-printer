# -*- coding: utf-8 -*-
"""Verzeichnis der Rahmen- und Linienformen (Zeichnen: kern.rahmenformen,
kern.linienformen; Grundregeln fuer Thermodruck: kern.formen)."""

from __future__ import annotations

from kern import linienformen, rahmenformen
from kern.formen import MIN_PUNKTE, staerke  # noqa: F401  (frueher hier zu Hause)

RAHMENSTILE = [(name, text) for name, text, _ in rahmenformen.FORMEN]
LINIENSTILE = [(name, text) for name, text, _ in linienformen.FORMEN]
LINIE_HOEHE_MM = linienformen.HOEHE_MM

_RAHMEN = {name: zeichner for name, _, zeichner in rahmenformen.FORMEN}
_LINIEN = {name: zeichner for name, _, zeichner in linienformen.FORMEN}


def rahmen(zeichner, breite, hoehe, s, ecken, stil):
    """Rahmen in eine Flaeche breite x hoehe zeichnen (Masse in Punkten).
    Unbekannte Stile zeichnen einfach."""
    _RAHMEN.get(stil, rahmenformen.einfach)(zeichner, breite, hoehe, staerke(s), ecken)


def linie(zeichner, breite, hoehe, s, stil):
    """Waagerechte Linie mittig in eine Flaeche breite x hoehe zeichnen."""
    _LINIEN.get(stil, linienformen.durchgezogen)(zeichner, breite, hoehe,
                                                 min(hoehe, staerke(s)))
