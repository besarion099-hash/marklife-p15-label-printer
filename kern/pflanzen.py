# -*- coding: utf-8 -*-
"""Pflanzenmotive fuer Rahmen und Linien: Lorbeerzweige, Blueten, Ranken, Gras.

Bausteine: bluete() und zweig() (Blattpaare entlang eines beliebigen Pfads).
Die Rahmen am Ende legen Linienmuster als Baender auf die Kanten.
"""

from __future__ import annotations

import math

from PIL import Image, ImageChops, ImageDraw

from kern.formen import (ECKEN, MIN_PUNKTE, blatt, gespiegelt, halbhoch, ringsum, scheibe,
                         strecke, zierstrich, zug)
from kern.linienzier import ranke


# --- Bausteine -----------------------------------------------------------------

def bluete(z, x, y, r):
    """Fuenfblaettrige Bluete mit hellem Kelch und dunklem Punkt in der Mitte."""
    for i in range(5):
        w = math.radians(-90 + 72 * i)
        blatt(z, x + math.cos(w) * r * 0.15, y + math.sin(w) * r * 0.15, r * 0.85, w, 0.34)
    if r >= 6:
        scheibe(z, x, y, r * 0.32)
        z.ellipse([x - r * 0.2, y - r * 0.2, x + r * 0.2, y + r * 0.2], fill=255)
        scheibe(z, x, y, max(1, r * 0.1))


def _abtasten(pfad, abstand, versatz=0.0):
    """Punkte im Abstand abstand entlang des Pfads: (x, y, winkel, anteil)."""
    laengen = [math.dist(a, b) for a, b in zip(pfad, pfad[1:])]
    gesamt = sum(laengen)
    pos, ergebnis = versatz, []
    while pos <= gesamt and gesamt > 0:
        rest = pos
        for (a, b), lang in zip(zip(pfad, pfad[1:]), laengen):
            if rest <= lang and lang > 0:
                t = rest / lang
                ergebnis.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
                                 math.atan2(b[1] - a[1], b[0] - a[0]), pos / gesamt))
                break
            rest -= lang
        pos += abstand
    return ergebnis


def zweig(z, pfad, blatt_lang, w, spreizung=40, verjuengen=0.35, spitze=True):
    """Lorbeerzweig: Stiel entlang pfad, Blattpaare zeigen in Pfadrichtung."""
    zug(z, pfad, w)
    for x, y, winkel, anteil in _abtasten(pfad, blatt_lang * 0.75, blatt_lang * 0.3)[:-1]:
        lang = blatt_lang * (1 - verjuengen * anteil)
        for seite in (-1, 1):
            blatt(z, x, y, lang, winkel + seite * math.radians(spreizung))
    if spitze and len(pfad) > 1:
        (x0, y0), (x1, y1) = pfad[-2], pfad[-1]
        blatt(z, x1, y1, blatt_lang * (1 - verjuengen), math.atan2(y1 - y0, x1 - x0))


def _zufall(i):
    """Feste Pseudozufallszahl 0..1 (gleiches Bild bei jedem Druck)."""
    return (math.sin(i * 12.9898) * 43758.5453) % 1


# --- Linien --------------------------------------------------------------------

def lorbeer(z, b, h, s):
    hub = halbhoch(h, s, 4)
    m = (h - 1) / 2
    lang = hub * 1.3
    zweig(z, [(0, m), (b - 1 - lang * 0.6, m)], lang, zierstrich(s, hub / 2), verjuengen=0.2)


def zweige_mitte(z, b, h, s):
    """Zwei Zweige laufen von den Enden zu einer Bluete in der Mitte."""
    hub = halbhoch(h, s, 4)
    m, mx = (h - 1) / 2, (b - 1) / 2
    lang, w = hub * 1.2, zierstrich(s, hub / 2)
    zweig(z, [(0, m), (mx - hub * 1.6, m)], lang, w, spitze=False)
    zweig(z, [(b - 1, m), (mx + hub * 1.6, m)], lang, w, spitze=False)
    bluete(z, mx, m, hub)


