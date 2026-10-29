# -*- coding: utf-8 -*-
"""Zierlinien: Motiv in der Mitte, Pfeile, Schnoerkel, Ranke, Art deco."""

from __future__ import annotations

import math

from kern.formen import (blatt, halbhoch as _hub, mittellinie as durchgezogen, raute, scheibe,
                         spirale, strecke, zierstrich, zug)


def _mit_mitte(motiv, faktor=3):
    def zeichnen(z, b, h, s):
        r = _hub(h, s, faktor)
        mx, mitte = (b - 1) / 2, (h - s) // 2
        strecke(z, (0, mitte), (round(mx - r - 2 * s), mitte), s)
        strecke(z, (round(mx + r + 2 * s), mitte), (b - 1, mitte), s)
        motiv(z, mx, (h - 1) / 2, r, s)
    return zeichnen


def drei_punkte(z, b, h, s):
    r = _hub(h, s, 1)
    mx, mitte = (b - 1) / 2, (h - s) // 2
    strecke(z, (0, mitte), (round(mx - 6 * r), mitte), s)
    strecke(z, (round(mx + 6 * r), mitte), (b - 1, mitte), s)
    for x in (mx - 3 * r, mx, mx + 3 * r):
        scheibe(z, x, (h - 1) / 2, r)


def hantel(z, b, h, s):
    r = _hub(h, s, 1.5)
    durchgezogen(z, b, h, s)
    scheibe(z, r, (h - 1) / 2, r)
    scheibe(z, b - 1 - r, (h - 1) / 2, r)


def _spitze(z, x, m, laenge, hub, richtung):
    z.polygon([(x, m), (x - richtung * laenge, m - hub), (x - richtung * laenge, m + hub)], fill=0)


def pfeil(z, b, h, s):
    hub = _hub(h, s, 2)
    m = (h - 1) / 2
    strecke(z, (0, (h - s) // 2), (round(b - 1 - hub), (h - s) // 2), s)
    _spitze(z, b - 1, m, 2 * hub, hub, 1)


def doppelpfeil(z, b, h, s):
    hub = _hub(h, s, 2)
    m = (h - 1) / 2
    strecke(z, (round(hub), (h - s) // 2), (round(b - 1 - hub), (h - s) // 2), s)
    _spitze(z, b - 1, m, 2 * hub, hub, 1)
    _spitze(z, 0, m, 2 * hub, hub, -1)


def schnoerkel(z, b, h, s):
    """Kalligrafischer Trenner: Spiralen an den Enden, Raute in der Mitte."""
    hub = _hub(h, s, 4)
    rr = hub / 2
    w = zierstrich(s, rr)
    m = (h - 1) / 2
    a = 2 * rr + w
    mitte = round(m - w / 2)
    strecke(z, (round(a), mitte), (round(b - 1 - a), mitte), w)
    zug(z, spirale(a, m - rr, rr, 90, 1.3, 0.25), w)
    zug(z, spirale(b - 1 - a, m + rr, rr, -90, 1.3, 0.25), w)
    raute(z, (b - 1) / 2, m, hub * 0.8, hub * 0.5)


def ranke(z, b, h, s):
    """Blattranke: sanfte Welle mit Blaettern an den Bogenspitzen."""
    hub = _hub(h, s, 4)
    w = zierstrich(s, hub / 3)
    m = (h - 1) / 2
    periode = max(6 * hub, 24)
    welle_hub = hub * 0.3
    zug(z, [(x, m + welle_hub * math.sin(2 * math.pi * x / periode)) for x in range(b)], w)
    x, oben = periode / 4, False                 # dort liegt der untere Bogen
    while x < b - hub:
        y = m + welle_hub * (-1 if oben else 1)
        richtung = -1 if oben else 1                  # Blatt zeigt vom Bogen weg
        blatt(z, x - hub * 0.3, y, hub * 1.1, math.radians(richtung * 40))
        blatt(z, x + hub * 0.6, y, hub * 0.8, math.radians(richtung * 70))
        x, oben = x + periode / 2, not oben


def art_deco(z, b, h, s):
    """Art-deco-Trenner: drei Linien, die zur Raute in der Mitte laufen."""
    hub = _hub(h, s, 3)
    w = zierstrich(s, hub / 1.5)
    mx, m = (b - 1) / 2, (h - 1) / 2
    rr = hub
    mitte = round(m - w / 2)
    strecke(z, (0, mitte), (round(mx - rr - w), mitte), w)
    strecke(z, (round(mx + rr + w), mitte), (b - 1, mitte), w)
    for dy in (-hub * 0.7, hub * 0.7):
        y = round(m + dy - w / 2)
        strecke(z, (round(mx - (b - 1) * 0.3), y), (round(mx - rr * 0.6), y), w)
        strecke(z, (round(mx + rr * 0.6), y), (round(mx + (b - 1) * 0.3), y), w)
    raute(z, mx, m, rr * 0.6, rr)
