# -*- coding: utf-8 -*-
"""Die Linienformen. Jede Funktion zeichnet waagerecht mittig in eine Flaeche
breite x hoehe (Punkte) mit Strichbreite s. Reihenfolge = Galerie.

Feine Linien kommen mit 1 mm Hoehe aus, Zierlinien brauchen 3 bis 4 mm;
die Galerie setzt beim Einfuegen die passende Hoehe (HOEHE_MM).
"""

from __future__ import annotations

import math

from kern.formen import (MIN_PUNKTE, folge, halbhoch, herz, mittellinie, muster, raute, ring,
                         scheibe, stern, strecke, verteilt, zierstrich, zug)
from kern.linienzier import (_mit_mitte, art_deco, doppelpfeil, drei_punkte, hantel, pfeil,
                             ranke, schnoerkel)


_hub = halbhoch


def _baender(z, b, h, breiten, luecke):
    gesamt = sum(breiten) + luecke * (len(breiten) - 1)
    y = max(0, (h - gesamt) // 2)
    for w in breiten:
        strecke(z, (0, y), (b - 1, y), w)
        y += w + luecke


durchgezogen = mittellinie


def doppelt(z, b, h, s):
    _baender(z, b, h, [s, s], min(2 * s, max(0, (h - 2 * s) // 2)))


def dick_duenn(z, b, h, s):
    _baender(z, b, h, [2 * s, MIN_PUNKTE], s)


def dreifach(z, b, h, s):
    _baender(z, b, h, [s, s, s], s)


def _gemustert(art):
    def zeichnen(z, b, h, s):
        mitte = (h - s) // 2
        muster(z, (0, mitte), (b - 1, mitte), s, folge(art, s))
    return zeichnen


def _reihe(z, b, h, r, abstand, motiv):
    for x in verteilt(r, b - 1 - r, abstand):
        motiv(z, x, (h - 1) / 2, r)


def perlen(z, b, h, s):
    r = _hub(h, s, 1.2)
    _reihe(z, b, h, r, 3 * r, scheibe)


def kreise(z, b, h, s):
    r = _hub(h, s, 2.5)
    w = zierstrich(s, r)
    _reihe(z, b, h, r, 2.6 * r, lambda z_, x, y, rr: ring(z_, x, y, rr, w))


def kette(z, b, h, s):
    r = _hub(h, s, 2)
    w = zierstrich(s, r)
    _reihe(z, b, h, 2 * r, 3.2 * r, lambda z_, x, y, rr: ring(z_, x, y, rr, w, ry=r))


def rauten(z, b, h, s):
    r = _hub(h, s, 2)
    _reihe(z, b, h, 1.6 * r, 3.2 * r, lambda z_, x, y, rr: raute(z_, x, y, rr, r))


def sterne(z, b, h, s):
    r = _hub(h, s, 3)
    _reihe(z, b, h, r, 2.6 * r, stern)


def herzen(z, b, h, s):
    r = _hub(h, s, 3)
    _reihe(z, b, h, r, 2.6 * r, herz)


def _kurve(z, b, h, s, faktor, periode_faktor, form):
    hub = _hub(h, s, faktor)
    periode = max(periode_faktor * s, 16)
    punkte, x = [], 0.0
    while x <= b - 1:
        punkte.append((x, (h - 1) / 2 + form((x / periode) % 1) * hub))
        x += 1
    zug(z, punkte, s)


def welle(z, b, h, s):
    _kurve(z, b, h, s, 3, 16, lambda p: math.sin(2 * math.pi * p))


def zickzack(z, b, h, s):
    _kurve(z, b, h, s, 4, 8, lambda p: 4 * p - 1 if p < 0.5 else 3 - 4 * p)


def saegezahn(z, b, h, s):
    hub = _hub(h, s, 3)
    periode = max(6 * s, 12)
    y0, y1 = (h - 1) / 2 + hub, (h - 1) / 2 - hub
    punkte = [(0, y0)]
    for x in verteilt(periode, b - 1, periode):
        punkte += [(x, y1), (x, y0)]
    zug(z, punkte, s)


def zinnen(z, b, h, s):
    hub = _hub(h, s, 2.5)
    w = zierstrich(s, hub)
    periode = max(4 * hub, 8)
    unten, oben = (h - 1) / 2 + hub, (h - 1) / 2 - hub
    punkte, x, hoch = [(0, unten)], 0.0, False
    while x < b - 1:
        x = min(b - 1, x + periode / 2)
        y = oben if not hoch else unten
        punkte += [(punkte[-1][0], y), (x, y)]
        hoch = not hoch
    zug(z, punkte, w)


def maeander(z, b, h, s):
    """Griechischer Maeander: Haken auf einer durchgehenden Grundlinie."""
    hoehe = min(h - 2, 10 * s)
    u = hoehe / 4
    if u < MIN_PUNKTE:                              # zu flach fuer Haken
        durchgezogen(z, b, h, s)
        return
    w = zierstrich(s, u)
    unten = (h + hoehe) / 2 - w
    def p(x, y):
        return (x, unten - y * u)
    strecke(z, (0, round(unten)), (b - 1, round(unten)), w)
    x = 0.0
    while x + 4 * u <= b - 1:
        zug(z, [p(x, 0), p(x, 4), (x + 4 * u, unten - 4 * u), (x + 4 * u, unten - 1.6 * u),
                (x + 1.6 * u, unten - 1.6 * u), (x + 1.6 * u, unten - 2.6 * u),
                (x + 2.6 * u, unten - 2.6 * u)], w)
        x += 5.4 * u


def boegen(z, b, h, s):
    r = _hub(h, s, 3)
    oben = (h - 1) / 2 - r / 2
    for x in verteilt(0, b - 1 - 2 * r, 2 * r)[:-1] + [b - 1 - 2 * r]:
        z.arc([x, oben - r, x + 2 * r, oben + r], 0, 180, fill=0, width=s)


def kordel(z, b, h, s):
    hub = _hub(h, s, 2.5)
    w = zierstrich(s, hub)
    for x in range(0, round(b - 2 * hub), max(3 * w, 6)):
        z.line([(x, (h - 1) / 2 + hub), (x + 2 * hub, (h - 1) / 2 - hub)], fill=0, width=w)


def schienen(z, b, h, s):
    hub = _hub(h, s, 2.5)
    w = MIN_PUNKTE
    oben, unten = round((h - 1) / 2 - hub), round((h - 1) / 2 + hub - w + 1)
    strecke(z, (0, oben), (b - 1, oben), w)
    strecke(z, (0, unten), (b - 1, unten), w)
    for x in verteilt(0, b - 1 - w, 3 * w + 2):
        strecke(z, (round(x), oben), (round(x), unten), w)


def schwellstrich(z, b, h, s):
    """Kalligrafischer Strich: in der Mitte dick, zu den Enden spitz."""
    dicke = _hub(h, s, 1.5)
    m = (h - 1) / 2
    oben = [(x, m - dicke * math.sin(math.pi * x / (b - 1))) for x in range(0, b, 2)]
    unten = [(x, 2 * m - y) for x, y in oben]
    z.polygon(oben + unten[::-1], fill=0)
    durchgezogen(z, b, h, MIN_PUNKTE)


FORMEN = [
    ("durchgezogen", "durchgezogen", durchgezogen), ("doppelt", "doppelt", doppelt),
    ("dick-duenn", "dick-dünn", dick_duenn), ("dreifach", "dreifach", dreifach),
    ("gestrichelt", "gestrichelt", _gemustert("gestrichelt")),
    ("lang-gestrichelt", "lang gestrichelt", _gemustert("lang-gestrichelt")),
    ("gepunktet", "gepunktet", _gemustert("gepunktet")),
    ("strich-punkt", "Strich-Punkt", _gemustert("strich-punkt")),
    ("strich-punkt-punkt", "Strich-Punkt-Punkt", _gemustert("strich-punkt-punkt")),
    ("perlen", "Perlen", perlen), ("kreise", "Kreise", kreise), ("kette", "Kette", kette),
    ("rauten", "Rauten", rauten), ("sterne", "Sterne", sterne), ("herzen", "Herzen", herzen),
    ("welle", "Welle", welle), ("zickzack", "Zickzack", zickzack),
    ("saegezahn", "Sägezahn", saegezahn), ("zinnen", "Zinnen", zinnen),
    ("maeander", "Mäander", maeander), ("boegen", "Bögen", boegen), ("kordel", "Kordel", kordel),
    ("schienen", "Schienen", schienen), ("schwellstrich", "Schwellstrich", schwellstrich),
    ("ornament", "Raute in der Mitte", _mit_mitte(lambda z, x, y, r, s: raute(z, x, y, r))),
    ("kreis-mitte", "Kreis in der Mitte",
     _mit_mitte(lambda z, x, y, r, s: ring(z, x, y, r, zierstrich(s, r)))),
    ("herz-mitte", "Herz in der Mitte", _mit_mitte(lambda z, x, y, r, s: herz(z, x, y, r))),
    ("stern-mitte", "Stern in der Mitte", _mit_mitte(lambda z, x, y, r, s: stern(z, x, y, r))),
    ("drei-punkte", "drei Punkte", drei_punkte), ("hantel", "Punkte an den Enden", hantel),
    ("pfeil", "Pfeil", pfeil), ("doppelpfeil", "Doppelpfeil", doppelpfeil),
    ("schnoerkel", "Schnörkel", schnoerkel), ("ranke", "Blattranke", ranke),
    ("art-deco", "Art déco", art_deco),
]

# Hoehe beim Einfuegen: einfache Linien 1 mm, mehrfache 2 mm, Zierlinien 3 mm.
FEIN = {"durchgezogen", "gestrichelt", "lang-gestrichelt", "gepunktet", "strich-punkt",
        "strich-punkt-punkt"}
MITTEL = {"doppelt", "dick-duenn", "dreifach"}
GROSS = {"schnoerkel", "ranke", "art-deco"}
HOEHE_MM = {name: 1.0 if name in FEIN else 2.0 if name in MITTEL else 4.0 if name in GROSS
            else 3.0 for name, _, _ in FORMEN}