def blaetter_mitte(z, b, h, s):
    """Linie mit einem Blattzweig in der Mitte: kleine Bluete, je zwei Blaetter
    nach links und rechts."""
    hub = halbhoch(h, s, 4)
    m, mx = (h - 1) / 2, (b - 1) / 2
    mitte = round(m - s / 2)
    rand = hub * 2.6
    strecke(z, (0, mitte), (round(mx - rand), mitte), s)
    strecke(z, (round(mx + rand), mitte), (b - 1, mitte), s)
    for richtung in (-1, 1):
        x = mx + richtung * hub * 0.8
        basis = 0 if richtung > 0 else 180
        for spreiz, lang in ((-24, 1.5), (24, 1.5), (0, 1.9)):
            blatt(z, x, m, hub * lang, math.radians(basis + spreiz), 0.17)
    z.ellipse([mx - hub * 0.75, m - hub * 0.75, mx + hub * 0.75, m + hub * 0.75], fill=255)
    bluete(z, mx, m, hub * 0.7)


def bluetenranke(z, b, h, s):
    hub = halbhoch(h, s, 4)
    w = zierstrich(s, hub / 3)
    m = (h - 1) / 2
    periode = max(6 * hub, 24)
    welle = hub * 0.3
    zug(z, [(x, m + welle * math.sin(2 * math.pi * x / periode)) for x in range(b)], w)
    x, i = periode / 4, 0
    while x < b - hub:
        oben = i % 2 == 1
        y = m + welle * (-1 if oben else 1)
        if i % 2 == 0:
            bluete(z, x, m - welle * 0.2, hub * 0.85)
        else:
            blatt(z, x - hub * 0.4, y, hub * 1.0, math.radians(-40), 0.3)
            blatt(z, x + hub * 0.4, y, hub * 0.8, math.radians(-140), 0.3)
        x, i = x + periode / 2, i + 1


def blumen(z, b, h, s):
    r = halbhoch(h, s, 4) * 0.95
    m = (h - 1) / 2
    x, i = r, 0
    while x <= b - 1 - r:
        if i % 2 == 0:
            bluete(z, x, m, r)
        else:
            blatt(z, x, m, r * 0.8, math.radians(-30), 0.3)
            blatt(z, x, m, r * 0.8, math.radians(150), 0.3)
        x, i = x + r * 1.6, i + 1


def gras(z, b, h, s):
    """Grashalme mit einzelnen Blueten, unten buendig."""
    hoch = h - 2
    w = MIN_PUNKTE
    boden = h - 1
    schritt = max(5, round(hoch / 4))
    for i, x in enumerate(range(1, b - 1, schritt)):
        lang = hoch * (0.45 + 0.4 * _zufall(i))
        neig = (_zufall(i + 99) - 0.5) * hoch * 0.25
        punkte = [(x + neig * t * t, boden - lang * t) for t in (0, 0.25, 0.5, 0.75, 1)]
        zug(z, punkte, w)
        if i % 7 == 3 and x + hoch * 0.3 < b:
            r = hoch * 0.22
            zug(z, [(x, boden), (x + r * 0.2, boden - hoch + r * 1.1)], w)
            bluete(z, x + r * 0.2, boden - hoch + r, r)


# --- Rahmen --------------------------------------------------------------------

def _band(z, b, h, band, linie, s):
    """Linienmuster als Band auf alle vier Kanten legen, die Ecken bleiben frei."""
    bild = z._image                                 # Zeichenflaeche des ImageDraw
    for laenge, ort, drehen in ((b - 2 * band, (band, 0), None),
                                (b - 2 * band, (band, h - band), Image.Transpose.FLIP_TOP_BOTTOM),
                                (h - 2 * band, (0, band), Image.Transpose.ROTATE_270),
                                (h - 2 * band, (b - band, band), Image.Transpose.ROTATE_90)):
        if laenge < band:
            continue
        streifen = Image.new("L", (laenge, band), 255)
        linie(ImageDraw.Draw(streifen), laenge, band, s)
        if drehen is not None:
            streifen = streifen.transpose(drehen)
        kasten = (ort[0], ort[1], ort[0] + streifen.width, ort[1] + streifen.height)
        bild.paste(ImageChops.darker(bild.crop(kasten), streifen), kasten[:2])


def _eckblueten(z, b, h, band):
    for rechts, unten in ECKEN:
        (x, y), = gespiegelt([(band / 2, band / 2)], b, h, rechts, unten)
        bluete(z, x, y, band * 0.48)


