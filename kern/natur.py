# -*- coding: utf-8 -*-
"""Naturmotive: Pilze, Tulpen, Gaensebluemchen, Lavendel, Rosmarin, Blaetter
mit Adern, Tannen, Berge und Sonne - als Bausteine und als Linien.

Motive mit Boden (Pilz, Tulpe, Tanne, Lavendel) stehen auf der Unterkante.
"""

from __future__ import annotations

import math

from kern.formen import MIN_PUNKTE, blatt, halbhoch, zierstrich, zug
from kern.pflanzen import _zufall


# --- Bausteine -----------------------------------------------------------------

def pilz(z, x, boden, g, fliegenpilz=True):
    """Pilz mit Hutbreite 2g; Fliegenpilz: dunkler Hut mit hellen Punkten,
    sonst heller Hut mit Rand (Steinpilz)."""
    sw, sh, ch = g * 0.55, g * 0.7, g * 0.8
    z.rounded_rectangle([x - sw / 2, boden - sh, x + sw / 2, boden], radius=sw / 3,
                        outline=0, width=MIN_PUNKTE)
    hut = [x - g, boden - sh - ch, x + g, boden - sh + ch]
    if fliegenpilz:
        z.pieslice(hut, 180, 360, fill=0)
        for dx, dy in ((-0.5, 0.3), (0.05, 0.62), (0.5, 0.3)):
            r = max(MIN_PUNKTE, g * 0.13)
            z.ellipse([x + dx * g - r, boden - sh - dy * ch - r, x + dx * g + r,
                       boden - sh - dy * ch + r], fill=255)
    else:
        z.pieslice(hut, 180, 360, fill=255, outline=0, width=max(MIN_PUNKTE, round(g / 5)))
        z.line([(x - g, boden - sh), (x + g, boden - sh)], fill=0, width=MIN_PUNKTE)


def tulpe(z, x, boden, hoehe, w=MIN_PUNKTE):
    oben = boden - hoehe
    kelch_h, kelch_b = hoehe * 0.36, hoehe * 0.34
    zug(z, [(x, boden), (x, oben + kelch_h * 0.8)], w)
    blatt(z, x, boden - hoehe * 0.05, hoehe * 0.5, math.radians(-62), 0.22)
    blatt(z, x, boden - hoehe * 0.05, hoehe * 0.42, math.radians(-118), 0.22)
    l, r = x - kelch_b / 2, x + kelch_b / 2
    z.polygon([(l, oben + kelch_h * 0.05), (x - kelch_b * 0.18, oben + kelch_h * 0.38), (x, oben),
               (x + kelch_b * 0.18, oben + kelch_h * 0.38), (r, oben + kelch_h * 0.05),
               (r, oben + kelch_h * 0.65), (x + kelch_b * 0.3, oben + kelch_h * 0.95),
               (x, oben + kelch_h), (x - kelch_b * 0.3, oben + kelch_h * 0.95),
               (l, oben + kelch_h * 0.65)], fill=0)


def gaensebluemchen(z, x, y, r):
    for i in range(12):
        w = math.radians(i * 30)
        blatt(z, x + math.cos(w) * r * 0.25, y + math.sin(w) * r * 0.25, r * 0.75, w, 0.17)
    z.ellipse([x - r * 0.36, y - r * 0.36, x + r * 0.36, y + r * 0.36], fill=255)
    z.ellipse([x - r * 0.28, y - r * 0.28, x + r * 0.28, y + r * 0.28], outline=0,
              width=MIN_PUNKTE)


