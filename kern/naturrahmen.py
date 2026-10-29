# -*- coding: utf-8 -*-
"""Naturrahmen: Szenen auf der Unterkante (Berge, Pilze, Tulpen, Tannen),
Baender aus Kraeutern und Blaettern, Lavendel und Gaensebluemchen in den Ecken."""

from __future__ import annotations

from PIL import Image, ImageChops, ImageDraw

from kern import natur
from kern.formen import ECKEN, MIN_PUNKTE, gespiegelt
from kern.pflanzen import _band


def _unten(z, b, h, s, linie, anteil):
    """Feiner Rahmen, unten innen eine Szene aus dem Linienmuster linie."""
    z.rectangle([0, 0, b - 1, h - 1], outline=0, width=MIN_PUNKTE)
    hoch = max(6 * s, round(h * anteil))
    breit = b - 4 * MIN_PUNKTE
    if breit < 1 or hoch >= h - 2 * MIN_PUNKTE:
        return
    streifen = Image.new("L", (breit, hoch), 255)
    linie(ImageDraw.Draw(streifen), breit, hoch, s)
    ort = (2 * MIN_PUNKTE, h - MIN_PUNKTE - hoch)
    bereich = z._image.crop((ort[0], ort[1], ort[0] + breit, ort[1] + hoch))
    z._image.paste(ImageChops.darker(bereich, streifen), ort)


def bergpanorama(z, b, h, s, r):
    _unten(z, b, h, s, natur.bergkette, 0.5)
    rr = max(3 * s, h / 7)
    natur.sonne(z, b - 1 - rr * 1.6, rr * 1.4, rr)


def pilzrahmen(z, b, h, s, r):
    _unten(z, b, h, s, natur.pilze, 0.38)


def tulpenbeet(z, b, h, s, r):
    _unten(z, b, h, s, natur.tulpen, 0.45)


def tannenrahmen(z, b, h, s, r):
    _unten(z, b, h, s, natur.tannen, 0.5)


def _eck_gaensebluemchen(z, b, h, band):
    for rechts, unten in ECKEN:
        (x, y), = gespiegelt([(band / 2, band / 2)], b, h, rechts, unten)
        natur.gaensebluemchen(z, x, y, band * 0.5)


def kraeuterrahmen(z, b, h, s, r):
    band = max(6 * s, min(b, h) // 4)
    _band(z, b, h, band, natur.kraeuter, s)
    _eck_gaensebluemchen(z, b, h, band)


def blaetterrahmen(z, b, h, s, r):
    band = max(6 * s, min(b, h) // 4)
    _band(z, b, h, band, natur.blaetter, s)
    _eck_gaensebluemchen(z, b, h, band)


def lavendel_ecken(z, b, h, s, r):
    """Feiner Rahmen, in den unteren Ecken je ein Lavendelstrauss."""
    m = max(2 * MIN_PUNKTE, round(h / 16))
    z.rectangle([m, m, b - 1 - m, h - 1 - m], outline=0, width=MIN_PUNKTE)
    hoch = h - 2 * m - 2
    for rechts in (False, True):
        for k, neigung in enumerate((-0.1, 0.02, 0.14)):
            fuss = m * 2.5 + k * 3 * MIN_PUNKTE
            fuss = (b - 1 - fuss) if rechts else fuss
            natur.lavendel(z, fuss, h - 1 - m, hoch * (0.95 - 0.1 * abs(k - 1)),
                           -neigung if rechts else neigung)


def gaensebluemchen_ecken(z, b, h, s, r):
    rr = max(3 * s, min(b, h) / 5)
    m = round(rr * 0.6)
    for e in (m, m + 3 * MIN_PUNKTE):
        if b - 1 - 2 * e > 0 and h - 1 - 2 * e > 0:
            z.rectangle([e, e, b - 1 - e, h - 1 - e], outline=0, width=MIN_PUNKTE)
    for rechts, unten in ECKEN:
        (x, y), = gespiegelt([(rr * 0.75, rr * 0.75)], b, h, rechts, unten)
        z.ellipse([x - rr * 0.8, y - rr * 0.8, x + rr * 0.8, y + rr * 0.8], fill=255)
        natur.gaensebluemchen(z, x, y, rr * 0.75)


RAHMEN = [
    ("bergpanorama", "Bergpanorama", bergpanorama), ("tannenrahmen", "Tannenwald", tannenrahmen),
    ("pilzrahmen", "Pilze", pilzrahmen), ("tulpenbeet", "Tulpenbeet", tulpenbeet),
    ("lavendel-ecken", "Lavendel", lavendel_ecken),
    ("gaensebluemchen-ecken", "Gänseblümchen-Ecken", gaensebluemchen_ecken),
    ("kraeuterrahmen", "Kräuterrahmen", kraeuterrahmen),
    ("blaetterrahmen", "Blätterrahmen", blaetterrahmen),
]