def blaetterkante(z, b, h, s, r):
    band = max(6 * s, min(b, h) // 4)
    _band(z, b, h, band, lorbeer, s)
    _eckblueten(z, b, h, band)


def rankenrahmen(z, b, h, s, r):
    band = max(6 * s, min(b, h) // 4)
    _band(z, b, h, band, ranke, s)
    _eckblueten(z, b, h, band)


def lorbeer_ecken(z, b, h, s, r):
    lang = max(3 * s, min(b, h) / 7)
    m = round(lang * 0.9)
    w = zierstrich(s, lang / 2)
    z.rectangle([m, m, b - 1 - m, h - 1 - m], outline=0, width=MIN_PUNKTE)
    for rechts, unten in ECKEN:
        quer = [(m, m), (m + lang * 4, m)]
        hoch = [(m, m), (m, m + min(lang * 2.5, h / 2 - m - lang * 0.5))]
        for pfad in (quer, hoch):
            zweig(z, gespiegelt(pfad, b, h, rechts, unten), lang, w, verjuengen=0.4)


def bluetenecken(z, b, h, s, r):
    rr = max(3 * s, min(b, h) / 6)
    m = round(rr * 0.75)
    for e in (m, m + 3 * MIN_PUNKTE):
        if b - 1 - 2 * e > 0 and h - 1 - 2 * e > 0:
            z.rectangle([e, e, b - 1 - e, h - 1 - e], outline=0, width=MIN_PUNKTE)
    for rechts, unten in ECKEN:
        punkte = gespiegelt([(rr, rr), (rr + rr * 1.1, rr * 0.75), (rr * 0.75, rr + rr * 1.1)],
                            b, h, rechts, unten)
        (x, y), q1, q2 = punkte
        for qx, qy in (q1, q2):
            blatt(z, x, y, math.dist((x, y), (qx, qy)) * 1.3, math.atan2(qy - y, qx - x), 0.3)
        z.ellipse([x - rr * 0.8, y - rr * 0.8, x + rr * 0.8, y + rr * 0.8], fill=255)
        bluete(z, x, y, rr * 0.75)


def kranz(z, b, h, s, r):
    """Ovaler Lorbeerkranz: zwei Zweige von einer Bluete unten bis fast nach oben."""
    lang = max(3 * s, min(b, h) / 8)
    w = zierstrich(s, lang / 2)
    cx, cy = (b - 1) / 2, (h - 1) / 2
    rx, ry = cx - lang * 0.9, cy - lang * 0.9
    def bogen(von, bis):
        n = 60
        return [(cx + rx * math.cos(math.radians(von + (bis - von) * i / n)),
                 cy + ry * math.sin(math.radians(von + (bis - von) * i / n))) for i in range(n + 1)]
    zweig(z, bogen(100, 262), lang, w, verjuengen=0.45)
    zweig(z, bogen(80, -82), lang, w, verjuengen=0.45)
    bluete(z, cx, cy + ry, lang * 0.9)


def wiese(z, b, h, s, r):
    """Feiner Rahmen, unten eine Blumenwiese."""
    z.rectangle([0, 0, b - 1, h - 1], outline=0, width=MIN_PUNKTE)
    hoch = max(6 * s, h // 3)
    streifen = Image.new("L", (b - 4 * MIN_PUNKTE, hoch), 255)
    gras(ImageDraw.Draw(streifen), streifen.width, hoch, s)
    kasten = (2 * MIN_PUNKTE, h - MIN_PUNKTE - hoch)
    bereich = z._image.crop((kasten[0], kasten[1], kasten[0] + streifen.width, kasten[1] + hoch))
    z._image.paste(ImageChops.darker(bereich, streifen), kasten)


def bluetenkette(z, b, h, s, r):
    rr = max(2 * s, min(b, h) / 9)
    for x, y in ringsum(b, h, rr, rr * 2.3):
        bluete(z, x, y, rr)


RAHMEN = [
    ("lorbeer-ecken", "Lorbeer-Ecken", lorbeer_ecken), ("bluetenecken", "Blüten-Ecken", bluetenecken),
    ("kranz", "Lorbeerkranz", kranz), ("blaetterkante", "Blätterkante", blaetterkante),
    ("rankenrahmen", "Rankenrahmen", rankenrahmen), ("wiese", "Blumenwiese", wiese),
    ("bluetenkette", "Blütenkette", bluetenkette),
]
LINIEN = [
    ("lorbeer", "Lorbeerzweig", lorbeer), ("zweige-mitte", "Zweige zur Blüte", zweige_mitte),
    ("blaetter-mitte", "Blätter in der Mitte", blaetter_mitte),
    ("bluetenranke", "Blütenranke", bluetenranke), ("blumen", "Blumenreihe", blumen),
    ("gras", "Gras mit Blumen", gras),
]