def lavendel(z, x, boden, hoehe, neigung=0.0):
    """Lavendelhalm: Stiel, oben kleine Bluetenknospen abwechselnd links/rechts."""
    spitze = (x + neigung * hoehe, boden - hoehe)
    zug(z, [(x, boden), spitze], MIN_PUNKTE)
    rx = min(max(MIN_PUNKTE, hoehe * 0.05), 2.5)        # Knospen bleiben klein
    ry = rx * 1.5
    anzahl = max(7, round(hoehe * 0.55 / (ry * 1.6)))
    for i in range(anzahl):
        t = 0.45 + 0.55 * i / (anzahl - 1)
        px, py = x + (spitze[0] - x) * t, boden + (spitze[1] - boden) * t
        seite = -1 if i % 2 else 1
        px += seite * rx * 0.8 * (1 - 0.4 * i / (anzahl - 1))
        z.ellipse([px - rx, py - ry, px + rx, py + ry], fill=0)


def ader_blatt(z, x, y, laenge, winkel):
    """Blatt mit heller Mittelader und Seitenadern."""
    blatt(z, x, y, laenge, winkel, 0.3)
    dx, dy = math.cos(winkel), math.sin(winkel)
    zug_weiss = [(x + dx * laenge * 0.12, y + dy * laenge * 0.12),
                 (x + dx * laenge * 0.85, y + dy * laenge * 0.85)]
    z.line(zug_weiss, fill=255, width=MIN_PUNKTE)
    for t in ((0.35, 0.55, 0.72) if laenge >= 24 else (0.5,)):
        px, py = x + dx * laenge * t, y + dy * laenge * t
        for seite in (-1, 1):
            w = winkel + seite * math.radians(45)
            lang = laenge * 0.22 * (1 - t * 0.4)
            z.line([(px, py), (px + math.cos(w) * lang, py + math.sin(w) * lang)], fill=255,
                   width=MIN_PUNKTE)


def tanne(z, x, boden, hoehe):
    stamm_b, stamm_h = max(MIN_PUNKTE, hoehe * 0.09), hoehe * 0.12
    z.rectangle([x - stamm_b / 2, boden - stamm_h, x + stamm_b / 2, boden], fill=0)
    for unten, breit, spitze in ((stamm_h, 0.5, 0.55), (hoehe * 0.38, 0.4, 0.78),
                                 (hoehe * 0.62, 0.28, 1.0)):
        z.polygon([(x - hoehe * breit / 2, boden - unten), (x + hoehe * breit / 2, boden - unten),
                   (x, boden - hoehe * spitze)], fill=0)


def sonne(z, x, y, r, w=MIN_PUNKTE):
    z.ellipse([x - r * 0.5, y - r * 0.5, x + r * 0.5, y + r * 0.5], outline=0, width=w)
    for i in range(8):
        a = math.radians(i * 45)
        z.line([(x + math.cos(a) * r * 0.68, y + math.sin(a) * r * 0.68),
                (x + math.cos(a) * r, y + math.sin(a) * r)], fill=0, width=w)


def berge(z, b, h, w, schnee=True):
    """Bergkette ueber die ganze Breite, Gipfel mit Schneekappen."""
    boden = h - 1
    n = max(2, round(b / (h * 1.3)))
    breite = b / n
    punkte = [(0, boden - h * 0.25)]
    gipfel = []
    for i in range(n):
        gx = breite * (i + 0.35 + 0.3 * _zufall(i + 7))
        gy = boden - (h - 2) * (0.7 + 0.3 * _zufall(i + 3))
        tal_y = boden - (h - 2) * (0.2 + 0.2 * _zufall(i + 11))
        punkte += [(gx, gy), (breite * (i + 1), tal_y)]
        gipfel.append((gx, gy, punkte[-3], punkte[-1]))
    punkte[-1] = (b - 1, punkte[-1][1])
    zug(z, punkte, w)
    if schnee:
        for gx, gy, links, rechts in gipfel:
            a = (gx + (links[0] - gx) * 0.38, gy + (links[1] - gy) * 0.38)
            c = (gx + (rechts[0] - gx) * 0.38, gy + (rechts[1] - gy) * 0.38)
            mitte_y = max(a[1], c[1])
            z.polygon([a, (gx, gy), c, ((gx + c[0]) / 2, mitte_y - (c[1] - gy) * 0.2),
                       (gx, mitte_y), ((gx + a[0]) / 2, mitte_y - (a[1] - gy) * 0.2)], fill=0)


