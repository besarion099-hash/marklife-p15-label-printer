# -*- coding: utf-8 -*-
"""Rahmen aus wiederholten Mustern: Wellen, Zacken, Perforation, Kordel,
Schienen und Motive ringsum (Perlen, Kreise, Sterne, Herzen)."""

from __future__ import annotations

from kern.formen import (ECKEN, MIN_PUNKTE, gespiegelt, herz, ring, ringsum, scheibe, stern,
                         strecke, verteilt, zierstrich, zug)


def wellen(z, b, h, s, r):
    """Bogenkante: Halbkreise nach aussen, die Ecken bleiben geschlossen."""
    rr = max(6 * s, 12) // 2
    d = 2 * rr
    innen = [rr, rr, b - 1 - rr, h - 1 - rr]
    if innen[2] <= innen[0] or innen[3] <= innen[1]:
        z.rectangle([0, 0, b - 1, h - 1], outline=0, width=s)
        return
    nx = max(1, round((innen[2] - innen[0]) / d))
    ny = max(1, round((innen[3] - innen[1]) / d))
    bx, by = (innen[2] - innen[0]) / nx, (innen[3] - innen[1]) / ny
    for i in range(nx):
        x = innen[0] + i * bx
        z.arc([x, 0, x + bx, 2 * rr], 180, 360, fill=0, width=s)
        z.arc([x, h - 1 - 2 * rr, x + bx, h - 1], 0, 180, fill=0, width=s)
    for i in range(ny):
        y = innen[1] + i * by
        z.arc([0, y, 2 * rr, y + by], 90, 270, fill=0, width=s)
        z.arc([b - 1 - 2 * rr, y, b - 1, y + by], 270, 90, fill=0, width=s)


def zacken(z, b, h, s, r):
    hub = max(3 * s, 8)
    e = s / 2
    for von, bis, quer, innen, waagerecht in ((hub, b - 1 - hub, e, hub, True),
                                              (hub, b - 1 - hub, h - 1 - e, h - 1 - hub, True),
                                              (hub, h - 1 - hub, e, hub, False),
                                              (hub, h - 1 - hub, b - 1 - e, b - 1 - hub, False)):
        punkte = []
        for i, t in enumerate(verteilt(von, bis, hub)):
            q = quer if i % 2 == 0 else innen
            punkte.append((t, q) if waagerecht else (q, t))
        zug(z, punkte, s)
    for rechts, unten in ECKEN:
        zug(z, gespiegelt([(hub, e), (e, e), (e, hub)], b, h, rechts, unten), s)


def briefmarke(z, b, h, s, r):
    band = max(2 * s, 6)
    z.rectangle([0, 0, b - 1, h - 1], outline=0, width=band)
    loch = band * 0.6
    for x, y in ringsum(b, h, 0, band * 2):
        z.ellipse([x - loch, y - loch, x + loch, y + loch], fill=255)


def kordel(z, b, h, s, r):
    band = max(3 * s, 8)
    w = zierstrich(s, band / 2)
    for t in range(0, b - band, max(w * 3, 6)):
        z.line([(t, band - 1), (t + band, 0)], fill=0, width=w)
        z.line([(t, h - 1), (t + band, h - band)], fill=0, width=w)
    for t in range(0, h - band, max(w * 3, 6)):
        z.line([(0, t + band), (band - 1, t)], fill=0, width=w)
        z.line([(b - band, t + band), (b - 1, t)], fill=0, width=w)


def schienen(z, b, h, s, r):
    band = max(3 * s, 8)
    w = MIN_PUNKTE
    z.rectangle([0, 0, b - 1, h - 1], outline=0, width=w)
    z.rectangle([band - w, band - w, b - band + w - 1, h - band + w - 1], outline=0, width=w)
    for x in verteilt(band, b - 1 - band, 3 * w + 2):
        strecke(z, (round(x), 0), (round(x), band - 1), w)
        strecke(z, (round(x), h - band), (round(x), h - 1), w)
    for y in verteilt(band, h - 1 - band, 3 * w + 2):
        strecke(z, (0, round(y)), (band - 1, round(y)), w)
        strecke(z, (b - band, round(y)), (b - 1, round(y)), w)


def _reihum(z, b, h, groesse, motiv, abstand=2.4):
    for x, y in ringsum(b, h, groesse, groesse * abstand):
        motiv(z, x, y, groesse)


def perlen(z, b, h, s, r):
    _reihum(z, b, h, max(s, 3), scheibe, 2.6)


def kreise(z, b, h, s, r):
    _reihum(z, b, h, max(2 * s, 6), lambda z_, x, y, g: ring(z_, x, y, g, MIN_PUNKTE), 2.2)


def sterne(z, b, h, s, r):
    _reihum(z, b, h, max(2 * s, 6), stern)


def herzen(z, b, h, s, r):
    _reihum(z, b, h, max(2 * s, 6), herz)