# --- Linien --------------------------------------------------------------------

def pilze(z, b, h, s):
    g = (h - 2) / 1.55
    for i, x in enumerate(_verteilt(g, b - 1 - g, g * 2.6)):
        pilz(z, x, h - 1, g * (1.0 if i % 3 != 1 else 0.7), fliegenpilz=i % 2 == 0)


def tulpen(z, b, h, s):
    hoch = h - 2
    for x in _verteilt(hoch * 0.4, b - 1 - hoch * 0.4, hoch * 0.9):
        tulpe(z, x, h - 1, hoch, zierstrich(s, hoch / 8))


def gaensebluemchen_reihe(z, b, h, s):
    r = halbhoch(h, s, 4) * 0.95
    m = (h - 1) / 2
    for i, x in enumerate(_verteilt(r, b - 1 - r, r * 2.6)):
        gaensebluemchen(z, x, m, r * (1 if i % 2 == 0 else 0.75))


def lavendel_reihe(z, b, h, s):
    hoch = h - 2
    for i, x in enumerate(_verteilt(hoch * 0.2, b - 1 - hoch * 0.2, hoch * 0.28)):
        lavendel(z, x, h - 1, hoch * (0.8 + 0.2 * _zufall(i)), (_zufall(i + 5) - 0.5) * 0.25)


def kraeuter(z, b, h, s):
    """Rosmarinzweig: Stiel mit feinen Nadeln nach beiden Seiten."""
    hub = halbhoch(h, s, 4)
    m = (h - 1) / 2
    zug(z, [(0, m), (b - 1, m)], zierstrich(s, hub / 3))
    x, i = hub * 0.3, 0
    while x < b - 1 - hub:
        for seite in (-1, 1):
            blatt(z, x + i % 2 * hub * 0.3, m, hub * 1.1, math.radians(seite * 55), 0.11)
        x, i = x + hub * 0.45, i + 1


def blaetter(z, b, h, s):
    hub = halbhoch(h, s, 4)
    m = (h - 1) / 2
    zug(z, [(0, m), (b - 1, m)], zierstrich(s, hub / 3))
    x, oben = hub * 0.2, True
    while x < b - 1 - hub * 1.4:
        ader_blatt(z, x, m, hub * 2.1, math.radians(-30 if oben else 30))
        x, oben = x + hub * 1.5, not oben


def bergkette(z, b, h, s):
    berge(z, b, h, zierstrich(s, h / 8))


def tannen(z, b, h, s):
    hoch = h - 2
    for i, x in enumerate(_verteilt(hoch * 0.3, b - 1 - hoch * 0.3, hoch * 0.45)):
        tanne(z, x, h - 1, hoch * (0.7 + 0.3 * _zufall(i + 2)))


def _verteilt(von, bis, abstand):
    if bis <= von:
        return [(von + bis) / 2]
    n = max(1, round((bis - von) / abstand))
    return [von + i * (bis - von) / n for i in range(n + 1)]


LINIEN = [
    ("pilze", "Pilze", pilze), ("tulpen", "Tulpen", tulpen),
    ("gaensebluemchen", "Gänseblümchen", gaensebluemchen_reihe),
    ("lavendel", "Lavendel", lavendel_reihe), ("kraeuter", "Rosmarinzweig", kraeuter),
    ("blaetter", "Blätter mit Adern", blaetter), ("berge", "Bergkette", bergkette),
    ("tannen", "Tannenwald", tannen),
]
# Szenen auf der Unterkante brauchen mehr Hoehe als Zierlinien.
HOEHE_MM = {"pilze": 5.0, "tulpen": 5.0, "lavendel": 5.0, "berge": 5.0, "tannen": 5.0}
